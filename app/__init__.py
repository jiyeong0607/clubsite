# app/__init__.py
from flask import Flask, render_template
from flask_login import LoginManager, current_user, login_required
from config import Config

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    # 함수 내부에서 import하여 순환 import 방지
    from app.models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # DB 초기화 (늦은 import)
    from app.models import db
    db.init_app(app)
    
    # 로그인 매니저 초기화
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요합니다.'
    login_manager.login_message_category = 'info'
    
    @app.context_processor
    def inject_user():
        return {
            'current_user': current_user,
            'is_admin': current_user.is_authenticated and current_user.is_admin_user()
        }
    
    # 블루프린트 등록 (늦은 import)
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # 메인 라우트
    from flask import Blueprint
    main_bp = Blueprint('main', __name__)
    
    @main_bp.route('/')
    def index():
        return render_template('index0.html', title='동아리 홈페이지')
    
    @main_bp.route('/dashboard')
    @login_required
    def dashboard():
        user_teams = current_user.get_teams()
        return render_template('index.html',
                             title='대시보드',
                             teams=user_teams)
    
    
    app.register_blueprint(main_bp)
    
    # 에러 핸들러
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from app.models import db  # 함수 내부에서 import
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app