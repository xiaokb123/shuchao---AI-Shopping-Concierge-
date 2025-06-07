from api.models import db, UserPreference, BrowsingHistory, ForumPost
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class UserPreferenceAnalyzer:
    def __init__(self, user_id):
        self.user_id = user_id
        self.vectorizer = TfidfVectorizer()
    
    def analyze_preferences(self):
        """综合分析用户偏好"""
        # 浏览历史权重
        browsing_weight = self._analyze_browsing_history()
        
        # 论坛活动权重
        forum_weight = self._analyze_forum_activity()
        
        # 购买历史权重
        purchase_weight = self._analyze_purchase_history()
        
        # 合并所有权重
        combined_weights = {}
        for source in [browsing_weight, forum_weight, purchase_weight]:
            for key, value in source.items():
                combined_weights[key] = combined_weights.get(key, 0) + value
        
        # 更新用户偏好
        self._update_preferences(combined_weights)
    
    def _analyze_browsing_history(self):
        """分析浏览历史"""
        history = BrowsingHistory.query.filter_by(user_id=self.user_id).all()
        weights = {}
        for record in history:
            product = record.product
            # 根据浏览时长和频率计算权重
            weight = 1.0
            if record.view_duration:
                weight *= min(record.view_duration / 60.0, 2.0)
            weights[product.category] = weights.get(product.category, 0) + weight
        return weights