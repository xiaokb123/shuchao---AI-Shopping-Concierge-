from api.models import db, Product, PriceHistory
import asyncio
from datetime import datetime

class PriceTracker:
    def __init__(self):
        self.update_interval = 3600  # 每小时更新一次
        
    async def start_tracking(self):
        """开始价格追踪"""
        while True:
            await self._update_all_prices()
            await asyncio.sleep(self.update_interval)
    
    async def _update_all_prices(self):
        """更新所有商品价格"""
        products = Product.query.all()
        
        for product in products:
            try:
                new_price = await self._fetch_current_price(product)
                
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
                    product.price_updated_at = datetime.now()
                    
                    db.session.commit()
            except Exception as e:
                print(f"更新商品 {product.id} 价格失败: {str(e)}")