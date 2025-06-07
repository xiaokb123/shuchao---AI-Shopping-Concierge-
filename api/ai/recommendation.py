import openai
from api.models import db, Product, UserPreference
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import json
import os

class AIChatProcessor:
    """AI对话处理器"""
    def __init__(self, openai_client):
        self.chat_history = []
        self.openai_client = openai_client
        self.system_prompt = """你是一个智能购物助手，具有以下能力：
        1. 理解用户购物需求并提供商品推荐
        2. 解释推荐策略和算法决策过程
        3. 进行自然流畅的中文对话
        4. 结合用户历史偏好进行个性化推荐
        5. 处理价格咨询、商品比较等常见问题"""
    
    def generate_recommendation_reason(self, product, context):
        """使用LLM生成推荐理由（增加异常处理）"""
        try:
            prompt = f"""基于以下信息为商品生成推荐理由：
            商品名称：{product.name}
            商品特点：{product.features}
            用户上下文：{context}
            返回格式：简洁的2句话说明，使用口语化中文"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"推荐理由生成失败: {str(e)}")
            return "该商品符合您的需求"

    def process_user_input(self, text):
        """处理自然语言输入（增加异常处理）"""
        try:
            prompt = f"""分析用户需求：
            {text}
            提取以下JSON格式：
            {{"preference_tags": ["标签1", "标签2"], 
            "budget_range": [最小值, 最大值],
            "special_requirements": "需求描述"}}"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"输入解析失败: {str(e)}")
            return {"preference_tags": [], "budget_range": [0, 1000], "special_requirements": ""}

    def chat_response(self, user_message):
        """优化对话接口"""
        try:
            self.chat_history.append({"role": "user", "content": user_message})
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.chat_history[-6:]
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_reply = response.choices[0].message.content
            self.chat_history.append({"role": "assistant", "content": ai_reply})
            return ai_reply
            
        except Exception as e:
            return f"对话服务暂时不可用，请稍后再试。错误信息：{str(e)}"

class SmartRecommender:
    def __init__(self, user_id):
        self.user_id = user_id
        self.scaler = MinMaxScaler()
        self.chat_processor = AIChatProcessor(
            openai_client=openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        )
    
    def get_recommendations(self, context=None, user_input=None):
        """增强版智能推荐"""
        # 解析自然语言输入
        if user_input:
            parsed_input = self.chat_processor.process_user_input(user_input)
            context = self._update_context(context, parsed_input)
        
        # 获取用户偏好
        preferences = self._get_user_preferences()
        
        # 获取预算信息
        budget = self._get_user_budget()
        
        # 获取候选商品
        candidates = self._get_candidate_products(preferences)
        
        # 计算综合得分
        scores = self._calculate_scores(candidates, preferences, budget)
        
        # 返回最佳推荐
        final_recommendations = self._get_top_recommendations(candidates, scores)
        return self._add_ai_explanations(final_recommendations, context)
    
    def _calculate_scores(self, candidates, preferences, budget):
        """计算商品综合得分"""
        scores = np.zeros(len(candidates))
        
        # 相关度得分
        relevance_scores = self._calculate_relevance(candidates, preferences)
        
        # 性价比得分
        value_scores = self._calculate_value_for_money(candidates)
        
        # 预算适配度
        budget_scores = self._calculate_budget_fit(candidates, budget)
        
        # 加权合并得分
        weights = [0.4, 0.3, 0.3]  # 权重可调
        scores = (
            weights[0] * relevance_scores +
            weights[1] * value_scores +
            weights[2] * budget_scores
        )
        
        return scores
    
    def _add_ai_explanations(self, recommendations, context):
        """为每个推荐添加AI生成的解释"""
        for product in recommendations:
            product.ai_reason = self.chat_processor.generate_recommendation_reason(product, context)
        return recommendations
    
    def chat(self, message):
        """增强版对话接口"""
        return self.chat_processor.chat_response(message)
    
    def get_dialog_history(self):
        """获取完整对话历史"""
        return self.chat_processor.chat_history
    
    def clear_dialog_history(self):
        """清空对话历史"""
        self.chat_processor.chat_history = []