# app/decorators.py
from functools import wraps
from flask import abort, redirect, url_for, request, flash
from flask_login import current_user, login_required

def admin_required(f):
    """관리자 권한이 필요한 페이지에 사용하는 데코레이터"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin_user():
            flash('관리자 권한이 필요합니다.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def group_access_required(f):
    """그룹 상세 정보 접근 시 권한 확인 데코레이터"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # 함수 호출 시점에 import하여 순환 import 방지
        from app.models import Group
        
        group_id = kwargs.get('group_id') or request.view_args.get('group_id')
        if not group_id:
            abort(404)
        
        group = Group.query.get_or_404(group_id)
        
        # 관리자는 모든 그룹에 접근 가능
        if current_user.is_admin_user():
            return f(*args, **kwargs)
        
        # 해당 그룹의 멤버인지 확인
        if not group.has_member(current_user.id):
            flash('해당 그룹의 정보에 접근할 권한이 없습니다.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def member_access_required(f):
    """멤버 개인정보 접근 시 권한 확인 데코레이터"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        from app.models import Member
        
        member_id = kwargs.get('member_id') or request.view_args.get('member_id')
        if not member_id:
            abort(404)
        
        member = Member.query.get_or_404(member_id)
        
        # 관리자는 모든 멤버 정보에 접근 가능
        if current_user.is_admin_user():
            return f(*args, **kwargs)
        
        # 같은 그룹 멤버인지 확인
        user_member = current_user.get_member_info()
        if not user_member or user_member.group_id != member.group_id:
            flash('해당 멤버의 정보에 접근할 권한이 없습니다.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def own_profile_or_admin_required(f):
    """자신의 프로필이거나 관리자만 접근 가능한 데코레이터"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id') or request.view_args.get('user_id')
        if not user_id:
            abort(404)
        
        # 관리자이거나 자신의 프로필인 경우
        if current_user.is_admin_user() or current_user.id == int(user_id):
            return f(*args, **kwargs)
        
        flash('접근 권한이 없습니다.', 'error')
        abort(403)
    return decorated_function