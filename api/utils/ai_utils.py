import jieba
import jieba.analyse
from datetime import datetime
import re

def analyze_user_intent(message):
    """
    分析用户消息中的购物意图
    返回包含意图信息的字典
    """
    intent = {
        'type': 'search',  # search, compare, ask_detail
        'category': None,  # 商品类别
        'budget': None,    # 预算
        'brand': None,     # 品牌偏好
        'features': [],    # 期望功能/特性
        'concerns': []     # 关注点
    }
    
    # 提取预算信息
    budget_pattern = r'预算[在是]?(\d+)元'
    budget_match = re.search(budget_pattern, message)
    if budget_match:
        intent['budget'] = float(budget_match.group(1))
    
    # 提取品牌偏好
    brands = ['联想', '华为', '小米', '苹果', '戴尔', '惠普', '华硕']  # 示例品牌
    for brand in brands:
        if brand in message:
            intent['brand'] = brand
            break
    
    # 识别商品类别
    categories = {
        '笔记本': ['笔记本', '电脑', '笔记本电脑', '游戏本'],
        '手机': ['手机', '智能手机', '手机'],
        '平板': ['平板', '平板电脑', 'iPad'],
        '耳机': ['耳机', '耳麦', '降噪耳机']
    }
    
    for category, keywords in categories.items():
        if any(keyword in message for keyword in keywords):
            intent['category'] = category
            break
    
    # 识别功能特性
    features = {
        '性能': ['性能', '处理器', 'CPU', '显卡', 'GPU'],
        '续航': ['续航', '电池', '待机'],
        '屏幕': ['屏幕', '显示器', '分辨率'],
        '轻薄': ['轻薄', '便携', '重量'],
        '性价比': ['性价比', '划算', '实惠']
    }
    
    for feature, keywords in features.items():
        if any(keyword in message for keyword in keywords):
            intent['features'].append(feature)
    
    # 识别关注点
    concerns = {
        '价格': ['价格', '便宜', '贵', '实惠'],
        '质量': ['质量', '耐用', '可靠'],
        '外观': ['外观', '设计', '好看'],
        '售后': ['售后', '保修', '服务']
    }
    
    for concern, keywords in concerns.items():
        if any(keyword in message for keyword in keywords):
            intent['concerns'].append(concern)
    
    # 判断意图类型
    if '对比' in message or '比较' in message:
        intent['type'] = 'compare'
    elif any(word in message for word in ['怎么样', '如何', '区别', '优缺点']):
        intent['type'] = 'ask_detail'
    
    return intent

def extract_keywords(message, intent):
    """
    从用户消息中提取搜索关键词
    结合意图信息优化关键词
    """
    # 添加自定义词典
    custom_words = [
        '性价比', '游戏本', '轻薄本', '商务本', '设计本',
        '高性能', '长续航', '高分屏', '大内存', '固态硬盘'
    ]
    for word in custom_words:
        jieba.add_word(word)
    
    # 使用TextRank算法提取关键词
    keywords = jieba.analyse.textrank(
        message,
        topK=5,
        allowPOS=('n', 'v', 'a')  # 允许名词、动词、形容词
    )
    
    # 根据意图补充关键词
    if intent['category']:
        keywords.append(intent['category'])
    
    if intent['brand']:
        keywords.append(intent['brand'])
    
    if intent['features']:
        keywords.extend(intent['features'])
    
    # 去重
    keywords = list(set(keywords))
    
    # 构建搜索关键词组合
    search_keywords = []
    
    # 基础关键词（类别+品牌）
    base_keywords = []
    if intent['category']:
        base_keywords.append(intent['category'])
    if intent['brand']:
        base_keywords.append(intent['brand'])
    
    if base_keywords:
        search_keywords.append(' '.join(base_keywords))
    
    # 特性关键词
    for feature in intent['features']:
        if base_keywords:
            search_keywords.append(f"{' '.join(base_keywords)} {feature}")
        else:
            search_keywords.append(feature)
    
    # 其他关键词组合
    other_keywords = [k for k in keywords if k not in base_keywords and k not in intent['features']]
    for k in other_keywords:
        if base_keywords:
            search_keywords.append(f"{' '.join(base_keywords)} {k}")
        else:
            search_keywords.append(k)
    
    return search_keywords 