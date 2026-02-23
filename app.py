from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps
import mysql.connector
from mysql.connector import Error

from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
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
    return {'now': datetime.utcnow()}

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Database connection test function
def test_db_connection():
    """Test direct MySQL connection on startup"""
    try:
        connection = mysql.connector.connect(
            host='34.71.146.71',
            user='main',
            password='plz123emt',
            database='ProjectDatabase',
            port=3306
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print("=" * 50)
            print("✅ DATABASE CONNECTION SUCCESSFUL")
            print("=" * 50)
            print(f"Connected to MySQL Server version: {db_info}")
            
            cursor = connection.cursor()
            
            # Get database name
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"Connected to database: {db_name[0]}")
            
            # Show all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                print(f"\nTables in database:")
                for table in tables:
                    # Get row count for each table
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"  - {table[0]}: {count} rows")
            else:
                print("\nNo tables found in database.")
            
            cursor.close()
            connection.close()
            print("\n" + "=" * 50)
            return True
            
    except Error as e:
        print("=" * 50)
        print("❌ DATABASE CONNECTION FAILED")
        print("=" * 50)
        print(f"Error: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

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
        
        # Validation
        if not full_name or not email or not password:
            flash('Full name, email, and password are required.', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))
        
        # Create new user (note: no username field, using full_name and email)
        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            role='user',  # Default role
            is_active=True
        )
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Auto login after registration
            login_user(new_user)
            
            # Update last login
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
        email = request.form.get('email')  # Using email instead of username
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            return redirect(url_for('login'))
        
        # Login user
        login_user(user, remember=remember)
        
        # Update last login
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

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    return render_template('admin.html', users=users, sessions=[])

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
        status = "deactivated" if not user.is_active else "activated"
        flash(f'User {user.full_name} has been {status}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/user/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.user_id == current_user.user_id:
        flash('You cannot change your own role.', 'danger')
    else:
        new_role = request.form.get('role')
        if new_role in ['user', 'admin']:
            user.role = new_role
            user.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'{user.full_name} is now a {new_role}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    full_name = request.form.get('full_name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    email = request.form.get('email')
    
    # Check if email is already taken by another user
    if email != current_user.email:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use by another account.', 'danger')
            return redirect(url_for('profile'))
    
    current_user.full_name = full_name
    current_user.phone = phone
    current_user.address = address
    current_user.email = email
    current_user.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('profile'))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long.', 'danger')
        return redirect(url_for('profile'))
    
    current_user.set_password(new_password)
    current_user.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))

# Create tables CLI command (if tables don't exist)
@app.cli.command("init-db")
def init_db():
    """Initialize the database with tables if they don't exist."""
    print("Creating database tables if they don't exist...")
    db.create_all()
    
    # Check if admin exists
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            full_name='System Administrator',
            email='admin@example.com',
            phone='',
            address='',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')  # Change this in production!
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created (email: admin@example.com, password: admin123)')
    else:
        print('✅ Admin user already exists')
    
    # Create a test user
    test_user = User.query.filter_by(email='test@example.com').first()
    if not test_user:
        test_user = User(
            full_name='Test User',
            email='test@example.com',
            phone='123-456-7890',
            address='123 Test St',
            role='user',
            is_active=True
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        db.session.commit()
        print('✅ Test user created (email: test@example.com, password: test123)')
    
    print("=" * 50)
    print("Database initialization complete!")
    print("=" * 50)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Try a simple query to verify database is working
        user_count = User.query.count()
        db_status = f'connected ({user_count} users)'
    except:
        db_status = 'disconnected'
    
    status = {
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }
    return status

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("STARTING USER MANAGEMENT APPLICATION")
    print("=" * 50)
    
    # Test database connection before starting
    if test_db_connection():
        print("\n🚀 Starting Flask application...")
        print("📱 Access the app at: http://localhost:5000")
        print("🔑 Default admin: admin@example.com / admin123")
        print("🔑 Default test user: test@example.com / test123")
        print("=" * 50 + "\n")
        
        # Run the app
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("\n❌ Failed to connect to database. Please check your connection settings.")
        print("=" * 50 + "\n")