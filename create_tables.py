from api.app import app, db
from sqlalchemy import text
import pymysql

def create_database():
    try:
        # 连接到MySQL服务器（不指定数据库）
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456'
        )
        
        # 创建游标
        cursor = conn.cursor()
        
        # 删除数据库（如果存在）
        cursor.execute("DROP DATABASE IF EXISTS shuchao")
        
        # 创建数据库
        cursor.execute("CREATE DATABASE shuchao CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print("数据库创建成功！")
        
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        raise

def create_tables():
    try:
        # 先创建数据库
        create_database()
        
        # 连接到新创建的数据库
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='shuchao',
            charset='utf8mb4'
        )
        
        # 创建游标
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE users (
                id INT NOT NULL AUTO_INCREMENT,
                username VARCHAR(80) NOT NULL,
                email VARCHAR(120) NOT NULL,
                password_hash VARCHAR(256),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_active TINYINT(1) DEFAULT 1,
                avatar_url VARCHAR(500),
                gender VARCHAR(10),
                age INT,
                occupation VARCHAR(50),
                interests JSON,
                monthly_budget DECIMAL(10,2) DEFAULT 0.0,
                total_spent DECIMAL(10,2) DEFAULT 0.0,
                consumption_level VARCHAR(20),
                preferences JSON,
                shopping_preferences JSON,
                price_sensitivity FLOAT,
                brand_preference JSON,
                login_count INT DEFAULT 0,
                post_count INT DEFAULT 0,
                comment_count INT DEFAULT 0,
                browse_count INT DEFAULT 0,
                PRIMARY KEY (id),
                UNIQUE KEY unique_username (username),
                UNIQUE KEY unique_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建商品表
        cursor.execute('''
            CREATE TABLE products (
                id INT NOT NULL AUTO_INCREMENT,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(50),
                original_price DECIMAL(10,2),
                current_price DECIMAL(10,2),
                price_history JSON,
                lowest_price DECIMAL(10,2),
                highest_price DECIMAL(10,2),
                platform VARCHAR(50),
                platform_url VARCHAR(500),
                platform_item_id VARCHAR(100),
                seller_id VARCHAR(100),
                seller_name VARCHAR(100),
                brand VARCHAR(100),
                model VARCHAR(100),
                specifications JSON,
                images JSON,
                discount_info VARCHAR(200),
                stock INT,
                sales_count INT DEFAULT 0,
                rating FLOAT DEFAULT 0.0,
                rating_count INT DEFAULT 0,
                keywords JSON,
                tags JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_crawled_at DATETIME,
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建商品评论表
        cursor.execute('''
            CREATE TABLE product_reviews (
                id INT NOT NULL AUTO_INCREMENT,
                product_id INT NOT NULL,
                user_id INT NOT NULL,
                rating FLOAT NOT NULL,
                content TEXT,
                pros TEXT,
                cons TEXT,
                images JSON,
                likes_count INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建爬虫任务表
        cursor.execute('''
            CREATE TABLE crawler_tasks (
                id INT NOT NULL AUTO_INCREMENT,
                platform VARCHAR(50) NOT NULL,
                keywords JSON NOT NULL,
                category VARCHAR(50),
                price_range JSON,
                status VARCHAR(20) DEFAULT 'pending',
                priority INT DEFAULT 0,
                max_items INT DEFAULT 100,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                started_at DATETIME,
                completed_at DATETIME,
                error_message TEXT,
                config JSON,
                proxy VARCHAR(200),
                headers JSON,
                total_items INT DEFAULT 0,
                success_count INT DEFAULT 0,
                failure_count INT DEFAULT 0,
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建爬虫日志表
        cursor.execute('''
            CREATE TABLE crawler_logs (
                id INT NOT NULL AUTO_INCREMENT,
                task_id INT NOT NULL,
                level VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                details JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY (task_id) REFERENCES crawler_tasks(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建价格提醒表
        cursor.execute('''
            CREATE TABLE price_alerts (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                target_price DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                triggered_at DATETIME,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建聊天会话表
        cursor.execute('''
            CREATE TABLE chat_sessions (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                title VARCHAR(200),
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                config JSON,
                context JSON,
                message_count INT DEFAULT 0,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建聊天消息表
        cursor.execute('''
            CREATE TABLE chat_messages (
                id INT NOT NULL AUTO_INCREMENT,
                session_id INT NOT NULL,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                tokens INT,
                processing_time FLOAT,
                recommendations JSON,
                crawler_keywords JSON,
                PRIMARY KEY (id),
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建AI推荐记录表
        cursor.execute('''
            CREATE TABLE ai_recommendation_records (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                message_id INT,
                product_id INT NOT NULL,
                score FLOAT,
                reason TEXT,
                features JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_feedback VARCHAR(20),
                feedback_time DATETIME,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (message_id) REFERENCES chat_messages(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建预算表
        cursor.execute('''
            CREATE TABLE budgets (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                category VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                spent DECIMAL(10,2) DEFAULT 0.0,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建购买历史表
        cursor.execute('''
            CREATE TABLE purchase_history (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                quantity INT DEFAULT 1,
                purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建浏览历史表
        cursor.execute('''
            CREATE TABLE browsing_history (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                view_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建论坛帖子表
        cursor.execute('''
            CREATE TABLE forum_posts (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                post_type VARCHAR(20) DEFAULT 'normal',
                product_id INT,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建论坛评论表
        cursor.execute('''
            CREATE TABLE forum_comments (
                id INT NOT NULL AUTO_INCREMENT,
                post_id INT NOT NULL,
                user_id INT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建论坛点赞表
        cursor.execute('''
            CREATE TABLE forum_likes (
                id INT NOT NULL AUTO_INCREMENT,
                post_id INT NOT NULL,
                user_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建用户偏好表
        cursor.execute('''
            CREATE TABLE user_preferences (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                category VARCHAR(50) NOT NULL,
                weight DECIMAL(5,2) DEFAULT 1.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 创建反馈表
        cursor.execute('''
            CREATE TABLE feedback (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT,
                feedback_type VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                contact VARCHAR(120),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        
        # 提交更改
        conn.commit()
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print("所有数据库表创建成功！")
        
    except Exception as e:
        print(f"创建表时出错: {e}")
        raise

if __name__ == "__main__":
    create_tables() 