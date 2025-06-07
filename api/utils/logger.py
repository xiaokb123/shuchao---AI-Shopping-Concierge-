import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
from datetime import datetime

def setup_logger(app):
    """配置日志系统"""
    # 创建日志目录
    log_dir = app.config.get('LOG_DIR', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 通用日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # 错误日志文件处理器 - 按大小轮转
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=app.config.get('LOG_MAX_BYTES', 10 * 1024 * 1024),  # 默认10MB
        backupCount=app.config.get('LOG_BACKUP_COUNT', 30)
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # 普通日志文件处理器 - 按时间轮转
    info_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        when='midnight',  # 每天午夜轮转
        interval=1,
        backupCount=app.config.get('LOG_DAYS_KEEP', 30),  # 保留30天的日志
        encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    
    # 调试日志文件处理器
    debug_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'debug.log'),
        when='midnight',
        interval=1,
        backupCount=7,  # 保留7天的调试日志
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_level = logging.DEBUG if app.debug else logging.INFO
    console_handler.setLevel(console_level)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 设置为最低级别，让处理器决定要记录什么
    
    # 清除现有的处理器
    root_logger.handlers = []
    
    # 添加所有处理器
    root_logger.addHandler(error_handler)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(debug_handler)
    root_logger.addHandler(console_handler)
    
    # 配置Flask应用日志记录器
    app.logger.setLevel(logging.DEBUG)
    # 清除默认处理器
    app.logger.handlers = []
    for handler in root_logger.handlers:
        app.logger.addHandler(handler)
    
    # 设置其他模块的日志级别
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # 记录应用启动信息
    app.logger.info('='*50)
    app.logger.info(f'数潮应用启动 - 环境: {app.config.get("FLASK_ENV", "production")}')
    app.logger.info(f'启动时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    app.logger.info('='*50)