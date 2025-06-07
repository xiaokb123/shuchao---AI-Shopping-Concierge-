from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

class BusinessError(Exception):
    """业务逻辑错误"""
    def __init__(self, message, code=400):
        self.message = message
        self.code = code
        super().__init__(message)

class ResourceNotFoundError(BusinessError):
    """资源未找到错误"""
    def __init__(self, message="请求的资源不存在"):
        super().__init__(message, 404)

class ValidationError(BusinessError):
    """数据验证错误"""
    def __init__(self, message="数据验证失败"):
        super().__init__(message, 400)

def init_error_handlers(app):
    """初始化错误处理"""
    
    # Sentry集成
    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            environment=app.config.get('FLASK_ENV', 'production')
        )

    @app.errorhandler(Exception)
    def handle_exception(e):
        """处理所有异常"""
        if isinstance(e, BusinessError):
            response = {
                'error': e.__class__.__name__,
                'message': e.message,
                'code': e.code
            }
            return jsonify(response), e.code
            
        if isinstance(e, HTTPException):
            response = {
                'error': e.name,
                'message': e.description,
                'code': e.code
            }
            return jsonify(response), e.code
        
        # 记录未知错误
        current_app.logger.error(f"未知错误: {str(e)}", exc_info=True)
        if app.config.get('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)
        
        if app.debug:
            # 在开发环境返回详细错误信息
            response = {
                'error': 'Internal Server Error',
                'message': str(e),
                'type': e.__class__.__name__,
                'code': 500
            }
        else:
            # 在生产环境返回通用错误信息
            response = {
                'error': 'Internal Server Error',
                'message': '服务器内部错误',
                'code': 500
            }
        return jsonify(response), 500

    @app.errorhandler(404)
    def handle_404(e):
        """处理404错误"""
        return jsonify({
            'error': 'Not Found',
            'message': '请求的资源不存在',
            'code': 404
        }), 404

    @app.errorhandler(400)
    def handle_400(e):
        """处理400错误"""
        return jsonify({
            'error': 'Bad Request',
            'message': '请求参数错误',
            'code': 400
        }), 400

    @app.errorhandler(401)
    def handle_401(e):
        """处理401错误"""
        return jsonify({
            'error': 'Unauthorized',
            'message': '请先登录',
            'code': 401
        }), 401

    @app.errorhandler(403)
    def handle_403(e):
        """处理403错误"""
        return jsonify({
            'error': 'Forbidden',
            'message': '没有权限执行此操作',
            'code': 403
        }), 403

    @app.errorhandler(429)
    def handle_rate_limit(e):
        """处理速率限制错误"""
        return jsonify({
            'error': 'Too Many Requests',
            'message': '请求过于频繁，请稍后再试',
            'code': 429
        }), 429