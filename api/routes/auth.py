from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from api.models import db, User
from api.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask import current_app
from api.utils.email import send_password_reset_email
from flask_wtf.csrf import CSRFProtect

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录处理"""
    if current_user.is_authenticated:
        return redirect(url_for('ai.chat'))
    
    form = LoginForm()
    try:
        if request.method == 'POST':
            if request.headers.get('Accept') == 'application/json':
                # 处理AJAX请求
                email = request.form.get('email')
                password = request.form.get('password')
                remember = request.form.get('remember', False)
                
                user = User.query.filter_by(email=email).first()
                
                if not user:
                    return jsonify({'success': False, 'error': '该邮箱未注册。'})
                
                if not user.is_active:
                    return jsonify({'success': False, 'error': '该账号已被禁用，请联系管理员。'})
                
                if not user.check_password(password):
                    return jsonify({'success': False, 'error': '密码错误！'})
                
                # 登录成功
                login_user(user, remember=remember)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': '登录成功！',
                    'redirect': url_for('ai.chat')
                })
            else:
                # 处理表单提交
                if form.validate_on_submit():
                    user = User.query.filter_by(email=form.email.data).first()
                    
                    if not user:
                        flash('该邮箱未注册。', 'error')
                        return render_template('auth/login.html', form=form)
                    
                    if not user.is_active:
                        flash('该账号已被禁用，请联系管理员。', 'error')
                        return render_template('auth/login.html', form=form)
                    
                    if not user.check_password(form.password.data):
                        flash('密码错误！', 'error')
                        return render_template('auth/login.html', form=form)
                    
                    # 登录成功
                    login_user(user, remember=form.remember_me.data)
                    user.last_login = datetime.utcnow()
                    db.session.commit()
                    
                    flash('登录成功！', 'success')
                    return redirect(url_for('ai.chat'))
            
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'success': False, 'error': '登录时发生错误，请稍后重试。'})
        flash('登录时发生错误，请稍后重试。', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('您已成功退出！', 'success')
    return redirect(url_for('main.index'))

def is_safe_url(target):
    """验证重定向URL是否安全"""
    from urllib.parse import urlparse, urljoin
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('ai.chat'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                created_at=datetime.utcnow(),
                is_active=True
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # 注册成功后直接登录
            login_user(user)
            flash('注册成功！欢迎加入。', 'success')
            return redirect(url_for('ai.chat'))
            
        except IntegrityError:
            db.session.rollback()
            flash('用户名或邮箱已被使用。', 'error')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"注册失败: {str(e)}")
            flash('注册失败，请稍后重试。', 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码处理"""
    if current_user.is_authenticated:
        return redirect(url_for('ai.chat'))
    
    form = ForgotPasswordForm()
    try:
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if not user:
                flash('该邮箱未注册。', 'error')
                current_app.logger.warning(f"Password reset attempted for unregistered email: {form.email.data}")
                return render_template('auth/forgot_password.html', form=form)
            
            if not user.is_active:
                flash('该账号已被禁用，请联系管理员。', 'error')
                return render_template('auth/forgot_password.html', form=form)
            
            # 发送重置密码邮件
            if send_password_reset_email(user):
                flash('重置密码链接已发送到您的邮箱，请查收。', 'info')
                current_app.logger.info(f"Password reset email sent to user: {user.username}")
                return redirect(url_for('auth.login'))
            else:
                flash('发送重置邮件失败，请稍后重试。', 'error')
                current_app.logger.error(f"Failed to send password reset email to user: {user.username}")
                return render_template('auth/forgot_password.html', form=form)
    
    except Exception as e:
        current_app.logger.error(f"Forgot password error: {str(e)}")
        flash('处理请求时发生错误，请稍后重试。', 'error')
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码"""
    if current_user.is_authenticated:
        return redirect(url_for('ai.chat'))
    
    form = ResetPasswordForm()  # 需要创建这个表单类
    
    try:
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if not user:
                flash('邮箱地址错误。', 'error')
                return render_template('auth/reset_password.html', form=form)
            
            try:
                if user.reset_password(token, form.password.data):
                    flash('密码已成功重置！请使用新密码登录。', 'success')
                    current_app.logger.info(f"Password reset successful for user: {user.username}")
                    return redirect(url_for('auth.login'))
                else:
                    flash('重置链接无效或已过期。', 'error')
            
            except ValueError as e:
                flash(str(e), 'error')
                current_app.logger.error(f"Password reset failed for user {user.username}: {str(e)}")
            
            except Exception as e:
                current_app.logger.error(f"Unexpected error during password reset: {str(e)}")
                flash('重置密码时发生错误，请稍后重试。', 'error')
    
    except Exception as e:
        current_app.logger.error(f"Error in reset password route: {str(e)}")
        flash('处理请求时发生错误，请稍后重试。', 'error')
    
    return render_template('auth/reset_password.html', form=form, token=token) 