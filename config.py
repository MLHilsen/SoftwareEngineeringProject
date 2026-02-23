import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    
    # Update with your working credentials
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://main:plz123emt@34.71.146.71:3306/ProjectDatabase'
    
    # Alternative formats if the above doesn't work:
    # SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://main:plz123emt@34.71.146.71:3306/ProjectDatabase'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }