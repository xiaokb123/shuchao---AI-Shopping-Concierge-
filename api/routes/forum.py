from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from api.models import db, ForumPost, ForumComment, ForumLike, User
from datetime import datetime

forum_bp = Blueprint('forum', __name__)

@forum_bp.app_template_filter('time_ago')
def time_ago_filter(date):
    """计算时间差"""
    now = datetime.utcnow()
    diff = now - date
    
    if diff.days > 365:
        return f"{diff.days // 365}年前"
    if diff.days > 30:
        return f"{diff.days // 30}个月前"
    if diff.days > 0:
        return f"{diff.days}天前"
    if diff.seconds > 3600:
        return f"{diff.seconds // 3600}小时前"
    if diff.seconds > 60:
        return f"{diff.seconds // 60}分钟前"
    return "刚刚"

@forum_bp.route('/')
def index():
    """论坛首页"""
    page = request.args.get('page', 1, type=int)
    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('forum/index.html', posts=posts)

@forum_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    """帖子详情页"""
    post = ForumPost.query.get_or_404(post_id)
    return render_template('forum/post_detail.html', post=post)

@forum_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """创建新帖子"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        post_type = request.form.get('type', 'discussion')
        
        if not title or not content:
            flash('标题和内容不能为空', 'error')
            return redirect(url_for('forum.create_post'))
            
        post = ForumPost(
            title=title,
            content=content,
            post_type=post_type,
            user_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('发帖成功', 'success')
        return redirect(url_for('forum.post_detail', post_id=post.id))
        
    return render_template('forum/create_post.html')

@forum_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """添加评论"""
    post = ForumPost.query.get_or_404(post_id)
    content = request.form.get('content')
    
    if not content:
        return jsonify({'error': '评论内容不能为空'}), 400
        
    comment = ForumComment(
        content=content,
        post_id=post_id,
        user_id=current_user.id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'user': comment.user.username,
        'created_at': time_ago_filter(comment.created_at)
    })

@forum_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    """点赞/取消点赞"""
    post = ForumPost.query.get_or_404(post_id)
    like = ForumLike.query.filter_by(
        post_id=post_id,
        user_id=current_user.id
    ).first()
    
    if like:
        db.session.delete(like)
        action = 'unliked'
    else:
        like = ForumLike(post_id=post_id, user_id=current_user.id)
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    
    return jsonify({
        'action': action,
        'likes_count': post.likes.count()
    })

@forum_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """编辑帖子"""
    post = ForumPost.query.get_or_404(post_id)
    
    # 检查权限
    if post.user_id != current_user.id:
        flash('您没有权限编辑这篇帖子', 'error')
        return redirect(url_for('forum.post_detail', post_id=post_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        post_type = request.form.get('type', post.post_type)
        
        if not title or not content:
            flash('标题和内容不能为空', 'error')
            return render_template('forum/edit_post.html', post=post)
            
        post.title = title
        post.content = content
        post.post_type = post_type
        post.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('帖子更新成功', 'success')
        return redirect(url_for('forum.post_detail', post_id=post.id))
        
    return render_template('forum/edit_post.html', post=post) 