from datetime import datetime, timedelta
from sqlalchemy import desc
from ..models import db, Product, PurchaseHistory, BrowsingHistory, UserPreference

def get_recommendations(user, keywords, intent, crawler_task):
    """
    基于用户偏好和搜索意图生成商品推荐
    """
    # 等待爬虫任务完成
    while crawler_task.status == 'running':
        db.session.refresh(crawler_task)
    
    if crawler_task.status == 'failed':
        return []
    
    # 获取最新爬取的商品
    products = Product.query.filter(
        Product.last_crawled_at >= crawler_task.created_at
    ).all()
    
    if not products:
        return []
    
    # 计算每个商品的推荐分数
    scored_products = []
    for product in products:
        score = calculate_product_score(product, user, intent)
        if score > 0:
            product_dict = product_to_dict(product)
            product_dict['score'] = score
            product_dict['reason'] = generate_recommendation_reason(product, intent)
            scored_products.append(product_dict)
    
    # 按分数排序
    scored_products.sort(key=lambda x: x['score'], reverse=True)
    
    # 返回前10个推荐
    return scored_products[:10]

def calculate_product_score(product, user, intent):
    """计算商品推荐分数"""
    score = 0.0
    
    # 基础分数
    score += 1.0
    
    # 价格匹配度
    if intent.get('budget'):
        if product.current_price <= intent['budget']:
            score += 2.0
        else:
            score -= (product.current_price - intent['budget']) / intent['budget']
    
    # 品牌匹配度
    if intent.get('brand') and product.brand == intent['brand']:
        score += 1.5
    
    # 功能特性匹配度
    if product.specifications:
        for feature in intent.get('features', []):
            if feature.lower() in str(product.specifications).lower():
                score += 1.0
    
    # 用户历史购买行为
    purchase_history = PurchaseHistory.query.filter_by(
        user_id=user.id,
        product_id=product.id
    ).first()
    if purchase_history:
        score += 0.5
    
    # 用户浏览历史
    browse_history = BrowsingHistory.query.filter_by(
        user_id=user.id,
        product_id=product.id
    ).first()
    if browse_history:
        score += 0.3
    
    # 用户偏好
    user_prefs = UserPreference.query.filter_by(user_id=user.id).all()
    for pref in user_prefs:
        if pref.category.lower() in str(product.specifications).lower():
            score += pref.weight
    
    # 价格趋势
    if product.price_history and len(product.price_history) > 1:
        current_price = product.current_price
        avg_price = sum(ph['price'] for ph in product.price_history) / len(product.price_history)
        if current_price < avg_price:
            score += 0.5
    
    # 销量和评分
    if product.sales_count:
        score += min(product.sales_count / 1000, 1.0)
    if product.rating:
        score += product.rating / 5.0
    
    return max(score, 0.0)

def generate_recommendation_reason(product, intent):
    """生成推荐理由"""
    reasons = []
    
    # 价格相关
    if intent.get('budget'):
        if product.current_price <= intent['budget']:
            reasons.append(f"在预算范围内（¥{intent['budget']}）")
        if product.price_history and product.current_price == product.lowest_price:
            reasons.append("当前处于历史最低价")
    
    # 品牌相关
    if intent.get('brand') and product.brand == intent['brand']:
        reasons.append(f"您指定的{product.brand}品牌")
    
    # 功能特性
    matched_features = []
    if product.specifications:
        for feature in intent.get('features', []):
            if feature.lower() in str(product.specifications).lower():
                matched_features.append(feature)
    if matched_features:
        reasons.append(f"符合您需要的{', '.join(matched_features)}特性")
    
    # 评分和销量
    if product.rating and product.rating >= 4.5:
        reasons.append(f"用户评分高达{product.rating}分")
    if product.sales_count and product.sales_count > 1000:
        reasons.append(f"月销量{product.sales_count}+")
    
    # 组合理由
    if reasons:
        return "；".join(reasons) + "。"
    return "根据您的需求推荐。"

def product_to_dict(product):
    """将商品对象转换为字典"""
    return {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'category': product.category,
        'current_price': product.current_price,
        'original_price': product.original_price,
        'platform': product.platform,
        'platform_url': product.platform_url,
        'brand': product.brand,
        'model': product.model,
        'specifications': product.specifications,
        'images': product.images,
        'discount_info': product.discount_info,
        'stock': product.stock,
        'sales_count': product.sales_count,
        'rating': product.rating,
        'rating_count': product.rating_count
    } 