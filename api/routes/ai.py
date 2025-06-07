from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from datetime import datetime
from api.models import db, ChatSession, ChatMessage, AIRecommendation, Product
from api.utils.openai_helper import get_ai_response
from api.utils.product_helper import search_products
from sqlalchemy import desc
import jieba.analyse
import json

ai_bp = Blueprint('ai', __name__, template_folder='../templates/ai')

@ai_bp.route('/chat')
@login_required
def chat():
    """AI导购聊天页面"""
    try:
        # 获取用户的所有会话，按最后更新时间排序
        chat_sessions = ChatSession.query.filter_by(
            user_id=current_user.id
        ).order_by(desc(ChatSession.updated_at)).all()
        
        # 获取当前会话
        session_id = request.args.get('session_id')
        current_session = None
        
        if session_id:
            current_session = ChatSession.query.filter_by(
                id=session_id,
                user_id=current_user.id
            ).first()
        
        # 如果没有指定会话或会话不存在，创建新会话
        if not current_session:
            current_session = ChatSession(
                user_id=current_user.id,
                title='新会话',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(current_session)
            db.session.commit()
            
            # 添加欢迎消息
            welcome_message = ChatMessage(
                session_id=current_session.id,
                role='assistant',
                content=f'你好，{current_user.username}！我是数潮AI导购助手。请告诉我您想购买什么，我会为您推荐最适合的商品。'
            )
            db.session.add(welcome_message)
            db.session.commit()
        
        # 获取当前会话的消息
        messages = []
        if current_session:
            messages = ChatMessage.query.filter_by(
                session_id=current_session.id
            ).order_by(ChatMessage.created_at).all()
        
        return render_template('ai/chat.html',
                             chat_sessions=chat_sessions,
                             current_session=current_session,
                             messages=messages)
                             
    except Exception as e:
        flash('加载聊天页面时发生错误，请重试', 'error')
        print(f"Error in chat view: {str(e)}")
        return redirect(url_for('main.index'))

@ai_bp.route('/message/stream', methods=['POST'])
@login_required
def stream_message():
    """流式处理用户消息并返回AI回复"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({'error': '消息不能为空'}), 400
            
        # 获取或创建会话
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
        
        if not session:
            return jsonify({'error': '会话不存在'}), 404
            
        # 记录用户消息
        user_message = ChatMessage(
            session_id=session.id,
            role='user',
            content=message,
            created_at=datetime.utcnow()
        )
        db.session.add(user_message)
        db.session.commit()
        
        # 用于存储完整的AI回复
        full_response = []
        
        def generate():
            # 获取AI回复
            for chunk in get_ai_response(message, stream=True):
                if chunk:
                    full_response.append(chunk)
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # 保存完整的回复
            ai_message = ChatMessage(
                session_id=session.id,
                role='assistant',
                content=''.join(full_response),
                created_at=datetime.utcnow()
            )
            db.session.add(ai_message)
            
            # 更新会话时间和标题
            session.updated_at = datetime.utcnow()
            if not session.title or session.title == '新会话':
                session.title = generate_session_title(message)
            db.session.commit()
            
            yield f"data: [DONE]\n\n"
            
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in stream_message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/session/rename', methods=['PUT'])
@login_required
def rename_session():
    """重命名会话"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        new_title = data.get('title', '').strip()
        
        if not new_title:
            return jsonify({'error': '标题不能为空'}), 400
            
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
        
        if not session:
            return jsonify({'error': '会话不存在'}), 404
            
        session.title = new_title
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '会话已重命名',
            'title': new_title
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in rename_session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/session/delete', methods=['DELETE'])
@login_required
def delete_session():
    """删除会话"""
    try:
        session_id = request.args.get('session_id')
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
        
        if not session:
            return jsonify({'error': '会话不存在'}), 404
            
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '会话已删除'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_session: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_session_title(message: str) -> str:
    """生成会话标题"""
    try:
        keywords = jieba.analyse.extract_tags(message, topK=3)
        if keywords:
            return "关于" + "、".join(keywords) + "的咨询"
        return "商品咨询"
    except Exception as e:
        print(f"Error in generate_session_title: {str(e)}")
        return "新会话"

@ai_bp.route('/session/new', methods=['POST'])
@login_required
def new_session():
    """创建新会话"""
    try:
        # 创建新会话
        session = ChatSession(
            user_id=current_user.id,
            title='新会话',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(session)
        db.session.commit()
        
        # 添加欢迎消息
        welcome_message = ChatMessage(
            session_id=session.id,
            role='assistant',
            content=f'你好，{current_user.username}！我是数潮AI导购助手。请告诉我您想购买什么，我会为您推荐最适合的商品。'
        )
        db.session.add(welcome_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'redirect_url': url_for('ai.chat', session_id=session.id)
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in new_session: {str(e)}")
        return jsonify({
            'success': False,
            'message': '创建新会话失败，请重试'
        }), 500 