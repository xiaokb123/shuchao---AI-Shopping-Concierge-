from typing import List, Dict, Any
from api.models import Product, db
from sqlalchemy import or_, and_

def search_products(recommendations: List[Dict[str, Any]], limit: int = 3) -> List[Product]:
    """
    根据推荐信息搜索商品
    
    Args:
        recommendations: 推荐信息列表
        limit: 每个推荐返回的最大商品数量
        
    Returns:
        匹配的商品列表
    """
    products = []
    
    for rec in recommendations:
        # 构建查询条件
        conditions = []
        
        # 价格范围
        price_range = rec.get('price_range', {})
        if price_range.get('min') is not None:
            conditions.append(Product.current_price >= price_range['min'])
        if price_range.get('max') is not None:
            conditions.append(Product.current_price <= price_range['max'])
            
        # 品牌
        brands = rec.get('brands', [])
        if brands:
            conditions.append(Product.brand.in_(brands))
            
        # 类别
        categories = rec.get('categories', [])
        if categories:
            conditions.append(Product.category.in_(categories))
            
        # 关键词搜索
        keywords = rec.get('keywords', '').split()
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(
                    or_(
                        Product.name.ilike(f'%{keyword}%'),
                        Product.description.ilike(f'%{keyword}%')
                    )
                )
            conditions.append(and_(*keyword_conditions))
            
        # 执行查询
        query = Product.query
        if conditions:
            query = query.filter(and_(*conditions))
            
        # 排序和限制
        matched_products = (
            query.order_by(Product.sales_count.desc())
            .limit(limit)
            .all()
        )
        
        # 添加推荐原因
        for product in matched_products:
            product.reason = generate_recommendation_reason(product, rec)
            products.append(product)
    
    return products

def generate_recommendation_reason(product: Product, recommendation: Dict[str, Any]) -> str:
    """
    生成推荐理由
    
    Args:
        product: 商品对象
        recommendation: 推荐信息
        
    Returns:
        推荐理由
    """
    reasons = []
    
    # 价格相关
    price_range = recommendation.get('price_range', {})
    if price_range.get('min') is not None and price_range.get('max') is not None:
        if price_range['min'] <= product.current_price <= price_range['max']:
            reasons.append(f"价格{product.current_price}元在您的预算范围内")
            
    # 品牌相关
    if product.brand in recommendation.get('brands', []):
        reasons.append(f"属于您偏好的{product.brand}品牌")
        
    # 销量相关
    if product.sales_count > 1000:
        reasons.append("销量优秀")
    elif product.sales_count > 500:
        reasons.append("销量良好")
        
    # 评分相关
    if product.rating >= 4.5:
        reasons.append("好评率极高")
    elif product.rating >= 4.0:
        reasons.append("评价优秀")
        
    # 组合理由
    if reasons:
        return "，".join(reasons)
    return "根据您的需求推荐"

def get_similar_products(product_id: int, limit: int = 3) -> List[Product]:
    """
    获取相似商品
    
    Args:
        product_id: 商品ID
        limit: 返回的最大商品数量
        
    Returns:
        相似商品列表
    """
    product = db.session.get(Product, product_id)
    if not product:
        return []
        
    # 查找同类别、同价位的商品
    similar_products = (
        Product.query
        .filter(
            Product.id != product_id,
            Product.category == product.category,
            Product.current_price.between(
                product.current_price * 0.7,
                product.current_price * 1.3
            )
        )
        .order_by(Product.sales_count.desc())
        .limit(limit)
        .all()
    )
    
    return similar_products

def get_product_details(product_id):
    """获取商品详细信息"""
    product = db.session.get(Product, product_id)
    if not product:
        return None 