# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(name=username).first()  # 수정: name 필드 사용
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            
            # 관리자라면 관리자 대시보드로, 일반 사용자라면 일반 대시보드로
            if user.is_admin_user():  # 수정: 올바른 메서드명
                flash(f'관리자로 로그인되었습니다. 환영합니다, {user.name}님!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash(f'로그인되었습니다. 환영합니다, {user.name}님!', 'success')
                return redirect(url_for('main.dashboard'))
        else:
            flash('사용자명 또는 비밀번호가 올바르지 않습니다.', 'error')
    
    return render_template('auth/login.html', title='로그인')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index0'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        birthdate_str = request.form.get('birthdate')
        
        # 유효성 검사
        if not all([username, email, password, confirm_password, birthdate_str]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('auth/signup.html', title='회원가입')
        
        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('auth/signup.html', title='회원가입')
        
        # 중복 확인
        if User.query.filter_by(name=username).first():
            flash('이미 존재하는 사용자명입니다.', 'error')
            return render_template('auth/signup.html', title='회원가입')
        
        if User.query.filter_by(email=email).first():
            flash('이미 존재하는 이메일입니다.', 'error')
            return render_template('auth/signup.html', title='회원가입')
        
        # 생년월일 변환
        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
        except ValueError:
            flash('올바른 생년월일 형식을 입력해주세요. (YYYY-MM-DD)', 'error')
            return render_template('auth/signup.html', title='회원가입')
        
        # 새 사용자 생성
        user = User(
            name=username, 
            email=email,
            birthdate=birthdate
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/signup.html', title='회원가입')

@auth_bp.route('/logout')
@login_required
def logout():
    """로그아웃"""
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('main.index0'))