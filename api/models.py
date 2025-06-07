from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Integer, String, DateTime, Boolean, Float, JSON, Text, ForeignKey, Column

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    reset_token = Column(String(100))  # 密码重置令牌
    reset_token_expiry = Column(DateTime)  # 令牌过期时间
    
    # 用户画像
    avatar_url = Column(String(500))  # 头像URL
    gender = Column(String(10))  # 性别
    age = Column(Integer)  # 年龄
    occupation = Column(String(50))  # 职业
    interests = Column(JSON)  # 兴趣爱好
    
    # 消费能力和预算
    monthly_budget = Column(Float, default=0.0)  # 月度预算
    total_spent = Column(Float, default=0.0)  # 总消费
    consumption_level = Column(String(20))  # 消费水平：低、中、高
    
    # 用户偏好
    preferences = Column(JSON)  # 通用偏好设置
    shopping_preferences = Column(JSON)  # 购物偏好
    price_sensitivity = Column(Float)  # 价格敏感度
    brand_preference = Column(JSON)  # 品牌偏好
    
    # 用户行为统计
    login_count = Column(Integer, default=0)  # 登录次数
    post_count = Column(Integer, default=0)  # 发帖数
    comment_count = Column(Integer, default=0)  # 评论数
    browse_count = Column(Integer, default=0)  # 浏览次数
    
    # 关联
    budgets = relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    forum_posts = relationship('ForumPost', backref='author', lazy=True, cascade='all, delete-orphan')
    purchase_history = relationship('PurchaseHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    browsing_history = relationship('BrowsingHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    user_preferences = relationship('UserPreference', backref='user', lazy=True, cascade='all, delete-orphan')
    ai_recommendations = relationship('AIRecommendation', 
                                    back_populates='user', 
                                    lazy=True,
                                    primaryjoin="User.id == AIRecommendation.user_id",
                                    foreign_keys="AIRecommendation.user_id")
    chat_sessions = relationship('ChatSession', backref='user', lazy=True)
    orders = relationship('Order', backref='user', lazy=True)
    reviews = relationship('Review', backref='user', lazy=True)

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('用户名不能为空')
        if len(username) < 3:
            raise ValueError('用户名长度必须大于3个字符')
        if len(username) > 80:
            raise ValueError('用户名长度不能超过80个字符')
        if not re.match('^[a-zA-Z0-9_-]+$', username):
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return username

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError('邮箱不能为空')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('邮箱格式不正确')
        if User.query.filter(User.email == email, User.id != self.id).first():
            raise ValueError('该邮箱已被注册')
        return email

    @validates('monthly_budget')
    def validate_monthly_budget(self, key, budget):
        if budget < 0:
            raise ValueError('预算不能为负数')
        return budget

    def set_password(self, password):
        """设置密码"""
        if not password:
            raise ValueError('密码不能为空')
        if len(password) < 8:
            raise ValueError('密码长度必须大于8个字符')
        if not re.search(r'[A-Z]', password):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', password):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', password):
            raise ValueError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError('密码必须包含至少一个特殊字符')
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        db.session.commit()

    def update_post_count(self):
        """更新发帖数"""
        self.post_count += 1
        db.session.commit()

    def update_comment_count(self):
        """更新评论数"""
        self.comment_count += 1
        db.session.commit()

    def update_browse_count(self):
        """更新浏览次数"""
        self.browse_count += 1
        db.session.commit()

    def update_consumption_level(self):
        """根据消费金额更新消费水平"""
        if self.total_spent < 1000:
            self.consumption_level = '低'
        elif self.total_spent < 5000:
            self.consumption_level = '中'
        else:
            self.consumption_level = '高'
        db.session.commit()

    def generate_reset_token(self):
        """生成密码重置令牌"""
        import secrets
        from datetime import timedelta
        
        # 生成随机令牌
        self.reset_token = secrets.token_urlsafe(32)
        # 设置令牌过期时间（24小时后）
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
        
        try:
            db.session.commit()
            return self.reset_token
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"生成重置令牌失败: {str(e)}")
    
    def verify_reset_token(self, token):
        """验证密码重置令牌"""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        
        if token != self.reset_token:
            return False
        
        if datetime.utcnow() > self.reset_token_expiry:
            # 清除过期的令牌
            self.reset_token = None
            self.reset_token_expiry = None
            db.session.commit()
            return False
        
        return True
    
    def reset_password(self, token, new_password):
        """重置密码"""
        if not self.verify_reset_token(token):
            raise ValueError('无效或已过期的重置令牌')
        
        try:
            # 设置新密码
            self.set_password(new_password)
            # 清除重置令牌
            self.reset_token = None
            self.reset_token_expiry = None
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"重置密码失败: {str(e)}")
    
    def clear_reset_token(self):
        """清除重置令牌"""
        self.reset_token = None
        self.reset_token_expiry = None
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    spent = Column(Float, default=0.0)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def is_exceeded(self):
        return self.spent > self.amount

