import pymysql

def create_database():
    try:
        # 连接MySQL（不指定数据库）
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456'
        )
        
        # 创建cursor
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute("CREATE DATABASE IF NOT EXISTS shuchao CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        print("数据库创建成功！")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"创建数据库时出错: {e}")

if __name__ == "__main__":
    create_database() 