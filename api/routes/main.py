from flask import Blueprint, render_template, redirect, url_for, flash, abort, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页"""
    if current_user.is_authenticated:
        # 如果用户已登录，创建新会话并重定向到聊天页面
        return redirect(url_for('ai.chat'))
    return render_template('landing.html', today=datetime.utcnow(), site_name='数潮商城')

@main_bp.route('/test-csrf', methods=['GET', 'POST'])
def test_csrf():
    """测试CSRF配置"""
    if request.method == 'POST':
        try:
            # 如果能到达这里，说明CSRF验证通过
            return jsonify({
                'success': True,
                'message': 'CSRF验证通过'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'发生错误: {str(e)}'
            }), 500
    return render_template('test_csrf.html')

@main_bp.route('/about')
def about():
    """关于我们"""
    return render_template('about.html')

@main_bp.route('/terms')
def terms():
    """服务条款"""
    return render_template('terms.html')

@main_bp.route('/privacy')
def privacy():
    """隐私政策"""
    return render_template('privacy.html')

@main_bp.errorhandler(404)
def page_not_found(e):
    """404错误处理"""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_server_error(e):
    """500错误处理"""
    return render_template('errors/500.html'), 500

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """用户仪表板"""
    return render_template('dashboard.html')

@main_bp.route('/profile')
@login_required
def profile():
    """用户个人资料"""
    return render_template('user/profile.html')

@main_bp.route('/settings')
@login_required
def settings():
    """用户设置"""
    return render_template('user/settings.html') 