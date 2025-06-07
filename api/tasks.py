from celery import Celery
from api.models import db, Product, PriceHistory
from api.crawler.spider import ProductSpider
from datetime import datetime

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def crawl_products():
    """爬取商品信息的定时任务"""
    spider = ProductSpider()
    spider.crawl_all_platforms()

@celery.task
def update_product_prices():
    """更新商品价格的定时任务"""
    products = Product.query.all()
    for product in products:
        try:
            new_price = get_current_price(product)
            if new_price != product.current_price:
                # 记录价格历史
                history = PriceHistory(
                    product_id=product.id,
                    price=new_price,
                    timestamp=datetime.now()
                )
                db.session.add(history)
                
                # 更新当前价格
                product.current_price = new_price
                product.updated_at = datetime.now()
                
                db.session.commit()
        except Exception as e:
            print(f"更新商品 {product.id} 价格失败: {str(e)}")

@celery.task
def analyze_user_preferences():
    """分析用户偏好的定时任务"""
    from api.analytics.user_preferences import UserPreferenceAnalyzer
    users = User.query.all()
    for user in users:
        analyzer = UserPreferenceAnalyzer(user.id)
        analyzer.analyze_preferences()