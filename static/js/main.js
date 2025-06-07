// 使用Service Worker实现PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('ServiceWorker注册成功');
            })
            .catch(err => {
                console.log('ServiceWorker注册失败:', err);
            });
    });
}

// 实现懒加载
const lazyImages = document.querySelectorAll('.lazy-image');
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.remove('lazy-image');
            observer.unobserve(img);
        }
    });
});

lazyImages.forEach(img => imageObserver.observe(img));

// 实现无限滚动
class InfiniteScroll {
    constructor(container, loadMore) {
        this.container = container;
        this.loadMore = loadMore;
        this.page = 1;
        this.loading = false;
        this.observer = new IntersectionObserver(
            this.handleIntersect.bind(this)
        );
        this.observer.observe(this.loadMore);
    }

    async handleIntersect(entries) {
        if (entries[0].isIntersecting && !this.loading) {
            this.loading = true;
            await this.loadNextPage();
            this.loading = false;
        }
    }

    async loadNextPage() {
        try {
            const response = await fetch(`/api/products?page=${this.page}`);
            const data = await response.json();
            this.renderProducts(data.items);
            this.page++;
        } catch (error) {
            console.error('加载更多商品失败:', error);
        }
    }

    renderProducts(products) {
        // 渲染商品列表
    }
}

// 自动关闭警告消息
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有警告消息
    var alerts = document.querySelectorAll('.alert');
    
    // 为每个警告消息设置自动关闭
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5秒后自动关闭
    });
});

// 表单验证
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有需要验证的表单
    var forms = document.querySelectorAll('.needs-validation');
    
    // 遍历表单并添加验证
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});