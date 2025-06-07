from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from api.models import db, User, Budget
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__)

@user_bp.route('/settings')
@login_required
def settings():
    """用户设置页面"""
    return render_template('user/settings.html')

@user_bp.route('/budget', methods=['POST'])
@login_required
def set_budget():
    """设置用户预算"""
    try:
        data = request.get_json()
        monthly_budget = data.get('monthly_budget')
        category_budgets = data.get('category_budgets', {})
        
        if monthly_budget is None:
            return jsonify({
                'success': False,
                'message': '总预算不能为空'
            }), 400
        
        try:
            monthly_budget = float(monthly_budget)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '预算必须是数字'
            }), 400
        
        if monthly_budget < 0:
            return jsonify({
                'success': False,
                'message': '预算不能为负数'
            }), 400
        
        # 更新用户总预算
        current_user.monthly_budget = monthly_budget
        
        # 更新或创建分类预算
        for category, amount in category_budgets.items():
            try:
                amount = float(amount)
                if amount < 0:
                    continue
                
                budget = Budget.query.filter_by(
                    user_id=current_user.id,
                    category=category
                ).first()
                
                if budget:
                    budget.amount = amount
                else:
                    budget = Budget(
                        user_id=current_user.id,
                        category=category,
                        amount=amount,
                        spent=0.0,
                        start_date=datetime.utcnow().replace(day=1),
                        end_date=(datetime.utcnow().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                    )
                    db.session.add(budget)
                    
            except ValueError:
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '预算设置成功',
            'budget': {
                'monthly': monthly_budget,
                'categories': {b.category: b.amount for b in current_user.budgets}
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'设置预算失败: {str(e)}'
        }), 500

