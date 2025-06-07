from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Regexp
from api.models import User

class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        validators.Email(message='请输入有效的邮箱地址')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码')
    ])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=20, message='用户名长度必须在3到20个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        validators.Email(message='请输入有效的邮箱地址')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码'),
        Length(min=6, message='密码长度不能少于6个字符')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('注册')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('该用户名已被使用')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('该邮箱已被注册')

class ForgotPasswordForm(FlaskForm):
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        validators.Email(message='请输入有效的邮箱地址')
    ])
    submit = SubmitField('发送重置链接')

class ResetPasswordForm(FlaskForm):
    """密码重置表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        validators.Email(message='请输入有效的邮箱地址')
    ])
    password = PasswordField('新密码', validators=[
        DataRequired(message='请输入新密码'),
        Length(min=8, message='密码长度必须大于8个字符'),
        Regexp(r'[A-Z]', message='密码必须包含至少一个大写字母'),
        Regexp(r'[a-z]', message='密码必须包含至少一个小写字母'),
        Regexp(r'\d', message='密码必须包含至少一个数字'),
        Regexp(r'[!@#$%^&*(),.?":{}|<>]', message='密码必须包含至少一个特殊字符')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('重置密码')