"""
Configuration file for SMARTWATT NEXUS
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smartwatt-nexus-secret-key-2026'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///smartwatt_nexus.db'
    
    # ML Models
    LSTM_EPOCHS = 50
    LSTM_BATCH_SIZE = 16
    LSTM_LOOKBACK = 7
    
    ANN_EPOCHS = 100
    ANN_BATCH_SIZE = 16
    
    # TS Electric Department Rates
    TARIFF_SLABS = [
        {'from': 0, 'to': 50, 'rate': 2.80},
        {'from': 50, 'to': 100, 'rate': 3.40},
        {'from': 100, 'to': 200, 'rate': 4.60},
        {'from': 200, 'to': 500, 'rate': 6.00},
        {'from': 500, 'to': float('inf'), 'rate': 7.50}
    ]
    
    FIXED_CHARGE = 100  # Monthly fixed charge in INR
    TAX_RATE = 0.10  # 10% tax
    
    # Alert Configuration
    HIGH_CONSUMPTION_THRESHOLD = 1.3  # 30% above average
    ANOMALY_SENSITIVITY = 1.5  # Standard deviations
    
    # API Configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Pagination
    ITEMS_PER_PAGE = 50

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
