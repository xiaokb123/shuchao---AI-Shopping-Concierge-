from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.database_models import ProductDB
from typing import Optional
import jieba

class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        platform: Optional[str] = None
    ):
        # 分词处理
        keywords = jieba.cut(query)
        
        # 构建基础查询
        base_query = self.db.query(ProductDB)
        
        # 关键词过滤
        keyword_filters = []
        for keyword in keywords:
            keyword_filters.append(ProductDB.name.ilike(f"%{keyword}%"))
            keyword_filters.append(ProductDB.description.ilike(f"%{keyword}%"))
        
        base_query = base_query.filter(or_(*keyword_filters))
        
        # 应用其他过滤条件
        if category:
            base_query = base_query.filter(ProductDB.category == category)
        if min_price is not None:
            base_query = base_query.filter(ProductDB.price >= min_price)
        if max_price is not None:
            base_query = base_query.filter(ProductDB.price <= max_price)
        if platform:
            base_query = base_query.filter(ProductDB.platform == platform)
            
        return base_query.all() 