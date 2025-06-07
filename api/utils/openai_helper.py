import os
import openai
from typing import Dict, Any, List

# 设置 OpenAI API 密钥
openai.api_key = os.environ.get('OPENAI_API_KEY') or 'your-api-key'

def get_ai_response(message: str, budget: float = None, context: list = None) -> Dict[str, Any]:
    """获取AI回复和商品推荐"""
    try:
        # 构建系统提示
        system_prompt = """你是一个专业的购物顾问，可以帮助用户选择合适的商品。
        你需要根据用户的需求、预算和历史对话上下文提供个性化的购物建议。
        每次回复都应该包含以下内容：
        1. 对用户需求的理解和分析
        2. 具体的商品推荐（考虑预算限制）
        3. 购买建议和注意事项
        4. 相关商品的比较分析
        请确保你的建议专业、客观，并始终考虑用户的最大利益。"""
        
        if budget:
            system_prompt += f"\n用户的预算是 {budget} 元，请确保推荐的商品总价不超过这个预算。"
        
        # 构建消息历史
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.extend(context[-5:])  # 保留最近5轮对话作为上下文
        messages.append({"role": "user", "content": message})
        
        # 调用 OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # 提取AI回复
        ai_message = response.choices[0].message.content
        
        # 提取推荐信息
        recommendations = extract_recommendations(ai_message)
        
        return {
            'message': ai_message,
            'recommendations': recommendations
        }
        
    except Exception as e:
        print(f"Error in get_ai_response: {str(e)}")
        return {
            'message': '抱歉，我现在无法处理您的请求。请稍后再试。',
            'recommendations': []
        }

def extract_recommendations(message: str) -> List[Dict[str, Any]]:
    """从AI回复中提取商品推荐信息"""
    recommendations = []
    
    try:
        # 使用更复杂的逻辑来提取推荐信息
        lines = message.split('\n')
        current_recommendation = None
        
        for line in lines:
            line = line.strip().lower()
            
            # 检查是否是新的推荐
            if any(keyword in line for keyword in ['推荐', '建议购买', '可以考虑']):
                if current_recommendation:
                    recommendations.append(current_recommendation)
                current_recommendation = {
                    'keywords': [],
                    'price_range': None,
                    'brand': None,
                    'category': None,
                    'features': [],
                    'reasons': []
                }
            
            if current_recommendation:
                # 提取价格范围
                if '价格' in line or '元' in line:
                    price_range = extract_price_range(line)
                    if price_range:
                        current_recommendation['price_range'] = price_range
                
                # 提取品牌
                if '品牌' in line or '牌子' in line:
                    brand = extract_brand(line)
                    if brand:
                        current_recommendation['brand'] = brand
                
                # 提取类别
                if '类型' in line or '种类' in line:
                    category = extract_category(line)
                    if category:
                        current_recommendation['category'] = category
                
                # 提取特征
                if '特点' in line or '功能' in line or '优势' in line:
                    features = line.split('：')[-1].split('，')
                    current_recommendation['features'].extend(features)
                
                # 提取推荐原因
                if '因为' in line or '原因' in line or '适合' in line:
                    reason = line.split('：')[-1]
                    current_recommendation['reasons'].append(reason)
                
                # 添加关键词
                keywords = [word for word in line.split() if len(word) > 1]
                current_recommendation['keywords'].extend(keywords)
        
        # 添加最后一个推荐
        if current_recommendation:
            recommendations.append(current_recommendation)
        
    except Exception as e:
        print(f"Error in extract_recommendations: {str(e)}")
    
    return recommendations

def extract_price_range(text: str) -> Dict[str, float]:
    """提取价格范围"""
    import re
    
    try:
        # 匹配价格范围，支持多种格式
        patterns = [
            r'(\d+(?:\.\d+)?)\s*[元¥]\s*[-~到至]\s*(\d+(?:\.\d+)?)\s*[元¥]',  # 100元-200元
            r'[元¥]?(\d+(?:\.\d+)?)\s*[-~到至]\s*[元¥]?(\d+(?:\.\d+)?)',      # 100-200
            r'(\d+(?:\.\d+)?)\s*[元¥].*?(\d+(?:\.\d+)?)\s*[元¥]'              # 100元左右到200元
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                min_price = float(match.group(1))
                max_price = float(match.group(2))
                return {
                    'min': min_price,
                    'max': max_price,
                    'average': (min_price + max_price) / 2
                }
        
        # 匹配单个价格
        single_price = re.search(r'(\d+(?:\.\d+)?)\s*[元¥]', text)
        if single_price:
            price = float(single_price.group(1))
            return {
                'min': price * 0.9,
                'max': price * 1.1,
                'average': price
            }
            
    except Exception as e:
        print(f"Error in extract_price_range: {str(e)}")
    
    return None

def extract_brand(text: str) -> str:
    """提取品牌信息"""
    import re
    
    try:
        # 匹配品牌信息
        patterns = [
            r'品牌[：:]\s*([^\s,，。]+)',
            r'牌子[：:]\s*([^\s,，。]+)',
            r'([a-zA-Z]+)[品牌牌子]',
            r'([^,，。\s]+)品牌'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
                
    except Exception as e:
        print(f"Error in extract_brand: {str(e)}")
    
    return None

def extract_category(text: str) -> str:
    """提取类别信息"""
    import re
    
    try:
        # 匹配类别信息
        patterns = [
            r'类[别型][：:]\s*([^\s,，。]+)',
            r'种类[：:]\s*([^\s,，。]+)',
            r'属于([^\s,，。]+)[类型]',
            r'([^,，。\s]+)[类型]商品'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
                
    except Exception as e:
        print(f"Error in extract_category: {str(e)}")
    
    return None 