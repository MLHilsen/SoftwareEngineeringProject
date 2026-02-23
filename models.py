from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    # Matching your exact table structure
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
    
    # Flask-Login requires an 'id' attribute, so we'll create a property
    @property
    def id(self):
        """Return user_id as id for Flask-Login compatibility"""
        return self.user_id
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def update_last_login(self):
        """Update last_login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.email}>'