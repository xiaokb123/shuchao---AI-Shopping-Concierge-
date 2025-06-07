from api import create_app
from api.models import db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def reset_database():
    """重置数据库"""
    app = create_app()
    with app.app_context():
        try:
            print("开始重置数据库...")
            
            # 删除所有表
            print("删除所有表...")
            db.drop_all()
            
            # 创建所有表
            print("创建所有表...")
            db.create_all()
            
            # 创建测试用户
            print("创建测试用户...")
            test_user = User(
                username='test',
                email='test@example.com',
                password_hash=generate_password_hash('test123'),
                created_at=datetime.utcnow(),
                is_active=True
            )
            db.session.add(test_user)
            
            # 创建管理员用户
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                created_at=datetime.utcnow(),
                is_active=True
            )
            db.session.add(admin_user)
            
            # 提交更改
            db.session.commit()
            print("数据库重置完成！")
            
        except Exception as e:
            print(f"重置数据库时出错: {str(e)}")
            db.session.rollback()
            raise e

if __name__ == '__main__':
    reset_database() 