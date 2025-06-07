from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 个人资料
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    occupation = db.Column(db.String(64))
    
    # 预算设置
    monthly_budget = db.Column(db.Float, default=0.0)
    
    # 购物偏好
    interests = db.Column(db.JSON, default=list)
    price_sensitivity = db.Column(db.Integer, default=50)
    
    # 通知设置
    email_notifications = db.Column(db.Boolean, default=True)
    price_alerts = db.Column(db.Boolean, default=True)
    recommendation_notifications = db.Column(db.Boolean, default=True)
    
    # 关联关系
    chat_sessions = db.relationship('ChatSession', backref='user', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'gender': self.gender,
            'age': self.age,
            'occupation': self.occupation,
            'monthly_budget': self.monthly_budget,
            'interests': self.interests,
            'price_sensitivity': self.price_sensitivity,
            'email_notifications': self.email_notifications,
            'price_alerts': self.price_alerts,
            'recommendation_notifications': self.recommendation_notifications,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>' 