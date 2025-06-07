from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found'}), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
        
    @app.errorhandler(429)
    def ratelimit_error(error):
        return jsonify({'error': 'Too many requests'}), 429 