class Product(db.Model):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    current_price = Column(Float, nullable=False)
    original_price = Column(Float)
    discount = Column(Float)
    stock = Column(Integer, default=0)
    sales_count = Column(Integer, default=0)
    rating = Column(Float)
    review_count = Column(Integer, default=0)
    platform = Column(String(50))
    platform_url = Column(String(500))
    brand = Column(String(100))
    category = Column(String(100))
    tags = Column(JSON)
    images = Column(JSON)
    specifications = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    reviews = relationship('Review', backref='product', lazy=True)
    price_alerts = relationship('PriceAlert', back_populates='product', lazy=True)
    browsing_history = relationship('BrowsingHistory', back_populates='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class ProductReview(db.Model):
    __tablename__ = 'product_reviews'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = Column(Float, nullable=False)
    content = Column(Text)
    pros = Column(Text)  # 优点
    cons = Column(Text)  # 缺点
    images = Column(JSON)  # 评论图片
    likes_count = Column(Integer, default=0)  # 点赞数
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    user = relationship('User', backref='product_reviews')
    
    @validates('rating')
    def validate_rating(self, key, rating):
        if rating < 0 or rating > 5:
            raise ValueError('评分必须在0-5之间')
        return rating

class PurchaseHistory(db.Model):
    __tablename__ = 'purchase_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    
    product = relationship('Product', backref='purchases')

class BrowsingHistory(db.Model):
    __tablename__ = 'browsing_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    view_time = Column(DateTime, default=datetime.utcnow)
    
    product = relationship('Product', back_populates='browsing_history')

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 帖子类型（普通帖子、商品评测、求推荐等）
    post_type = Column(String(20), default='normal')
    
    # 关联的商品（如果是商品评测或推荐）
    product_id = Column(Integer, ForeignKey('products.id', ondelete='SET NULL'))
    
    # 关联
    comments = relationship('ForumComment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = relationship('ForumLike', backref='post', lazy=True, cascade='all, delete-orphan')

class ForumComment(db.Model):
    __tablename__ = 'forum_comments'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('forum_posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship('User', backref='comments')

class ForumLike(db.Model):
    __tablename__ = 'forum_likes'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('forum_posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category = Column(String(50), nullable=False)
    weight = Column(Float, default=1.0)  # 用户对该类别的偏好程度
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIRecommendation(db.Model):
    __tablename__ = 'ai_recommendations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message_id = Column(Integer, ForeignKey('chat_messages.id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    score = Column(Float)  # 推荐分数
    reason = Column(Text)  # 推荐原因
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship('User', back_populates='ai_recommendations')
    product = relationship('Product', backref='ai_recommendations', overlaps="recommendations,recommended_product")
    
    def __repr__(self):
        return f'<AIRecommendation {self.id}>'

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    feedback_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    contact = Column(String(120))
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship('User', backref='feedbacks')

    def __repr__(self):
        return f'<Feedback {self.id}>'

class CrawlerTask(db.Model):
    __tablename__ = 'crawler_tasks'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)  # 目标平台
    keywords = Column(JSON, nullable=False)  # 搜索关键词
    category = Column(String(50))  # 商品类别
    price_range = Column(JSON)  # 价格区间
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    priority = Column(Integer, default=0)  # 任务优先级
    max_items = Column(Integer, default=100)  # 最大爬取商品数
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)  # 开始时间
    completed_at = Column(DateTime)  # 完成时间
    error_message = Column(Text)  # 错误信息
    
    # 爬虫配置
    config = Column(JSON)  # 爬虫配置参数
    proxy = Column(String(200))  # 代理设置
    headers = Column(JSON)  # 请求头设置
    
    # 统计信息
    total_items = Column(Integer, default=0)  # 已爬取商品数
    success_count = Column(Integer, default=0)  # 成功数
    failure_count = Column(Integer, default=0)  # 失败数
    
    # 关联
    logs = relationship('CrawlerLog', backref='task', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CrawlerTask {self.platform}:{self.keywords}>'

class CrawlerLog(db.Model):
    __tablename__ = 'crawler_logs'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('crawler_tasks.id', ondelete='CASCADE'), nullable=False)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    details = Column(JSON)  # 详细信息
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CrawlerLog {self.level}:{self.message[:50]}>'

class PriceAlert(db.Model):
    __tablename__ = 'price_alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    target_price = Column(Float, nullable=False)  # 目标价格
    status = Column(String(20), default='active')  # active, triggered, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime)  # 触发时间
    
    # 关联
    user = relationship('User', backref='price_alerts')
    product = relationship('Product', back_populates='price_alerts')
    
    def __repr__(self):
        return f'<PriceAlert {self.product.name}:{self.target_price}>'

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(100))  # 会话标题
    status = Column(String(20), default='active')  # active, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 会话配置
    config = Column(JSON)  # 会话配置参数
    context = Column(JSON)  # 会话上下文
    
    # 统计信息
    message_count = Column(Integer, default=0)  # 消息数量
    
    # 关联
    messages = relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan', order_by='ChatMessage.created_at')
    
    def __repr__(self):
        return f'<ChatSession {self.id}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 消息处理
    tokens = Column(Integer)  # token数量
    processing_time = Column(Float)  # 处理时间（秒）
    
    # 推荐信息
    recommendations_data = Column(JSON)  # 推荐的商品信息
    crawler_keywords = Column(JSON)  # 生成的爬虫关键词
    
    # 关系
    ai_recommendations = relationship('AIRecommendation', backref='source_message', lazy=True)
    
    def __repr__(self):
        return f'<ChatMessage {self.role}:{self.content[:50]}>'

class AIRecommendationRecord(db.Model):
    __tablename__ = 'ai_recommendation_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message_id = Column(Integer, ForeignKey('chat_messages.id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    
    # 推荐信息
    score = Column(Float)  # 推荐分数
    reason = Column(Text)  # 推荐原因
    features = Column(JSON)  # 特征匹配
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 用户反馈
    user_feedback = Column(String(20))  # positive, negative, neutral
    feedback_time = Column(DateTime)
    
    # 简化关系定义
    user = relationship('User', backref='recommendation_records')
    product = relationship('Product', backref='recommendation_records')
    message = relationship('ChatMessage', backref='recommendations_made')
    
    def __repr__(self):
        return f'<AIRecommendationRecord {self.product.name}:{self.score}>'

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserBehavior(db.Model):
    __tablename__ = 'user_behaviors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    # ... 其他字段定义