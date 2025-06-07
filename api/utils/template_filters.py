from datetime import datetime

def time_ago(dt):
    """将datetime转换为"多久之前"的格式"""
    if not dt:
        return ''
        
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    if seconds < 60:
        return '刚刚'
    
    minutes = seconds // 60
    if minutes < 60:
        return f'{int(minutes)}分钟前'
    
    hours = minutes // 60
    if hours < 24:
        return f'{int(hours)}小时前'
    
    days = diff.days
    if days < 30:
        return f'{days}天前'
    
    months = days // 30
    if months < 12:
        return f'{int(months)}个月前'
    
    years = days // 365
    return f'{int(years)}年前'

def post_type_text(post_type):
    """将帖子类型转换为显示文本"""
    type_map = {
        'normal': '普通帖子',
        'review': '商品评测',
        'question': '求推荐',
        'discussion': '讨论'
    }
    return type_map.get(post_type, post_type)

def post_type_color(post_type):
    """将帖子类型转换为对应的颜色类"""
    color_map = {
        'normal': 'secondary',
        'review': 'primary',
        'question': 'success',
        'discussion': 'info'
    }
    return color_map.get(post_type, 'secondary') 