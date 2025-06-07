from typing import List
import asyncio
from datetime import datetime

class NotificationService:
    def __init__(self):
        self.notification_queue = asyncio.Queue()
    
    async def send_budget_alert(self, user_id: str, budget_type: str, current_spent: float, limit: float):
        message = {
            'type': 'budget_alert',
            'user_id': user_id,
            'content': f'您的{budget_type}预算已使用{(current_spent/limit)*100:.1f}%',
            'timestamp': datetime.utcnow()
        }
        await self.notification_queue.put(message)
    
    async def send_price_alert(self, user_id: str, product_id: str, current_price: float, target_price: float):
        message = {
            'type': 'price_alert',
            'user_id': user_id,
            'content': f'您关注的商品已降至目标价格¥{current_price}',
            'timestamp': datetime.utcnow()
        }
        await self.notification_queue.put(message)
    
    async def process_notifications(self):
        while True:
            message = await self.notification_queue.get()
            # 实现具体的推送逻辑（可以使用WebSocket、极光推送等）
            await self._send_notification(message)
            self.notification_queue.task_done() 