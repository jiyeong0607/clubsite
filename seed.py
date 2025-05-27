import csv
import os
from app import db
from app.models import User, Category, Group, Member
from werkzeug.security import generate_password_hash

# CSV 파일 경로 설정
CSV_DIR = os.path.join('app', 'static', 'data')

def load_users():
    with open(os.path.join(CSV_DIR, 'users.csv'), encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = User(
                id=row['id'],
                name=row['name'],
                password_hash=generate_password_hash(row['password']),
                is_admin=row['is_admin'].strip().lower() in ['1', 'true', 'yes']
            )
            db.session.add(user)

def load_categories():
    with open(os.path.join(CSV_DIR, 'categories.csv'), encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.session.add(Category(id=row['id'], name=row['name']))

def load_groups():
    with open(os.path.join(CSV_DIR, 'groups.csv'), encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.session.add(Group(id=row['id'], name=row['name'], category_id=row['category_id']))

def load_members():
    with open(os.path.join(CSV_DIR, 'members.csv'), encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.session.add(Member(
                id=row['id'],
                name=row['name'],
                department=row['department'],
                blog_url=row['blog_url'],
                group_id=row['group_id']
            ))

def main():
    load_categories()
    load_groups()
    load_members()
    load_users()
    db.session.commit()

if __name__ == '__main__':
    main()
    db.create_all()