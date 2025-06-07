import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from api.models import db, Purchase, Product, User

class AdvancedAnalytics:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def analyze_shopping_patterns(self, user_id):
        """分析购物模式"""
        purchases = Purchase.query.filter_by(user_id=user_id).all()
        
        # 转换为DataFrame
        df = pd.DataFrame([{
            'product_id': p.product_id,
            'amount': p.amount,
            'timestamp': p.timestamp,
            'category': p.product.category
        } for p in purchases])
        
        # 时间序列分析
        time_patterns = self._analyze_time_patterns(df)
        
        # 类别偏好分析
        category_preferences = self._analyze_category_preferences(df)
        
        # 价格敏感度分析
        price_sensitivity = self._analyze_price_sensitivity(df)
        
        return {
            'time_patterns': time_patterns,
            'category_preferences': category_preferences,
            'price_sensitivity': price_sensitivity
        }
    
    def generate_business_insights(self):
        """生成商业洞察"""
        # 销售趋势分析
        sales_trends = self._analyze_sales_trends()
        
        # 用户群体分析
        user_segments = self._analyze_user_segments()
        
        # 商品组合分析
        product_combinations = self._analyze_product_combinations()
        
        return {
            'sales_trends': sales_trends,
            'user_segments': user_segments,
            'product_combinations': product_combinations
        }