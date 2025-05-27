# app/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    """관리자 대시보드"""
    # 함수 내부에서 import하여 순환 import 방지
    from app.models import db, User, Group, Member, Category
    from app.decorators import admin_required
    
    # 데코레이터 수동 적용
    if not current_user.is_authenticated or not current_user.is_admin_user():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 통계 정보 수집
    total_users = User.query.count()
    total_groups = Group.query.count()
    total_members = Member.query.count()
    
    # 카테고리별 그룹 수
    group_stats = (db.session.query(Category.name, func.count(Group.id).label('count'))
                   .join(Group, Category.id == Group.category_id)
                   .group_by(Category.name).all())
    
    # 최근 가입한 사용자들
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         title='관리자 대시보드',
                         total_users=total_users,
                         total_groups=total_groups,
                         total_members=total_members,
                         group_stats=group_stats,
                         recent_users=recent_users)

@admin_bp.route('/users')
def manage_users():
    """사용자 관리 페이지"""
    from app.models import User
    
    if not current_user.is_authenticated or not current_user.is_admin_user():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html',
                         title='사용자 관리',
                         users=users)

@admin_bp.route('/users/<int:user_id>/admin-toggle', methods=['POST'])
def toggle_user_admin(user_id):
    """사용자 관리자 권한 토글"""
    from app.models import db, User
    
    if not current_user.is_authenticated or not current_user.is_admin_user():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(user_id)
    
    # 자기 자신의 권한은 변경할 수 없음
    if user.id == current_user.id:
        flash('자신의 권한은 변경할 수 없습니다.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    old_status = '관리자' if user.is_admin else '일반사용자'
    user.is_admin = not user.is_admin
    new_status = '관리자' if user.is_admin else '일반사용자'
    
    db.session.commit()
    
    flash(f'{user.name}의 권한이 {old_status}에서 {new_status}로 변경되었습니다.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """사용자 삭제"""
    from app.models import db, User
    
    if not current_user.is_authenticated or not current_user.is_admin_user():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(user_id)
    
    # 자기 자신은 삭제할 수 없음
    if user.id == current_user.id:
        flash('자신의 계정은 삭제할 수 없습니다.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    username = user.name
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'{username} 사용자가 삭제되었습니다.', 'info')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/groups')
def manage_groups():
    """그룹 관리 페이지"""
    from app.models import Group
    
    if not current_user.is_authenticated or not current_user.is_admin_user():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    groups = Group.query.all()
    
    return render_template('admin/groups.html',
                         title='그룹 관리',
                         groups=groups)

@admin_bp.route('/groups/<int:group_id>')
def group_admin_detail(group_id):
    """관리자용 그룹 상세 정보"""
    from app.models import Group, Member
    
    if not current_user.is_authenticated or not current_user.is_admin_user():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    group = Group.query.get_or_404(group_id)
    members = Member.query.filter_by(group_id=group_id).all()
    
    return render_template('admin/group_detail.html',
                         title=f'{group.name} 그룹 관리',
                         group=group,
                         members=members)

@admin_bp.route('/groups/create', methods=['GET', 'POST'])
def create_group():
    """새 그룹 생성"""
    from app.models import db, Group, Category
    
    if not current_user.is_authenticated or not current_user.is_admin_user():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        
        if not name or not category_id:
            flash('그룹 이름과 카테고리를 입력해주세요.', 'error')
            categories = Category.query.all()
            return render_template('admin/create_group.html', 
                                 title='새 그룹 생성', 
                                 categories=categories)
        
        # 중복 확인
        if Group.query.filter_by(name=name).first():
            flash('이미 존재하는 그룹명입니다.', 'error')
            categories = Category.query.all()
            return render_template('admin/create_group.html', 
                                 title='새 그룹 생성', 
                                 categories=categories)
        
        new_group = Group(name=name, category_id=category_id)
        db.session.add(new_group)
        db.session.commit()
        
        flash(f'{name} 그룹이 생성되었습니다.', 'success')
        return redirect(url_for('admin.manage_groups'))
    
    categories = Category.query.all()
    return render_template('admin/create_group.html', 
                         title='새 그룹 생성',
                         categories=categories)

@admin_bp.route('/groups/<int:group_id>/delete', methods=['POST'])
def delete_group(group_id):
    """그룹 삭제"""
    from app.models import db, Group
    
    if not current_user.is_authenticated or not current_user.is_admin_user():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    group = Group.query.get_or_404(group_id)
    group_name = group.name
    
    db.session.delete(group)
    db.session.commit()
    
    flash(f'{group_name} 그룹이 삭제되었습니다.', 'info')
    return redirect(url_for('admin.manage_groups'))

@admin_bp.route('/all-groups-data')
def all_groups_data():
    """모든 그룹의 상세 정보 (관리자 전용)"""
    from app.models import Group
    
    if not current_user.is_authenticated or not current_user.is_admin_user():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('login'))
    
    groups = Group.query.all()
    group_data = []
    
    for group in groups:
        members_data = []
        for member in group.members:
            member_info = {
                'name': member.name,
                'department': member.department or '미설정',
                'blog_url': member.blog_url or '없음'
            }
            if member.user:
                member_info.update({
                    'email': member.user.email,
                    'joined_at': member.user.created_at.strftime('%Y-%m-%d')
                })
            members_data.append(member_info)
        
        group_data.append({
            'id': group.id,
            'name': group.name,
            'category': group.category.name,
            'member_count': len(group.members),
            'members': members_data
        })
    
    return render_template('admin/all_groups_data.html',
                         title='전체 그룹 데이터',
                         groups_data=group_data)