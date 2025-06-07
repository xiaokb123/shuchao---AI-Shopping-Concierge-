from flask import Blueprint, jsonify, request, render_template
from api.models import db, Product
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
def index():
    """商品列表页面"""
    return render_template('products/index.html')

@products_bp.route('/search')
def search():
    """搜索商品API"""
    query = request.args.get('q', '')
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort = request.args.get('sort', 'default')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    # 构建基础查询
    products_query = Product.query

    # 关键词搜索
    if query:
        search_filter = or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%'),
            Product.brand.ilike(f'%{query}%')
        )
        products_query = products_query.filter(search_filter)

    # 分类过滤
    if category:
        products_query = products_query.filter(Product.category == category)

    # 价格范围过滤
    if min_price is not None:
        products_query = products_query.filter(Product.current_price >= min_price)
    if max_price is not None:
        products_query = products_query.filter(Product.current_price <= max_price)

    # 排序
    if sort == 'price_asc':
        products_query = products_query.order_by(Product.current_price.asc())
    elif sort == 'price_desc':
        products_query = products_query.order_by(Product.current_price.desc())
    elif sort == 'sales':
        products_query = products_query.order_by(Product.sales_count.desc())
    elif sort == 'rating':
        products_query = products_query.order_by(Product.rating.desc())
    else:
        products_query = products_query.order_by(Product.created_at.desc())

    # 分页
    pagination = products_query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    # 构建响应数据
    response = {
        'success': True,
        'data': {
            'products': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'current_price': p.current_price,
                'original_price': p.original_price,
                'discount': p.discount,
                'brand': p.brand,
                'category': p.category,
                'rating': p.rating,
                'sales_count': p.sales_count,
                'images': p.images,
                'platform': p.platform,
                'platform_url': p.platform_url
            } for p in products],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }
    }

    return jsonify(response)

@products_bp.route('/<int:product_id>')
def detail(product_id):
    """商品详情页面"""
    product = Product.query.get_or_404(product_id)
    return render_template('products/detail.html', product=product)

@products_bp.route('/categories')
def get_categories():
    """获取所有商品分类"""
    categories = db.session.query(Product.category).distinct().all()
    return jsonify({
        'success': True,
        'data': [category[0] for category in categories if category[0]]
    }) 