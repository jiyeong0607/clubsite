from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Category, Group, Member

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    categories = Category.query.all()
    return render_template('index.html', categories=categories, title = 'main page')


@main_bp.route('/category/<int:cat_id>')
@login_required
def view_groups(cat_id):
    groups = Group.query.filter_by(category_id=cat_id).all()
    return render_template('groups.html', groups=groups)

@main_bp.route('/group/<int:group_id>')
@login_required
def view_members(group_id):
    members = Member.query.filter_by(group_id=group_id).all()
    return render_template('members.html', members=members)