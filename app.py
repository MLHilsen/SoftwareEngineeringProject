from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
from functools import wraps
import mysql.connector
from mysql.connector import Error

from config import Config
from models import db, User, Pet, Application, Appointment, MedicalRecord, Adoption, Favorite, BlogPost, Event, Notification, CareLog

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def utility_processor():
    def get_unread_count():
        if current_user.is_authenticated:
            return Notification.query.filter_by(user_id=current_user.user_id, is_read=False).count()
        return 0
    return {'now': datetime.utcnow(), 'unread_count': get_unread_count()}

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def notify(user_id, message, link=None):
    n = Notification(user_id=user_id, message=message, link=link)
    db.session.add(n)

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    pets = Pet.query.filter_by(status='available').order_by(Pet.created_at.desc()).limit(6).all()
    events = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date).limit(3).all()
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    return render_template('index.html', pets=pets, events=events, posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        if not full_name or not email or not password:
            flash('Full name, email, and password are required.', 'danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))
        new_user = User(full_name=full_name, email=email, phone=phone, address=address, role='user', is_active=True)
        new_user.set_password(password)
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            new_user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Registration successful! Welcome!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
        if not user.is_active:
            flash('Your account has been deactivated.', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()
        flash(f'Welcome back, {user.full_name}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# ── Dashboard / Profile ───────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    my_apps = Application.query.filter_by(user_id=current_user.user_id).order_by(Application.submitted_at.desc()).limit(5).all()
    my_appts = Appointment.query.filter_by(user_id=current_user.user_id, status='scheduled').order_by(Appointment.appointment_date).limit(5).all()
    my_favs = Favorite.query.filter_by(user_id=current_user.user_id).limit(4).all()
    notifications = Notification.query.filter_by(user_id=current_user.user_id).order_by(Notification.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', user=current_user, my_apps=my_apps, my_appts=my_appts, my_favs=my_favs, notifications=notifications)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    email = request.form.get('email')
    if email != current_user.email and User.query.filter_by(email=email).first():
        flash('Email already in use.', 'danger')
        return redirect(url_for('profile'))
    current_user.full_name = request.form.get('full_name')
    current_user.phone = request.form.get('phone')
    current_user.address = request.form.get('address')
    current_user.email = email
    current_user.updated_at = datetime.utcnow()
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    if not current_user.check_password(request.form.get('current_password')):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile'))
    new_password = request.form.get('new_password')
    if new_password != request.form.get('confirm_password'):
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('profile'))
    if len(new_password) < 6:
        flash('Password must be at least 6 characters.', 'danger')
        return redirect(url_for('profile'))
    current_user.set_password(new_password)
    current_user.updated_at = datetime.utcnow()
    db.session.commit()
    flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))

# ── Pets / Listings ───────────────────────────────────────────────────────────

@app.route('/listings')
@login_required
def listings():
    species = request.args.get('species', '')
    size = request.args.get('size', '')
    status = request.args.get('status', 'available')
    q = request.args.get('q', '')
    query = Pet.query
    if species:
        query = query.filter(Pet.species.ilike(f'%{species}%'))
    if size:
        query = query.filter_by(size=size)
    if status:
        query = query.filter_by(status=status)
    if q:
        query = query.filter(Pet.name.ilike(f'%{q}%') | Pet.breed.ilike(f'%{q}%'))
    pets = query.order_by(Pet.created_at.desc()).all()
    fav_ids = {f.pet_id for f in Favorite.query.filter_by(user_id=current_user.user_id).all()}
    return render_template('listings.html', pets=pets, fav_ids=fav_ids)

@app.route('/pet/<int:pet_id>')
@login_required
def pet_detail(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    records = MedicalRecord.query.filter_by(pet_id=pet_id).order_by(MedicalRecord.record_date.desc()).all()
    history = Adoption.query.filter_by(pet_id=pet_id).order_by(Adoption.adoption_date.desc()).all()
    is_fav = Favorite.query.filter_by(user_id=current_user.user_id, pet_id=pet_id).first() is not None
    appts = Appointment.query.filter_by(pet_id=pet_id, status='scheduled').order_by(Appointment.appointment_date).all()
    active_care = CareLog.query.filter_by(pet_id=pet_id, clocked_out=None).all()
    return render_template('pet_detail.html', pet=pet, records=records, history=history, is_fav=is_fav, appts=appts, active_care=active_care)

@app.route('/pet/compare')
@login_required
def compare_pets():
    ids = request.args.getlist('ids')
    pets = []
    if ids:
        pets = Pet.query.filter(Pet.pet_id.in_([int(i) for i in ids[:3]])).all()
    all_pets = Pet.query.filter_by(status='available').order_by(Pet.name).all()
    return render_template('compare.html', pets=pets, all_pets=all_pets)

# ── Favorites ─────────────────────────────────────────────────────────────────

@app.route('/favorites')
@login_required
def favorites():
    favs = Favorite.query.filter_by(user_id=current_user.user_id).all()
    return render_template('favorites.html', favs=favs)

@app.route('/favorites/toggle/<int:pet_id>', methods=['POST'])
@login_required
def toggle_favorite(pet_id):
    fav = Favorite.query.filter_by(user_id=current_user.user_id, pet_id=pet_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'status': 'removed'})
    else:
        db.session.add(Favorite(user_id=current_user.user_id, pet_id=pet_id))
        db.session.commit()
        return jsonify({'status': 'added'})

# ── Applications ──────────────────────────────────────────────────────────────

@app.route('/apply/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def apply(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if request.method == 'POST':
        app_type = request.form.get('application_type', 'adoption')
        existing = Application.query.filter_by(user_id=current_user.user_id, pet_id=pet_id, status='pending').first()
        if existing:
            flash('You already have a pending application for this pet.', 'warning')
            return redirect(url_for('pet_detail', pet_id=pet_id))
        application = Application(
            user_id=current_user.user_id,
            pet_id=pet_id,
            application_type=app_type,
            reason=request.form.get('reason'),
            housing=request.form.get('housing'),
            has_yard=bool(request.form.get('has_yard')),
            has_other_pets=bool(request.form.get('has_other_pets')),
            other_pets_desc=request.form.get('other_pets_desc'),
            household_mem=int(request.form.get('household_mem', 1)),
            pet_experience=request.form.get('pet_experience'),
            vet_name=request.form.get('vet_name'),
            vet_phone=request.form.get('vet_phone'),
            reference1_name=request.form.get('reference1_name'),
            reference1_phone=request.form.get('reference1_phone'),
            reference2_name=request.form.get('reference2_name'),
            reference2_phone=request.form.get('reference2_phone'),
        )
        db.session.add(application)
        db.session.commit()
        flash(f'Your {app_type} application for {pet.name} has been submitted!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('apply.html', pet=pet)

# ── Appointments ──────────────────────────────────────────────────────────────

@app.route('/appointments')
@login_required
def appointments():
    if current_user.is_admin():
        appts = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    else:
        appts = Appointment.query.filter_by(user_id=current_user.user_id).order_by(Appointment.appointment_date.desc()).all()
    pets = Pet.query.order_by(Pet.name).all()
    return render_template('appointments.html', appts=appts, pets=pets)

@app.route('/appointments/new', methods=['POST'])
@login_required
def new_appointment():
    pet_id = int(request.form.get('pet_id'))
    pet = Pet.query.get_or_404(pet_id)
    appt = Appointment(
        pet_id=pet_id,
        user_id=current_user.user_id,
        service_type=request.form.get('service_type'),
        appointment_date=datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%dT%H:%M'),
        duration_min=int(request.form.get('duration_min', 30)),
        notes=request.form.get('notes'),
        vet_name=request.form.get('vet_name'),
        cost=float(request.form.get('cost', 0)),
        created_by=current_user.user_id,
    )
    db.session.add(appt)
    db.session.commit()
    notify(current_user.user_id, f'Appointment scheduled for {pet.name} on {appt.appointment_date.strftime("%b %d")}', url_for('appointments'))
    db.session.commit()
    flash('Appointment scheduled!', 'success')
    return redirect(url_for('appointments'))

@app.route('/appointments/<int:appt_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    appt.status = 'cancelled'
    appt.cancellation_reason = request.form.get('reason', '')
    db.session.commit()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('appointments'))

# ── Care Tracker ──────────────────────────────────────────────────────────────

@app.route('/care-tracker')
@login_required
def care_tracker():
    active = CareLog.query.filter_by(clocked_out=None).all()
    my_log = CareLog.query.filter_by(user_id=current_user.user_id).order_by(CareLog.clocked_in.desc()).limit(10).all()
    pets = Pet.query.filter_by(status='available').order_by(Pet.name).all()
    my_active = CareLog.query.filter_by(user_id=current_user.user_id, clocked_out=None).first()
    return render_template('care_tracker.html', active=active, my_log=my_log, pets=pets, my_active=my_active)

@app.route('/care-tracker/clock-in', methods=['POST'])
@login_required
def clock_in():
    existing = CareLog.query.filter_by(user_id=current_user.user_id, clocked_out=None).first()
    if existing:
        flash('You are already clocked in. Clock out first.', 'warning')
        return redirect(url_for('care_tracker'))
    log = CareLog(pet_id=int(request.form.get('pet_id')), user_id=current_user.user_id, notes=request.form.get('notes'))
    db.session.add(log)
    db.session.commit()
    flash('Clocked in successfully!', 'success')
    return redirect(url_for('care_tracker'))

@app.route('/care-tracker/clock-out', methods=['POST'])
@login_required
def clock_out():
    log = CareLog.query.filter_by(user_id=current_user.user_id, clocked_out=None).first()
    if log:
        log.clocked_out = datetime.utcnow()
        log.notes = request.form.get('notes', log.notes)
        db.session.commit()
        flash('Clocked out successfully!', 'success')
    return redirect(url_for('care_tracker'))

# ── Blog ──────────────────────────────────────────────────────────────────────

@app.route('/blog')
def blog():
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('blog_post.html', post=post)

@app.route('/blog/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_blog_post():
    if request.method == 'POST':
        post = BlogPost(
            title=request.form.get('title'),
            content=request.form.get('content'),
            author_id=current_user.user_id,
            published=bool(request.form.get('published'))
        )
        db.session.add(post)
        db.session.commit()
        flash('Post published!', 'success')
        return redirect(url_for('blog'))
    return render_template('blog_form.html')

# ── Events ────────────────────────────────────────────────────────────────────

@app.route('/events')
def events():
    upcoming = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date).all()
    past = Event.query.filter(Event.event_date < datetime.utcnow()).order_by(Event.event_date.desc()).limit(5).all()
    return render_template('events.html', upcoming=upcoming, past=past)

@app.route('/events/new', methods=['POST'])
@login_required
@admin_required
def new_event():
    event = Event(
        title=request.form.get('title'),
        description=request.form.get('description'),
        event_date=datetime.strptime(request.form.get('event_date'), '%Y-%m-%dT%H:%M'),
        location=request.form.get('location'),
        created_by=current_user.user_id,
    )
    db.session.add(event)
    db.session.commit()
    flash('Event created!', 'success')
    return redirect(url_for('events'))

# ── Notifications ─────────────────────────────────────────────────────────────

@app.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.user_id).order_by(Notification.created_at.desc()).all()
    Notification.query.filter_by(user_id=current_user.user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('notifications.html', notifs=notifs)

@app.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'status': 'ok'})

# ── Careers ───────────────────────────────────────────────────────────────────

@app.route('/careers')
def careers():
    return render_template('careers.html')

# ── Store ─────────────────────────────────────────────────────────────────────

@app.route('/store')
def store():
    return render_template('store.html')

# ── Donate ────────────────────────────────────────────────────────────────────

@app.route('/donate')
def donate():
    return render_template('donate.html')

# ── Admin ─────────────────────────────────────────────────────────────────────

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    pets = Pet.query.order_by(Pet.created_at.desc()).all()
    applications = Application.query.order_by(Application.submitted_at.desc()).all()
    return render_template('admin.html', users=users, pets=pets, applications=applications)

@app.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.user_id == current_user.user_id:
        flash('You cannot modify your own account.', 'danger')
    else:
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'User {user.full_name} {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/user/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.user_id != current_user.user_id:
        new_role = request.form.get('role')
        if new_role in ['user', 'admin']:
            user.role = new_role
            user.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'{user.full_name} is now a {new_role}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/pet/new', methods=['POST'])
@login_required
@admin_required
def admin_new_pet():
    pet = Pet(
        name=request.form.get('name'),
        species=request.form.get('species'),
        breed=request.form.get('breed'),
        age=int(request.form.get('age', 0)),
        gender=request.form.get('gender', 'unknown'),
        size=request.form.get('size'),
        color=request.form.get('color'),
        description=request.form.get('description'),
        status=request.form.get('status', 'available'),
        temperament=request.form.get('temperament'),
        special_needs=request.form.get('special_needs'),
        adoption_fee=float(request.form.get('adoption_fee', 0)),
        image=request.form.get('image'),
    )
    db.session.add(pet)
    db.session.commit()
    flash(f'{pet.name} added!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/pet/<int:pet_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    pet.name = request.form.get('name')
    pet.species = request.form.get('species')
    pet.breed = request.form.get('breed')
    pet.age = int(request.form.get('age', pet.age))
    pet.gender = request.form.get('gender', pet.gender)
    pet.size = request.form.get('size', pet.size)
    pet.color = request.form.get('color')
    pet.description = request.form.get('description')
    pet.status = request.form.get('status', pet.status)
    pet.temperament = request.form.get('temperament')
    pet.special_needs = request.form.get('special_needs')
    pet.adoption_fee = float(request.form.get('adoption_fee', 0))
    pet.image = request.form.get('image')
    pet.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f'{pet.name} updated!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/application/<int:app_id>/review', methods=['POST'])
@login_required
@admin_required
def review_application(app_id):
    application = Application.query.get_or_404(app_id)
    new_status = request.form.get('status')
    application.status = new_status
    application.admin_notes = request.form.get('admin_notes', '')
    application.reviewed_by = current_user.user_id
    application.updated_at = datetime.utcnow()
    if new_status == 'approved':
        application.pet.status = 'adopted' if application.application_type == 'adoption' else 'fostered'
        adoption = Adoption(
            application_id=app_id,
            user_id=application.user_id,
            pet_id=application.pet_id,
            adoption_date=datetime.utcnow().date(),
            adoption_fee_paid=application.pet.adoption_fee,
        )
        db.session.add(adoption)
        notify(application.user_id, f'Your {application.application_type} application for {application.pet.name} was approved! 🎉', url_for('dashboard'))
    elif new_status == 'rejected':
        notify(application.user_id, f'Your application for {application.pet.name} was not approved. Please contact us for more info.', url_for('dashboard'))
    db.session.commit()
    flash(f'Application {new_status}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/medical-record/new', methods=['POST'])
@login_required
@admin_required
def new_medical_record():
    record = MedicalRecord(
        pet_id=int(request.form.get('pet_id')),
        record_type=request.form.get('record_type'),
        record_date=datetime.strptime(request.form.get('record_date'), '%Y-%m-%d').date(),
        vet_name=request.form.get('vet_name'),
        diagnosis=request.form.get('diagnosis'),
        treatment=request.form.get('treatment'),
        medications=request.form.get('medications'),
        cost=float(request.form.get('cost', 0)),
        next_appt_date=datetime.strptime(request.form.get('next_appt_date'), '%Y-%m-%d').date() if request.form.get('next_appt_date') else None,
        notes=request.form.get('notes'),
        created_by=current_user.user_id,
    )
    db.session.add(record)
    db.session.commit()
    flash('Medical record added!', 'success')
    return redirect(url_for('pet_detail', pet_id=record.pet_id))

@app.route('/health')
def health_check():
    try:
        user_count = User.query.count()
        db_status = f'connected ({user_count} users)'
    except:
        db_status = 'disconnected'
    return {'status': 'healthy', 'database': db_status, 'timestamp': datetime.utcnow().isoformat()}

@app.cli.command("init-db")
def init_db():
    db.create_all()
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(full_name='System Administrator', email='admin@example.com', phone='', address='', role='admin', is_active=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin created')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
