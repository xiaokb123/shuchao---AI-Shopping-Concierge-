# 数潮智能购物助手

## 演示视频
[![点击查看演示视频](https://via.placeholder.com/600x300?text=Demo+Video)](https://example.com/demo.mp4)

## 项目概述
数潮智能购物助手是基于 Flask 框架开发的 AI 导购系统，旨在根据用户的需求、预算以及购物偏好为用户推荐合适的商品。系统集成了大语言模型（如 OpenAI 的 GPT-3.5-turbo），支持用户通过对话获取专业的购物建议，并结合数据爬取、用户画像构建及论坛交流等模块，实现精准的商品推荐与消费预算管理。

## 核心功能
1. **AI 对话与推荐**  
   - 用户通过对话页面与 AI 进行交流，系统调用 OpenAI 接口返回详细的商品推荐和购物建议。
   - 示例相关代码见 [api/ai/routes.py](api/ai/routes.py)。

2. **商品推荐与评分计算**  
   - 系统基于用户输入的查询和意图，通过 `analyze_user_intent` 分析用户需求，并结合价格、品牌、功能匹配度等因素计算商品推荐分数（参见 [api/utils/ai_utils.py](api/utils/ai_utils.py) 和 [api/utils/recommendation.py](api/utils/recommendation.py)）。
   - 同时，通过 [api/ai/recommendation.py](api/ai/recommendation.py) 中的 `SmartRecommender` 实现智能商品推荐。

3. **商品信息爬取**  
   - 使用异步爬虫（aiohttp、asyncio）从京东、淘宝、拼多多等平台批量获取商品信息。
   - 相关代码示例：
   ```python
   class ProductSpider:
       def __init__(self):
           self.platforms = {
               'jd': 'https://api.jd.com/...',
               'taobao': 'https://api.taobao.com/...',
               'pinduoduo': 'https://api.pinduoduo.com/...'
           }
       
       async def crawl_all_platforms(self):
           """并发爬取所有平台数据"""
           tasks = []
           async with aiohttp.ClientSession() as session:
               for platform, url in self.platforms.items():
                   task = asyncio.create_task(
                       self.crawl_platform(session, platform, url)
                   )
                   tasks.append(task)
               await asyncio.gather(*tasks)
   ```
   
4. **用户画像构建与行为分析**  
   - 收集用户的浏览历史、购买记录以及论坛活动，利用 TF-IDF、K-Means 聚类等算法生成用户画像和偏好数据（参见 [api/analytics/user_preferences.py](api/analytics/user_preferences.py) 和 [api/ai/advanced_ai.py](api/ai/advanced_ai.py)）。
   
5. **购物预算管理**  
   - 用户可以设置月度预算，在推荐过程中系统会确保推荐商品满足用户预算要求（相关预算信息在 [config.py](config.py) 中配置）。

6. **论坛功能**  
   - 用户可在平台上发布帖子、交流购物心得，系统通过帖子内容提取关键词更新用户购物偏好（代码见 [api/forum/routes.py](api/forum/routes.py)）。

7. **系统监控与报警**  
   - 通过 Prometheus 度量关键指标，并结合钉钉、邮件等方式实时发送告警（参见 [api/monitor/advanced_monitoring.py](api/monitor/advanced_monitoring.py)）。

## 数据需求
系统涉及的数据主要包括以下几类：
- **用户数据**：存储用户基本信息、登录状态、购物预算、用户画像（[api/models.py](api/models.py)、[api/models/user.py](api/models/user.py)）。
- **商品数据**：包括商品名称、描述、价格、品牌、规格、销量、评分、历史价格等。
- **聊天记录与推荐记录**：记录用户与 AI 的交互日志、推荐理由、评分与用户反馈。
- **爬虫任务数据**：保存各平台爬取的商品信息及爬虫任务状态日志。
- **论坛数据**：包括帖子、评论、用户偏好记录等信息。

## 数据库设计
数据库采用 MySQL，并使用 SQLAlchemy 作为 ORM 层。表与表之间通过用户 ID、商品 ID、聊天会话 ID 等字段建立关联关系。

下面是部分数据库表结构的示例（具体 SQL 见 `create_tables.py`）：

```sql
CREATE TABLE ai_recommendation_records (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    message_id INT,
    product_id INT NOT NULL,
    score FLOAT,
    reason TEXT,
    features JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_feedback VARCHAR(20),
    feedback_time DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES chat_messages(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE budgets (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    spent DECIMAL(10,2) DEFAULT 0.0,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 系统架构
系统主要采用 Flask 作为 Web 框架，并按照功能模块划分多个 Blueprint：
- **Auth 模块**：用户认证与授权 ([api/routes/auth.py](api/routes/auth.py))。
- **AI 模块**：与 OpenAI API 对接，实现 AI 对话和商品推荐功能 ([api/ai/routes.py](api/ai/routes.py)、[api/utils/openai_helper.py](api/utils/openai_helper.py))。
- **产品模块**：商品搜索、展示与推荐 ([api/routes/products.py](api/routes/products.py)、[api/utils/product_helper.py](api/utils/product_helper.py))。
- **论坛模块**：论坛帖子创建与管理 ([api/forum/routes.py](api/forum/routes.py))。
- **数据爬取与分析模块**：异步爬虫、用户画像分析、行为数据统计（详情参考 `api/crawler/spider.py`、`api/analytics/advanced_analytics.py`）。
- **监控模块**：系统及业务监控 ([api/monitor/advanced_monitoring.py](api/monitor/advanced_monitoring.py))。

此外，系统还集成了 Celery 定时任务（参见 [api/tasks.py](api/tasks.py)）用于用户偏好分析及其他周期性处理。

## 性能与安全要求
- **性能要求**  
  - 使用 Flask-Caching 和 Redis 缓存提高响应速度。  
  - 异步爬虫和 Celery 任务分离数据爬取与复杂计算任务。  
  - SQLAlchemy 配置连接池，合理控制最大连接数及溢出。

- **安全要求**  
  - CSRF 防护：使用 Flask-WTF、CSRF token 自动注入页面模板。  
  - 密码存储：采用 Werkzeug 密码散列存储用户密码。  
  - JWT 令牌：确保认证接口安全，并设置适当的过期时间。  
  - 数据库防注入：使用 ORM 层及参数化查询，防止 SQL 注入攻击。

## 数据爬取
数据爬取模块包括异步爬虫和实时价格追踪两个部分：
- **异步爬虫**：通过 `aiohttp` 和 `asyncio` 同时从多个电商平台（如京东、淘宝、拼多多）获取商品信息，解析数据后存入数据库（见 [services/crawler.py](services/crawler.py) 与 [api/crawler/spider.py](api/crawler/spider.py)）。
- **价格追踪**：使用 `PriceTracker` 类周期性更新商品价格，并记录价格历史（见 [api/monitor/price_tracker.py](api/monitor/price_tracker.py)）。

## 用户画像构建
系统通过采集用户的以下数据来构建用户画像：
- **浏览历史**：记录用户商品浏览记录加权分析兴趣类别。
- **购买历史**：统计用户交易记录，了解消费偏好。
- **论坛活动**：提取论坛帖子中的关键词更新用户兴趣（关键实现见 [api/forum/routes.py](api/forum/routes.py)）。
- **行为聚类**：利用 TF-IDF 特征提取及聚类算法，对用户行为数据进行分群（参见 [api/analytics/user_preferences.py](api/analytics/user_preferences.py)）。

## 商品推荐
商品推荐流程主要包括以下步骤：
1. **用户意图分析**  
   - 解析用户输入消息，提取预算、品牌、商品类别及功能特性（见 [api/utils/ai_utils.py](api/utils/ai_utils.py)）。

2. **AI 辅助推荐**  
   - 根据用户输入和上下文信息构建系统提示，并调用 OpenAI API 获取详细购物建议（见 [api/utils/openai_helper.py](api/utils/openai_helper.py)）。

3. **打分与排序**  
   - 通过 `calculate_product_score` 等函数计算每个候选商品的综合得分，结合 SmartRecommender 模块输出最终推荐结果（详见 [api/utils/recommendation.py](api/utils/recommendation.py) 与 [api/ai/recommendation.py](api/ai/recommendation.py)）。

## 论坛功能实现
论坛模块为用户提供了一个交流互动的平台，主要功能包括：
- **帖子创建与管理**  
  - 用户可以发表帖子，帖子内容中的关键词会被提取并用于更新用户购物偏好。
  - 示例代码参考 [api/forum/routes.py](api/forum/routes.py)。

- **内容搜索与筛选**  
  - 按分类、关键词搜索帖子，实现精准内容匹配。

## 项目总结
数潮智能购物助手通过整合 AI 对话、数据爬取、用户画像构建和智能推荐等多种技术，为用户提供个性化、专业的购物建议。同时系统充分考虑性能和安全性，利用 Flask 的生态系统（包括 SQLAlchemy、Celery、Redis、WTForms 等）实现了一个高效、可靠的电商智能导购平台。

本项目不仅为消费者提供了简化决策的信息服务，同时也为商家、平台运营者提供了丰富的用户行为和市场数据，具有广阔的应用前景。

## 参考文档
- [Flask官方文档](https://flask.palletsprojects.com/)
- [SQLAlchemy官方文档](https://docs.sqlalchemy.org/)
- [OpenAI API使用指南](https://platform.openai.com/docs/api-reference)
- [Celery官方文档](https://docs.celeryproject.org/) 