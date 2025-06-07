from api.models import db, Budget, PurchaseHistory
from datetime import datetime, timedelta
import asyncio
from api.utils.notification import send_notification

class BudgetAlertManager:
    def __init__(self, user_id):
        self.user_id = user_id
        
    async def check_budget_status(self):
        """检查预算状态并发送提醒"""
        budgets = Budget.query.filter_by(user_id=self.user_id).all()
        
        for budget in budgets:
            percentage = await self._calculate_usage_percentage(budget)
            
            if percentage >= 80 and not budget.warning_sent:
                # 发送预警通知
                await self._send_warning_notification(budget, percentage)
                budget.warning_sent = True
                db.session.commit()
            
            if percentage >= 100 and not budget.limit_reached_sent:
                # 发送超限通知
                await self._send_limit_reached_notification(budget, percentage)
                budget.limit_reached_sent = True
                db.session.commit()
    
    async def _calculate_usage_percentage(self, budget):
        """计算预算使用百分比"""
        total_spent = db.session.query(
            db.func.sum(PurchaseHistory.amount)
        ).filter(
            PurchaseHistory.user_id == self.user_id,
            PurchaseHistory.category == budget.category,
            PurchaseHistory.purchase_time.between(budget.start_date, budget.end_date)
        ).scalar() or 0
        
        return (total_spent / budget.amount) * 100 if budget.amount > 0 else 0