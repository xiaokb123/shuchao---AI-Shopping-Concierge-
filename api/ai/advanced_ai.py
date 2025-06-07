from transformers import pipeline
import numpy as np
from sklearn.cluster import KMeans
from api.models import db, UserBehavior, Product
import torch
from openai import OpenAI
import os

class AdvancedAIRecommender:
    def __init__(self):
        # 配置OpenAI客户端
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # 加载预训练模型
        self.sentiment_analyzer = pipeline('sentiment-analysis')
        self.text_generator = pipeline('text-generation')
        self.image_classifier = pipeline('image-classification')
        
    def analyze_user_behavior(self, user_id):
        """深度分析用户行为"""
        behaviors = UserBehavior.query.filter_by(user_id=user_id).all()
        
        # 行为向量化
        behavior_vectors = []
        for behavior in behaviors:
            vector = self._vectorize_behavior(behavior)
            behavior_vectors.append(vector)
        
        # 使用K-means聚类分析用户兴趣
        kmeans = KMeans(n_clusters=5)
        clusters = kmeans.fit_predict(behavior_vectors)
        
        return self._generate_insights(clusters, behaviors)
    
    def generate_personalized_description(self, product, user_preferences):
        """已接入GPT-3.5生成个性化描述"""
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # 明确使用GPT-3.5模型
            messages=[
                {"role": "system", "content": "你是一个专业的商品描述生成助手。"},
                {"role": "user", "content": f"""
                基于以下信息生成个性化商品描述：
                商品: {product.name}
                原始描述: {product.description}
                用户偏好: {user_preferences}
                """}
            ]
        )
        return response.choices[0].message.content
    
    def predict_price_trends(self, product_id):
        """预测商品价格趋势"""
        from prophet import Prophet
        
        # 获取历史价格数据
        price_history = PriceHistory.query.filter_by(product_id=product_id).all()
        
        # 准备数据
        df = pd.DataFrame({
            'ds': [p.timestamp for p in price_history],
            'y': [p.price for p in price_history]
        })
        
        # 使用Prophet进行预测
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

class MultiModalRecommender:
    def __init__(self):
        # 配置OpenAI客户端
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.image_encoder = torch.hub.load('facebookresearch/dino:main', 'dino_vits16')
        self.text_encoder = torch.hub.load('huggingface/transformers', 'bert-base-chinese')
        
    def get_multimodal_recommendations(self, user_id, query=None, image=None):
        """多模态API接入"""
        try:
            if query:
                # 使用OpenAI进行文本嵌入
                response = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",  # 使用最新嵌入模型
                    input=query
                )
                query_embedding = response.data[0].embedding
            
            if image:
                # 使用OpenAI的DALL-E模型处理图像
                response = self.openai_client.images.create_variation(
                    image=image,  # DALL-E图像处理
                    size="256x256"
                )
                image_embedding = self._process_dalle_response(response)
            
            # 获取用户历史
            user_history = self._get_user_history(user_id)
            
            # 融合多模态特征
            combined_embedding = self._fusion_features(
                query_embedding,
                image_embedding,
                user_history
            )
            
            # 获取推荐
            recommendations = self._get_similar_products(combined_embedding)
            return recommendations
        except Exception as e:
            print(f"OpenAI API调用错误: {str(e)}")
            return []