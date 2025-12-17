from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from cryptography.fernet import Fernet
import os

db = SQLAlchemy()

# Encryption key (should be in env or generated once)
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_value(value):
    """Encrypt sensitive data"""
    if not value:
        return None
    return cipher.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value):
    """Decrypt sensitive data"""
    if not encrypted_value:
        return None
    return cipher.decrypt(encrypted_value.encode()).decode()

class Settings(db.Model):
    """Singleton model for application settings"""
    id = db.Column(db.Integer, primary_key=True, default=1)
    gemini_api_key_encrypted = db.Column(db.Text)
    github_webhook_secret = db.Column(db.String(200))
    setup_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def gemini_api_key(self):
        return decrypt_value(self.gemini_api_key_encrypted)
    
    @gemini_api_key.setter
    def gemini_api_key(self, value):
        self.gemini_api_key_encrypted = encrypt_value(value)

    def to_dict(self, mask_sensitive=True):
        return {
            "setup_completed": self.setup_completed,
            "gemini_api_key": "***" + (self.gemini_api_key[-4:] if self.gemini_api_key and mask_sensitive else self.gemini_api_key or ""),
            "github_webhook_secret": self.github_webhook_secret if not mask_sensitive else "***",
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Repository(db.Model):
    """Connected GitHub repositories"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    github_url = db.Column(db.String(500), nullable=False)
    webhook_id = db.Column(db.String(100))  # GitHub webhook ID
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "github_url": self.github_url,
            "webhook_id": self.webhook_id,
            "active": self.active,
            "created_at": self.created_at.isoformat()
        }

class Job(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    repo_url = db.Column(db.String(200), nullable=False)
    commit_sha = db.Column(db.String(100), nullable=False)
    pusher = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    status = db.Column(db.String(20), default="queued") # queued, running, success, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    report_content = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "repo_url": self.repo_url,
            "commit_sha": self.commit_sha,
            "pusher": self.pusher,
            "branch": self.branch,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "report_content": self.report_content
        }

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(50), db.ForeignKey('job.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
