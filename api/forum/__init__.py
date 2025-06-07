from flask import Blueprint

forum_bp = Blueprint('forum', __name__)

from . import routes  # 移到blueprint创建之后

# 自动导入路由模块中的所有路由，使得 edit_post 等 endpoint 能被注册
# <CURRENT_CURSOR_POSITION>
