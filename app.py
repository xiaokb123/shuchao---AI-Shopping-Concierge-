from api.utils.template_filters import post_type_color  # 添加导入语句


# 初始化 Flask 应用
app = Flask(__name__, 
    template_folder='../templates',
    static_folder='../static'
)


# 注册自定义过滤器
app.jinja_env.filters['post_type_color'] = post_type_color  # 注册过滤器
