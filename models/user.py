from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: str
    username: str
    email: str
    budget: float
    preferences: List[str]
    created_at: datetime
    updated_at: datetime
    
class Budget(BaseModel):
    user_id: str
    amount: float
    spent: float
    category: str
    period: str  # 'monthly', 'weekly', etc.
    start_date: datetime
    end_date: datetime 