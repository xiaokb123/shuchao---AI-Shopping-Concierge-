from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from api.models import db, Budget, PurchaseHistory
from datetime import datetime, timedelta

# 页面路由蓝图
budget_bp = Blueprint('budget', __name__, url_prefix='/budget')

# API路由蓝图
budget_api_bp = Blueprint('budget_api', __name__, url_prefix='/api/budget')

@budget_bp.route('/')
@login_required
def dashboard():
    """预算管理仪表板"""
    return render_template('budget/dashboard.html')

@budget_api_bp.route('/create', methods=['POST'])
@login_required
def create_budget():
    """创建新预算"""
    data = request.get_json()
    
    # 验证数据
    if not all(key in data for key in ['category', 'amount', 'start_date', 'end_date']):
        return jsonify({'error': '缺少必要参数'}), 400
        
    try:
        budget = Budget(
            user_id=current_user.id,
            category=data['category'],
            amount=float(data['amount']),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d'),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d')
        )
        db.session.add(budget)
        db.session.commit()
        return jsonify({'message': '预算创建成功', 'budget_id': budget.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@budget_api_bp.route('/<int:budget_id>', methods=['PUT'])
@login_required
def update_budget(budget_id):
    """更新预算"""
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        return jsonify({'error': '无权限修改此预算'}), 403
        
    data = request.get_json()
    try:
        if 'amount' in data:
            budget.amount = float(data['amount'])
        if 'category' in data:
            budget.category = data['category']
        if 'start_date' in data:
            budget.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        if 'end_date' in data:
            budget.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
            
        db.session.commit()
        return jsonify({'message': '预算更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@budget_api_bp.route('/status')
@login_required
def get_budget_status():
    """获取预算状态"""
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    
    status = []
    for budget in budgets:
        # 计算预算使用情况
        percentage = (budget.spent / budget.amount * 100) if budget.amount > 0 else 0
        status.append({
            'id': budget.id,
            'category': budget.category,
            'amount': budget.amount,
            'spent': budget.spent,
            'percentage': round(percentage, 2),
            'is_exceeded': budget.is_exceeded(),
            'start_date': budget.start_date.strftime('%Y-%m-%d'),
            'end_date': budget.end_date.strftime('%Y-%m-%d')
        })
    
    return jsonify(status)

@budget_api_bp.route('/alert')
@login_required
def check_budget_alerts():
    """检查预算警告"""
    from flask import current_app
    threshold = current_app.config['BUDGET_WARNING_THRESHOLD']
    
    alerts = []
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    
    for budget in budgets:
        percentage = (budget.spent / budget.amount * 100) if budget.amount > 0 else 0
        if percentage >= threshold * 100:
            alerts.append({
                'category': budget.category,
                'percentage': round(percentage, 2),
                'remaining': budget.amount - budget.spent
            })
    
    return jsonify(alerts)

@budget_api_bp.route('/<int:budget_id>', methods=['DELETE'])
@login_required
def delete_budget(budget_id):
    """删除预算"""
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        return jsonify({'error': '无权限删除此预算'}), 403
        
    try:
        db.session.delete(budget)
        db.session.commit()
        return jsonify({'message': '预算删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 