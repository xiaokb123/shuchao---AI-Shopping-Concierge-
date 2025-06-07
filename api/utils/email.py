from flask import current_app, render_template, url_for
from flask_mail import Message, Mail
from threading import Thread
from datetime import datetime

mail = Mail()

def send_async_email(app, msg):
    """异步发送邮件"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")

def send_email(subject, recipients, template, **kwargs):
    """发送邮件的通用函数"""
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        # 添加当前年份到模板上下文
        kwargs['year'] = datetime.utcnow().year
        msg.html = render_template(template, **kwargs)
        
        # 在后台线程中发送邮件
        Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg)
        ).start()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error preparing email: {str(e)}")
        return False

def send_password_reset_email(user):
    """发送密码重置邮件"""
    try:
        token = user.generate_reset_token()
        send_email(
            '重置您的密码',
            [user.email],
            'email/reset_password.html',
            user=user,
            token=token,
            reset_url=url_for('auth.reset_password', token=token, _external=True)
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending password reset email: {str(e)}")
        return False 