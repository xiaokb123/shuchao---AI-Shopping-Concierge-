// 表单验证
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(form)) {
                event.preventDefault();
            }
        });
        
        // 实时验证
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(input);
            });
        });
    });
});

// 验证表单
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// 验证单个字段
function validateField(input) {
    const value = input.value.trim();
    const type = input.type;
    const name = input.name;
    let isValid = true;
    let errorMessage = '';
    
    // 清除现有错误消息
    clearError(input);
    
    // 必填字段验证
    if (input.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = '此字段不能为空';
    }
    
    // 邮箱验证
    if (type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = '请输入有效的邮箱地址';
        }
    }
    
    // 密码验证
    if (name === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            errorMessage = '密码长度不能少于6个字符';
        }
    }
    
    // 确认密码验证
    if (name === 'confirm_password') {
        const password = document.querySelector('input[name="password"]').value;
        if (value !== password) {
            isValid = false;
            errorMessage = '两次输入的密码不一致';
        }
    }
    
    // 用户名验证
    if (name === 'username' && value) {
        if (value.length < 3 || value.length > 20) {
            isValid = false;
            errorMessage = '用户名长度必须在3到20个字符之间';
        }
        if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
            isValid = false;
            errorMessage = '用户名只能包含字母、数字、下划线和连字符';
        }
    }
    
    // 显示错误消息
    if (!isValid) {
        showError(input, errorMessage);
    }
    
    return isValid;
}

// 显示错误消息
function showError(input, message) {
    const formGroup = input.closest('.form-group');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback d-block';
    errorDiv.innerText = message;
    formGroup.appendChild(errorDiv);
    input.classList.add('is-invalid');
}

// 清除错误消息
function clearError(input) {
    const formGroup = input.closest('.form-group');
    const errorDiv = formGroup.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
    input.classList.remove('is-invalid');
}

// 显示提示消息
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // 5秒后自动关闭
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// 处理注册表单提交
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });

        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            setTimeout(() => {
                window.location.href = data.redirect + '?t=' + new Date().getTime();
            }, 1500);
        } else {
            showAlert(data.error || '注册失败，请重试', 'danger');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAlert('发生错误，请重试', 'danger');
    }
});

// 处理登录表单提交
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });

        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            setTimeout(() => {
                window.location.href = data.redirect + '?t=' + new Date().getTime();
            }, 1500);
        } else {
            showAlert(data.error || '登录失败，请重试', 'danger');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('发生错误，请重试', 'danger');
    }
}); 