from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database_models import Base, UserDB, BudgetDB, ProductDB, ShoppingHistoryDB, UserBehavior, FeedbackDB

# 创建数据库引擎
DATABASE_URL = "mysql+pymysql://root:123456@localhost/shuchao"
engine = create_engine(DATABASE_URL)

def init_database():
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("所有数据库表创建成功！")
        
        # 创建会话
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 检查是否需要创建测试数据
        user_count = session.query(UserDB).count()
        if user_count == 0:
            print("数据库为空，正在创建测试数据...")
            # 这里可以添加测试数据的创建代码
            
        session.close()
        
    except Exception as e:
        print(f"初始化数据库时出错: {e}")

if __name__ == "__main__":
    init_database() 