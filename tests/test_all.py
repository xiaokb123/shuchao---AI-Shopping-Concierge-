import unittest
from api import create_app
from api.models import db, User, Product, Budget
from datetime import datetime

class TestApp(unittest.TestCase):
    def setUp(self):
        """测试前设置"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        
        # 创建测试用户
        self.user = User(
            username='test_user',
            email='test@example.com'
        )
        self.user.set_password('password123')
        db.session.add(self.user)
        
        # 创建测试预算
        self.budget = Budget(
            user_id=1,
            category='books',
            amount=1000.0,
            start_date=datetime.now(),
            end_date=datetime.now()
        )
        db.session.add(self.budget)
        
        # 创建测试商品
        self.product = Product(
            name='测试商品',
            description='这是一个测试商品',
            current_price=99.9,
            original_price=199.9,
            platform='test_platform'
        )
        db.session.add(self.product)
        db.session.commit()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    
    def test_auth(self):
        """测试认证功能"""
        # 测试注册
        response = self.client.post('/auth/register', json={
            'username': 'new_user',
            'email': 'new@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        
        # 测试登录
        response = self.client.post('/auth/login', json={
            'username': 'new_user',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_budget(self):
        """测试预算功能"""
        # 登录
        self.client.post('/auth/login', json={
            'username': 'test_user',
            'password': 'password123'
        })
        
        # 测试创建预算
        response = self.client.post('/api/budget', json={
            'category': 'electronics',
            'amount': 5000.0,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        })
        self.assertEqual(response.status_code, 200)
        
        # 测试获取预算状态
        response = self.client.get('/api/budget/status')
        self.assertEqual(response.status_code, 200)
