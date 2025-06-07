// 加载预算状态
async function loadBudgetStatus() {
    try {
        const response = await fetch('/api/budget/status');
        const budgets = await response.json();
        
        const budgetCards = document.getElementById('budgetCards');
        budgetCards.innerHTML = '';
        
        budgets.forEach(budget => {
            const card = createBudgetCard(budget);
            budgetCards.appendChild(card);
        });
        
        // 检查预算警告
        checkBudgetAlerts();
    } catch (error) {
        console.error('加载预算状态失败:', error);
    }
}

// 创建预算卡片
function createBudgetCard(budget) {
    const card = document.createElement('div');
    card.className = 'budget-card';
    
    let progressClass = '';
    if (budget.percentage >= 100) {
        progressClass = 'danger';
    } else if (budget.percentage >= 80) {
        progressClass = 'warning';
    }
    
    card.innerHTML = `
        <h3>${budget.category}</h3>
        <div class="progress-bar">
            <div class="progress-bar-fill ${progressClass}" 
                 style="width: ${Math.min(budget.percentage, 100)}%"></div>
        </div>
        <div class="budget-details">
            <span>已使用: ¥${budget.spent}</span>
            <span>总预算: ¥${budget.amount}</span>
        </div>
        <div class="budget-dates">
            <small>${budget.start_date} 至 ${budget.end_date}</small>
        </div>
    `;
    
    return card;
}

// 显示创建预算模态框
function showNewBudgetModal() {
    document.getElementById('newBudgetModal').style.display = 'block';
}

// 关闭创建预算模态框
function closeNewBudgetModal() {
    document.getElementById('newBudgetModal').style.display = 'none';
}

// 处理创建预算表单提交
document.getElementById('newBudgetForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        category: document.getElementById('category').value,
        amount: document.getElementById('amount').value,
        start_date: document.getElementById('start_date').value,
        end_date: document.getElementById('end_date').value
    };
    
    try {
        const response = await fetch('/api/budget', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        if (response.ok) {
            closeNewBudgetModal();
            loadBudgetStatus();
        } else {
            alert(data.error || '创建预算失败');
        }
    } catch (error) {
        alert('发生错误，请重试');
    }
});

// 检查预算警告
async function checkBudgetAlerts() {
    try {
        const response = await fetch('/api/budget/alert');
        const alerts = await response.json();
        
        if (alerts.length > 0) {
            showAlertModal(alerts);
        }
    } catch (error) {
        console.error('检查预算警告失败:', error);
    }
}

// 显示警告模态框
function showAlertModal(alerts) {
    const alertContent = document.getElementById('alertContent');
    alertContent.innerHTML = alerts.map(alert => `
        <div class="alert-message">
            ${alert.category} 类别预算已使用 ${alert.percentage}%
            <br>
            剩余预算: ¥${alert.remaining.toFixed(2)}
        </div>
    `).join('');
    
    document.getElementById('alertModal').style.display = 'block';
}

// 关闭警告模态框
function closeAlertModal() {
    document.getElementById('alertModal').style.display = 'none';
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    loadBudgetStatus();
}); 