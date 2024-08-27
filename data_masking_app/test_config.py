import os

class Config:
    """Base config."""
    TESTING = True
    DEBUG = False
    SECRET_KEY = 'your_secret_key'
    UPLOAD_FOLDER = 'uploads/'

# You can add more configuration if needed