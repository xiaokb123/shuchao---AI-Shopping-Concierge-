// 初始化聊天
let chatHistory = [];

// 添加消息到聊天界面
function addMessage(message, isUser = false) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 处理聊天表单提交
document.getElementById('chatForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 显示用户消息
    addMessage(message, true);
    input.value = '';
    
    try {
        const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // 显示AI回复
        addMessage(data.response);
        
        // 更新推荐商品
        if (data.recommendations) {
            updateRecommendedProducts(data.recommendations);
        }
        
    } catch (error) {
        console.error('发送消息失败:', error);
        addMessage('抱歉，发生了错误，请重试。');
    }
});

// 更新推荐商品列表
function updateRecommendedProducts(products) {
    const productList = document.querySelector('.product-list');
    productList.innerHTML = products.map(product => `
        <div class="product-card" onclick="showProductDetails(${product.id})">
            <h4>${product.name}</h4>
            <p class="price">¥${product.current_price}</p>
            <p class="platform">${product.platform}</p>
        </div>
    `).join('');
}

// 显示商品详情
async function showProductDetails(productId) {
    try {
        const response = await fetch(`/api/ai/analyze-purchase`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_id: productId })
        });
        
        const data = await response.json();
        
        document.getElementById('productDetails').innerHTML = `
            <div class="analysis">
                <h3>购买分析</h3>
                <p>${data.analysis}</p>
            </div>
        `;
        
        document.getElementById('auxiliaryProducts').innerHTML = data.auxiliary_products.map(product => `
            <div class="product-card">
                <h4>${product.name}</h4>
                <p class="price">¥${product.current_price}</p>
                <p class="platform">${product.platform}</p>
            </div>
        `).join('');
        
        document.getElementById('productModal').style.display = 'block';
    } catch (error) {
        console.error('获取商品详情失败:', error);
    }
}

// 关闭商品详情模态框
function closeProductModal() {
    document.getElementById('productModal').style.display = 'none';
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    // 添加欢迎消息
    addMessage('你好！我是你的AI购物助手，请告诉我你想找什么商品，我会为你推荐最适合的选择。');
}); 