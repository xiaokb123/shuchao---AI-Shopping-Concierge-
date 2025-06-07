import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
from ..models import db, CrawlerTask, CrawlerLog, Product

async def fetch_page(session, url, headers=None):
    """异步获取页面内容"""
    try:
        async with session.get(url, headers=headers) as response:
            return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def crawl_jd(keywords, max_items=10):
    """爬取京东商品信息"""
    products = []
    base_url = "https://search.jd.com/Search"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        for keyword in keywords:
            url = f"{base_url}?keyword={keyword}&enc=utf-8"
            html = await fetch_page(session, url, headers)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.select('.gl-item')
                
                for item in items[:max_items]:
                    try:
                        product = {
                            'platform': '京东',
                            'name': item.select_one('.p-name em').text.strip(),
                            'current_price': float(item.select_one('.p-price strong').text.strip()),
                            'platform_url': f"https:{item.select_one('.p-name a')['href']}",
                            'platform_item_id': re.search(r'\d+', item.select_one('.p-name a')['href']).group(),
                            'images': [f"https:{item.select_one('.p-img img')['data-lazy-img']}"],
                            'seller_name': item.select_one('.p-shop a').text.strip() if item.select_one('.p-shop a') else None
                        }
                        products.append(product)
                    except Exception as e:
                        print(f"Error parsing JD item: {e}")
    
    return products

async def crawl_tmall(keywords, max_items=10):
    """爬取天猫商品信息"""
    products = []
    base_url = "https://list.tmall.com/search_product.htm"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        for keyword in keywords:
            url = f"{base_url}?q={keyword}"
            html = await fetch_page(session, url, headers)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.select('.product')
                
                for item in items[:max_items]:
                    try:
                        product = {
                            'platform': '天猫',
                            'name': item.select_one('.productTitle a').text.strip(),
                            'current_price': float(item.select_one('.productPrice em').text.strip()),
                            'platform_url': f"https:{item.select_one('.productTitle a')['href']}",
                            'platform_item_id': re.search(r'id=(\d+)', item.select_one('.productTitle a')['href']).group(1),
                            'images': [f"https:{item.select_one('.productImg-wrap img')['src']}"],
                            'seller_name': item.select_one('.productShop a').text.strip() if item.select_one('.productShop a') else None
                        }
                        products.append(product)
                    except Exception as e:
                        print(f"Error parsing Tmall item: {e}")
    
    return products

def create_crawler_task(keywords):
    """创建并执行爬虫任务"""
    try:
        # 创建爬虫任务记录
        task = CrawlerTask(
            platform='all',  # 爬取所有支持的平台
            keywords=keywords,
            status='running',
            priority=1,
            max_items=10,
            config={
                'platforms': ['jd', 'tmall'],
                'timeout': 30,
                'retry': 3
            },
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        db.session.add(task)
        db.session.commit()
        
        # 开始爬取
        products = asyncio.run(crawl_products(keywords, task))
        
        # 更新任务状态
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
        task.total_items = len(products)
        task.success_count = len(products)
        db.session.commit()
        
        # 保存商品信息到数据库
        save_products(products, task)
        
        return task
        
    except Exception as e:
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            db.session.commit()
            
            # 记录错误日志
            log = CrawlerLog(
                task_id=task.id,
                level='ERROR',
                message=f"爬虫任务失败: {str(e)}",
                details={
                    'keywords': keywords,
                    'error': str(e)
                }
            )
            db.session.add(log)
            db.session.commit()
        
        raise e

async def crawl_products(keywords, task):
    """执行商品爬取"""
    all_products = []
    
    # 并发爬取各平台
    tasks = []
    if 'jd' in task.config['platforms']:
        tasks.append(crawl_jd(keywords, task.max_items))
    if 'tmall' in task.config['platforms']:
        tasks.append(crawl_tmall(keywords, task.max_items))
    
    # 等待所有爬虫任务完成
    results = await asyncio.gather(*tasks)
    
    # 合并结果
    for platform_products in results:
        all_products.extend(platform_products)
    
    return all_products

def save_products(products, task):
    """保存爬取到的商品信息"""
    for product_data in products:
        # 检查商品是否已存在
        existing = Product.query.filter_by(
            platform=product_data['platform'],
            platform_item_id=product_data['platform_item_id']
        ).first()
        
        if existing:
            # 更新现有商品信息
            existing.name = product_data['name']
            existing.current_price = product_data['current_price']
            existing.platform_url = product_data['platform_url']
            existing.images = product_data['images']
            existing.seller_name = product_data['seller_name']
            existing.last_crawled_at = datetime.utcnow()
            
            # 更新价格历史
            existing.update_price_history(product_data['current_price'])
            
        else:
            # 创建新商品记录
            product = Product(
                name=product_data['name'],
                current_price=product_data['current_price'],
                platform=product_data['platform'],
                platform_url=product_data['platform_url'],
                platform_item_id=product_data['platform_item_id'],
                images=product_data['images'],
                seller_name=product_data['seller_name'],
                price_history=[{
                    'price': product_data['current_price'],
                    'timestamp': datetime.utcnow().isoformat()
                }],
                lowest_price=product_data['current_price'],
                highest_price=product_data['current_price'],
                last_crawled_at=datetime.utcnow()
            )
            db.session.add(product)
    
    # 提交所有更改
    db.session.commit() 