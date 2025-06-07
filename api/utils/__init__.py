from flask import Flask
from .template_filters import time_ago, post_type_text, post_type_color

def init_filters(app: Flask):
    """初始化所有模板过滤器"""
    app.jinja_env.filters['time_ago'] = time_ago
    app.jinja_env.filters['post_type_text'] = post_type_text
    app.jinja_env.filters['post_type_color'] = post_type_color
