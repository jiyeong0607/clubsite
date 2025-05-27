# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    # app context 내에서 DB 관련 작업
    with app.app_context():
        from app.models import db, User, Category
        
        db.create_all()
        
        # 기본 카테고리 생성
        if not Category.query.first():
            beginner = Category(name='비기너')
            challenger = Category(name='챌린저')
            db.session.add(beginner)
            db.session.add(challenger)
            db.session.commit()
            print("기본 카테고리가 생성되었습니다.")
        
        # 관리자 계정 생성
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            from datetime import date
            admin_user = User(
                name='admin',
                email='admin@club.com',
                is_admin=True,
                birthdate=date(1990, 1, 1)
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("관리자 계정이 생성되었습니다. (admin/admin123)")
        
    app.run(debug=True)