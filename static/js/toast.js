// Toast notification system for Mystery Club

class ToastManager {
    constructor() {
        this.createToastContainer();
    }

    createToastContainer() {
        if (!document.querySelector('.toast-container')) {
            const container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
    }

    show(message, type = 'success', duration = 3000) {
        const toastContainer = document.querySelector('.toast-container');
        const toastId = 'toast-' + Date.now();
        
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast toast-${type} show fade-in-up`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        const icon = this.getIcon(type);
        
        toast.innerHTML = `
            <div class="toast-header">
                <i class="${icon} me-2"></i>
                <strong class="me-auto">${this.getTitle(type)}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto-hide after duration
        setTimeout(() => {
            this.hide(toastId);
        }, duration);
        
        // Add click to close functionality
        const closeBtn = toast.querySelector('.btn-close');
        closeBtn.addEventListener('click', () => {
            this.hide(toastId);
        });
    }

    hide(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.add('fade-out');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    }

    getIcon(type) {
        const icons = {
            success: 'fas fa-check-circle text-success',
            error: 'fas fa-exclamation-circle text-danger',
            warning: 'fas fa-exclamation-triangle text-warning',
            info: 'fas fa-info-circle text-info'
        };
        return icons[type] || icons.info;
    }

    getTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Info'
        };
        return titles[type] || 'Notification';
    }
}

// Initialize toast manager
const toastManager = new ToastManager();

// Global function to show toasts
function showToast(message, type = 'success', duration = 3000) {
    toastManager.show(message, type, duration);
}

// Handle Flask flash messages
document.addEventListener('DOMContentLoaded', function() {
    // Convert Flask flash messages to toasts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const message = alert.textContent.trim();
        const type = alert.classList.contains('alert-success') ? 'success' : 
                    alert.classList.contains('alert-danger') ? 'error' : 'info';
        
        showToast(message, type);
        alert.style.display = 'none';
    });
});

// Add CSS for toast animations
const style = document.createElement('style');
style.textContent = `
    .fade-out {
        opacity: 0 !important;
        transform: translateX(100%) !important;
        transition: all 0.3s ease !important;
    }
    
    .toast {
        margin-bottom: 0.5rem;
        min-width: 300px;
        max-width: 400px;
    }
    
    .toast-header {
        background: rgba(255, 255, 255, 0.9);
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        padding: 0.75rem 1rem;
    }
    
    .toast-body {
        padding: 0.75rem 1rem;
        background: rgba(255, 255, 255, 0.95);
    }
`;
document.head.appendChild(style);

