from sqlalchemy import create_engine, text
from sqlalchemy.orm import joinedload
from functools import wraps
import time

class QueryOptimizer:
    def __init__(self, db):
        self.db = db
        self.query_stats = {}
    
    def optimize_query(self, query):
        """优化SQL查询"""
        # 添加必要的索引
        self._add_indexes(query)
        
        # 优化JOIN操作
        query = self._optimize_joins(query)
        
        # 添加查询缓存
        query = self._add_query_cache(query)
        
        return query
    
    def analyze_slow_queries(self):
        """分析慢查询"""
        slow_queries = self.db.session.execute(text("""
            SELECT query, calls, total_time, rows
            FROM pg_stat_statements
            ORDER BY total_time DESC
            LIMIT 10
        """))
        
        return [{
            'query': row[0],
            'calls': row[1],
            'total_time': row[2],
            'rows': row[3]
        } for row in slow_queries]
    
    def create_materialized_view(self, name, query):
        """创建物化视图"""
        self.db.session.execute(text(f"""
            CREATE MATERIALIZED VIEW {name} AS
            {query}
        """))
        self.db.session.commit()