# app/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User와 Member 관계 설정
    member = db.relationship('Member', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin_user(self):
        """관리자인지 확인"""
        return self.is_admin
    
    def get_member_info(self):
        """해당 사용자의 Member 정보 반환"""
        return Member.query.filter_by(user_id=self.id).first()
    
    def get_accessible_groups(self):
        """접근 가능한 그룹들 반환"""
        if self.is_admin:
            return Group.query.all()
        else:
            member = self.get_member_info()
            if member:
                return [member.group]
            return []
    
    def get_teams(self):
        """사용자가 속한 팀들 반환 (auth.py에서 사용)"""
        return self.get_accessible_groups()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    groups = db.relationship('Group', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    members = db.relationship('Member', backref='group', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_member_count(self):
        """그룹 멤버 수 반환"""
        return len(self.members)
    
    def has_member(self, user_id):
        """특정 사용자가 이 그룹의 멤버인지 확인"""
        return any(member.user_id == user_id for member in self.members if member.user_id)
    
    def __repr__(self):
        return f'<Group {self.name}>'

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(150))
    blog_url = db.Column(db.String(200))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)