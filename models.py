from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'admin'), nullable=False, default='user')
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    last_login = db.Column(db.TIMESTAMP, nullable=True)
    applications = db.relationship('Application', foreign_keys='Application.user_id', backref='applicant', lazy=True)
    appointments = db.relationship('Appointment', foreign_keys='Appointment.user_id', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

    @property
    def id(self):
        return self.user_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email}>'


class Pet(db.Model):
    __tablename__ = 'pets'
    pet_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'unknown'), nullable=False, default='unknown')
    size = db.Column(db.Enum('small', 'medium', 'large'), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('available', 'adopted', 'fostered'), nullable=True)
    medical_hist = db.Column(db.Text, nullable=True)
    temperament = db.Column(db.String(255), nullable=True)
    special_needs = db.Column(db.Text, nullable=True)
    adoption_fee = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    adopted_date = db.Column(db.TIMESTAMP, nullable=True)
    applications = db.relationship('Application', backref='pet', lazy=True)
    appointments = db.relationship('Appointment', backref='pet', lazy=True)
    medical_records = db.relationship('MedicalRecord', backref='pet', lazy=True)
    adoptions = db.relationship('Adoption', backref='pet', lazy=True)
    favorites = db.relationship('Favorite', backref='pet', lazy=True)

    def __repr__(self):
        return f'<Pet {self.name}>'


class Application(db.Model):
    __tablename__ = 'applications'
    application_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'), nullable=False)
    application_type = db.Column(db.Enum('adoption', 'foster'), nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'withdrawn'), nullable=False, default='pending')
    reason = db.Column(db.Text, nullable=True)
    housing = db.Column(db.Enum('house', 'apartment', 'condo', 'other'), nullable=True)
    has_yard = db.Column(db.Boolean, nullable=True, default=False)
    has_other_pets = db.Column(db.Boolean, nullable=True, default=False)
    other_pets_desc = db.Column(db.Text, nullable=True)
    household_mem = db.Column(db.Integer, nullable=True, default=1)
    pet_experience = db.Column(db.Text, nullable=True)
    vet_name = db.Column(db.String(100), nullable=True)
    vet_phone = db.Column(db.String(20), nullable=True)
    reference1_name = db.Column(db.String(100), nullable=True)
    reference1_phone = db.Column(db.String(100), nullable=True)
    reference2_name = db.Column(db.String(100), nullable=True)
    reference2_phone = db.Column(db.String(100), nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    submitted_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_applications')

    def __repr__(self):
        return f'<Application {self.application_id}>'


class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    service_type = db.Column(db.Enum('vaccination', 'grooming', 'checkup', 'surgery', 'other'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration_min = db.Column(db.Integer, nullable=True, default=30)
    status = db.Column(db.Enum('scheduled', 'completed', 'cancelled'), nullable=False, default='scheduled')
    notes = db.Column(db.Text, nullable=True)
    cost = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    vet_name = db.Column(db.String(100), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    cancellation_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=True, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment {self.appointment_id}>'


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'), nullable=False)
    record_type = db.Column(db.Enum('vaccination', 'checkup', 'surgery', 'treatment', 'other'), nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    vet_name = db.Column(db.String(100), nullable=True)
    diagnosis = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    medications = db.Column(db.Text, nullable=True)
    cost = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    next_appt_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)

    def __repr__(self):
        return f'<MedicalRecord {self.record_id}>'


class Adoption(db.Model):
    __tablename__ = 'adoptions'
    adoption_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.application_id'), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'), nullable=False)
    adoption_date = db.Column(db.Date, nullable=False)
    adoption_fee_paid = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    contract_signed = db.Column(db.Boolean, nullable=True, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    adopter = db.relationship('User', backref='adoptions')
    application = db.relationship('Application', backref='adoption')

    def __repr__(self):
        return f'<Adoption {self.adoption_id}>'


class Favorite(db.Model):
    __tablename__ = 'favorites'
    favorite_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'pet_id', name='uq_user_pet_favorite'),)


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    author = db.relationship('User', backref='blog_posts')


class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    creator = db.relationship('User', backref='events')


class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', backref='notifications')


class CareLog(db.Model):
    __tablename__ = 'care_logs'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    clocked_in = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    clocked_out = db.Column(db.TIMESTAMP, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    worker = db.relationship('User', backref='care_logs')
    care_pet = db.relationship('Pet', backref='care_logs')
