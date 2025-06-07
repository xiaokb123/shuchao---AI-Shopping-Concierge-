from flask_restx import Api, Resource, fields
from flask import Blueprint

# 创建API文档蓝图
api_bp = Blueprint('api', __name__)
api = Api(api_bp, 
    title='数潮 API 文档',
    version='1.0',
    description='数潮智能购物助手API文档',
    doc='/docs'
)

# 定义API模型
user_model = api.model('User', {
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱'),
    'password': fields.String(required=True, description='密码')
})

product_model = api.model('Product', {
    'name': fields.String(description='商品名称'),
    'price': fields.Float(description='当前价格'),
    'description': fields.String(description='商品描述'),
    'platform': fields.String(description='平台')
})

@api.route('/products')
class ProductList(Resource):
    @api.doc('获取商品列表')
    @api.marshal_list_with(product_model)
    def get(self):
        """获取商品列表"""
        return Product.query.all()