from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user
from datetime import datetime, timedelta
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# 将项目根目录添加到Python路径
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# 加载环境变量
load_dotenv()

# 初始化 Flask 应用
app = Flask(__name__, 
    template_folder='../templates',
    static_folder='../static'
)

# 从配置文件加载配置
from config import Config
app.config.from_object(Config)

# 导入数据库模型
from api.models import db, User

# 初始化数据库
db.init_app(app)
migrate = Migrate(app, db)

# 初始化CORS
CORS(app)

# 初始化CSRF保护
csrf = CSRFProtect(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'info'
login_manager.login_protection = 'strong'
login_manager.refresh_view = 'auth.login'
login_manager.needs_refresh_message = '您的登录已过期，请重新登录'
login_manager.needs_refresh_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# 注册蓝图
from api.routes.forum import forum_bp
from api.routes.ai import ai_bp
from api.routes.auth import auth_bp
from api.routes.products import products_bp
from api.routes.user import user_bp
from api.routes.main import main_bp

# 注册所有蓝图
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(forum_bp, url_prefix='/forum')
app.register_blueprint(main_bp)

@app.route('/')
def index():
    """首页路由"""
    if current_user.is_authenticated:
        return redirect(url_for('ai.chat'))
    response = make_response(render_template('landing.html'))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.after_request
def add_header(response):
    """添加HTTP缓存头"""
    if request.path.startswith('/static/'):
        response.cache_control.max_age = 300
        response.cache_control.public = True
    return response

# 错误处理路由
@app.errorhandler(401)
def unauthorized(error):
    """未授权访问处理"""
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'success': False,
            'message': '请先登录后再访问此页面'
        }), 401
    flash('请先登录后再访问此页面', 'warning')
    return redirect(url_for('auth.login', next=request.path))

@app.errorhandler(404)
def page_not_found(error):
    """页面未找到处理"""
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'success': False,
            'message': '请求的资源不存在'
        }), 404
    return render_template('404.html'), 404
        
@app.errorhandler(500)
def internal_server_error(error):
    """服务器内部错误处理"""
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500
    return render_template('500.html'), 500

# 添加模板全局变量
@app.context_processor
def inject_globals():
    return {
        'today': datetime.utcnow(),
        'site_name': '数潮',
        'site_description': 'AI智能导购助手'
    }

# 添加默认路由处理favicon.ico请求
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('img/favicon.ico')

# 添加Service Worker路由
@app.route('/sw.js')
def service_worker():
    return app.send_static_file('js/sw.js')

def post_type_color(post_type):
    mapping = {
        'question': 'info',
        'discussion': 'primary',
        'announcement': 'warning'
    }
    return mapping.get(post_type, 'secondary')

app.jinja_env.filters['post_type_color'] = post_type_color  # 注册过滤器

def post_type_text(post_type):
    mapping = {
        'question': '提问',
        'discussion': '讨论',
        'announcement': '公告'
    }
    return mapping.get(post_type, '未知')

app.jinja_env.filters['post_type_text'] = post_type_text  # 注册过滤器

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)