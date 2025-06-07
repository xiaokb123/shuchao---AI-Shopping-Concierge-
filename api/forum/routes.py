from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from api.models import db, ForumPost, ForumComment, ForumLike, UserPreference
from datetime import datetime
from . import forum_bp

@forum_bp.route('/')
def index():
    """论坛首页，重定向到帖子列表"""
    return redirect(url_for('forum.list_posts'))

@forum_bp.route('/posts')
def list_posts():
    """论坛帖子列表"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    
    query = ForumPost.query.order_by(ForumPost.created_at.desc())
    if category:
        query = query.filter_by(category=category)
    
    posts = query.paginate(page=page, per_page=20)
    
    return render_template('forum/index.html', posts=posts)

@forum_bp.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    """创建帖子"""
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    try:
        post = ForumPost(
            user_id=current_user.id,
            title=data.get('title'),
            content=data.get('content'),
            category=data.get('category'),
            product_id=data.get('product_id')
        )

        # 提取帖子中的关键词作为用户偏好
        keywords = extract_keywords(data.get('content', ''))
        for keyword in keywords:
            preference = UserPreference(
                user_id=current_user.id,
                keyword=keyword,
                weight=1.0,
                source='forum_post'
            )
            db.session.add(preference)

        db.session.add(post)
        db.session.commit()

        return jsonify({'message': '发布成功', 'post_id': post.id})
    except Exception as e:
        return jsonify({'error': '发帖失败：' + str(e)}), 400

def extract_keywords(text):
    """提取文本中的关键词"""
    import jieba.analyse
    return jieba.analyse.extract_tags(text, topK=5)

@forum_bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'], endpoint='edit_post')
@login_required
def edit_post(post_id):
    """编辑帖子（暂未实现，仅为避免路由错误）"""
    return "编辑功能暂未实现", 200