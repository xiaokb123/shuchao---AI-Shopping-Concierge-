from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from api.utils.email import mail
from api.utils.template_filters import time_ago, post_type_text, post_type_color
from api.utils.security import setup_security, csrf
from config import config
from flask_wtf.csrf import CSRFProtect, generate_csrf

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录。'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()

# 用户加载回调
@login_manager.user_loader
def load_user(user_id):
    from api.models import User
    return User.query.get(int(user_id))

def create_app(config_name='default'):
    app = Flask(__name__, template_folder='../templates')
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 开发环境配置
    if app.config['DEBUG']:
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        app.jinja_env.auto_reload = True
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # 设置安全相关配置
    setup_security(app)
    
    # 注册模板过滤器
    from api.utils.template_filters import time_ago, post_type_text, post_type_color
    app.jinja_env.filters.update({
        'time_ago': time_ago,
        'post_type_text': post_type_text,
        'post_type_color': post_type_color
    })
    
    # 添加csrf_token到所有模板的上下文
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf())
    
    # 导入蓝图
    from api.routes.main import main_bp
    from api.routes.auth import auth_bp
    from api.routes.user import user_bp
    from api.routes.products import products_bp
    from api.routes.ai import ai_bp
    from api.routes.forum import forum_bp  # 修正导入路径
    
    # 注册蓝图（注意顺序）
    app.register_blueprint(main_bp)  # 主蓝图放在最前面
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(forum_bp, url_prefix='/forum')
    
    return app