@user_bp.route('/budget', methods=['GET'])
@login_required
def get_budget():
    """获取用户预算信息"""
    try:
        # 获取所有预算信息
        budgets = Budget.query.filter_by(user_id=current_user.id).all()
        
        # 计算总支出
        total_spent = sum(budget.spent for budget in budgets)
        
        # 计算各类别的预算使用情况
        categories = []
        for budget in budgets:
            percentage = (budget.spent / budget.amount * 100) if budget.amount > 0 else 0
            categories.append({
                'category': budget.category,
                'amount': budget.amount,
                'spent': budget.spent,
                'remaining': budget.amount - budget.spent,
                'percentage': round(percentage, 2),
                'status': 'exceeded' if budget.is_exceeded() else (
                    'warning' if percentage >= 80 else 'normal'
                )
            })
        
        return jsonify({
            'success': True,
            'monthly_budget': current_user.monthly_budget,
            'total_spent': total_spent,
            'remaining': current_user.monthly_budget - total_spent,
            'categories': categories,
            'period': {
                'start': budgets[0].start_date.strftime('%Y-%m-%d') if budgets else None,
                'end': budgets[0].end_date.strftime('%Y-%m-%d') if budgets else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取预算失败: {str(e)}'
        }), 500

@user_bp.route('/budget/category/<category>', methods=['PUT'])
@login_required
def update_category_budget(category):
    """更新分类预算"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        
        if amount is None:
            return jsonify({
                'success': False,
                'message': '预算金额不能为空'
            }), 400
        
        try:
            amount = float(amount)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '预算必须是数字'
            }), 400
        
        if amount < 0:
            return jsonify({
                'success': False,
                'message': '预算不能为负数'
            }), 400
        
        budget = Budget.query.filter_by(
            user_id=current_user.id,
            category=category
        ).first()
        
        if budget:
            budget.amount = amount
        else:
            budget = Budget(
                user_id=current_user.id,
                category=category,
                amount=amount,
                spent=0.0,
                start_date=datetime.utcnow().replace(day=1),
                end_date=(datetime.utcnow().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            )
            db.session.add(budget)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '分类预算更新成功',
            'budget': {
                'category': budget.category,
                'amount': budget.amount,
                'spent': budget.spent,
                'remaining': budget.amount - budget.spent
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新分类预算失败: {str(e)}'
        }), 500

@user_bp.route('/budget/alerts', methods=['GET'])
@login_required
def get_budget_alerts():
    """获取预算警告"""
    try:
        alerts = []
        budgets = Budget.query.filter_by(user_id=current_user.id).all()
        
        # 检查总预算
        total_spent = sum(budget.spent for budget in budgets)
        total_percentage = (total_spent / current_user.monthly_budget * 100) if current_user.monthly_budget > 0 else 0
        
        if total_percentage >= 80:
            alerts.append({
                'type': 'total',
                'level': 'warning' if total_percentage < 100 else 'danger',
                'message': f'您的总预算使用已达到{round(total_percentage, 1)}%',
                'remaining': current_user.monthly_budget - total_spent
            })
        
        # 检查分类预算
        for budget in budgets:
            percentage = (budget.spent / budget.amount * 100) if budget.amount > 0 else 0
            if percentage >= 80:
                alerts.append({
                    'type': 'category',
                    'category': budget.category,
                    'level': 'warning' if percentage < 100 else 'danger',
                    'message': f'您的{budget.category}类预算使用已达到{round(percentage, 1)}%',
                    'remaining': budget.amount - budget.spent
                })
        
        return jsonify({
            'success': True,
            'alerts': alerts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取预算警告失败: {str(e)}'
        }), 500

@user_bp.route('/budget/statistics', methods=['GET'])
@login_required
def get_budget_statistics():
    """获取预算统计信息"""
    try:
        # 获取时间范围
        period = request.args.get('period', 'month')  # month, quarter, year
        end_date = datetime.utcnow()
        
        if period == 'month':
            start_date = end_date.replace(day=1)
        elif period == 'quarter':
            quarter_start_month = ((end_date.month - 1) // 3) * 3 + 1
            start_date = end_date.replace(month=quarter_start_month, day=1)
        else:  # year
            start_date = end_date.replace(month=1, day=1)
        
        # 获取预算使用统计
        budgets = Budget.query.filter_by(user_id=current_user.id).all()
        
        statistics = {
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            },
            'total': {
                'budget': current_user.monthly_budget,
                'spent': sum(budget.spent for budget in budgets),
                'categories': []
            },
            'trend': []
        }
        
        # 计算各类别统计
        for budget in budgets:
            percentage = (budget.spent / budget.amount * 100) if budget.amount > 0 else 0
            statistics['total']['categories'].append({
                'category': budget.category,
                'amount': budget.amount,
                'spent': budget.spent,
                'percentage': round(percentage, 2)
            })
        
        # 计算消费趋势
        current = start_date
        while current <= end_date:
            next_date = (current + timedelta(days=32)).replace(day=1) if period == 'month' else (
                current + timedelta(days=7) if period == 'week' else current + timedelta(days=1)
            )
            
            spent = db.session.query(db.func.sum(Budget.spent)).filter(
                Budget.user_id == current_user.id,
                Budget.start_date <= next_date,
                Budget.end_date >= current
            ).scalar() or 0
            
            statistics['trend'].append({
                'date': current.strftime('%Y-%m-%d'),
                'spent': spent
            })
            
            current = next_date
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取预算统计失败: {str(e)}'
        }), 500

@user_bp.route('/profile')
@login_required
def profile():
    """用户个人资料页面"""
    return render_template('user/profile.html')

@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户资料"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if username and username != current_user.username:
            if User.query.filter_by(username=username).first():
                return jsonify({
                    'success': False,
                    'message': '用户名已存在'
                }), 400
            current_user.username = username
        
        if email and email != current_user.email:
            if User.query.filter_by(email=email).first():
                return jsonify({
                    'success': False,
                    'message': '邮箱已被注册'
                }), 400
            current_user.email = email
        
        if password:
            current_user.set_password(password)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户资料更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新用户资料失败: {str(e)}'
        }), 500

@user_bp.route('/preferences', methods=['PUT'])
@login_required
def update_preferences():
    """更新用户的购物偏好设置"""
    data = request.get_json()
    
    try:
        current_user.interests = data.get('interests', [])
        current_user.price_sensitivity = data.get('price_sensitivity', 50)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '购物偏好更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@user_bp.route('/notifications', methods=['PUT'])
@login_required
def update_notifications():
    """更新用户的通知设置"""
    data = request.get_json()
    
    try:
        current_user.email_notifications = data.get('email_notifications', False)
        current_user.price_alerts = data.get('price_alerts', False)
        current_user.recommendation_notifications = data.get('recommendation_notifications', False)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '通知设置更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@user_bp.route('/security', methods=['PUT'])
@login_required
def update_security():
    """更新用户的安全设置（密码）"""
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_user.check_password(current_password):
        return jsonify({
            'success': False,
            'message': '当前密码不正确'
        }), 400
    
    try:
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 