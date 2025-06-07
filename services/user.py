from sqlalchemy.orm import Session
from ..models.database_models import UserDB, BudgetDB
from datetime import datetime
from typing import List, Optional

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_profile(self, user_id: str):
        return self.db.query(UserDB).filter(UserDB.id == user_id).first()
    
    def update_preferences(self, user_id: str, preferences: List[str]):
        user = self.get_user_profile(user_id)
        if user:
            user.preferences = preferences
            user.updated_at = datetime.utcnow()
            self.db.commit()
            return user
        return None
    
    def track_user_behavior(self, user_id: str, behavior_data: dict):
        # 记录用户行为数据
        behavior = UserBehavior(
            user_id=user_id,
            action=behavior_data['action'],
            target_type=behavior_data['target_type'],
            target_id=behavior_data['target_id'],
            timestamp=datetime.utcnow()
        )
        self.db.add(behavior)
        self.db.commit() 