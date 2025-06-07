from prometheus_client import Counter, Histogram, Gauge
import psutil
import requests
from datetime import datetime

class AdvancedMonitoring:
    def __init__(self, app):
        self.app = app
        self.setup_metrics()
        
    def setup_metrics(self):
        """设置监控指标"""
        # 系统指标
        self.cpu_usage = Gauge('system_cpu_usage', 'CPU使用率')
        self.memory_usage = Gauge('system_memory_usage', '内存使用率')
        self.disk_usage = Gauge('system_disk_usage', '磁盘使用率')
        
        # 业务指标
        self.active_users = Gauge('business_active_users', '活跃用户数')
        self.sales_amount = Counter('business_sales_amount', '销售额')
        self.order_processing_time = Histogram(
            'business_order_processing_time',
            '订单处理时间'
        )
    
    def monitor_system_health(self):
        """监控系统健康状况"""
        # 更新系统指标
        self.cpu_usage.set(psutil.cpu_percent())
        self.memory_usage.set(psutil.virtual_memory().percent)
        self.disk_usage.set(psutil.disk_usage('/').percent)
        
        # 检查关键服务
        self._check_services()
        
        # 检查数据库连接
        self._check_database()
        
        # 检查缓存服务
        self._check_cache()
    
    def alert(self, message, level='warning'):
        """发送告警"""
        # 发送到钉钉
        self._send_dingtalk_alert(message, level)
        
        # 发送邮件
        self._send_email_alert(message, level)
        
        # 记录到日志
        self.app.logger.warning(f"告警: {message}")