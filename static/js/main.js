/**
 * Main JavaScript for Financial AI Platform
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date range pickers
    initializeDateInputs();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Add form validation
    addFormValidation();
    
    // Initialize collapsible sections
    initializeCollapsibleSections();
    
    // Initialize theme toggler if present
    const themeToggler = document.getElementById('themeToggler');
    if (themeToggler) {
        initializeThemeToggler(themeToggler);
    }
});

/**
 * Initialize date inputs with default values
 */
function initializeDateInputs() {
    const startDateInputs = document.querySelectorAll('input[type="date"][id*="start_date"]');
    const endDateInputs = document.querySelectorAll('input[type="date"][id*="end_date"]');
    
    if (startDateInputs.length) {
        startDateInputs.forEach(input => {
            if (!input.value) {
                const threeMonthsAgo = new Date();
                threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
                input.value = threeMonthsAgo.toISOString().split('T')[0];
            }
        });
    }
    
    if (endDateInputs.length) {
        endDateInputs.forEach(input => {
            if (!input.value) {
                const today = new Date();
                input.value = today.toISOString().split('T')[0];
            }
        });
    }
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Add form validation to forms with needs-validation class
 */
function addFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize collapsible sections
 */
function initializeCollapsibleSections() {
    const collapsibleTriggers = document.querySelectorAll('[data-bs-toggle="collapse"]');
    
    collapsibleTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const icon = this.querySelector('i.fas');
            if (icon) {
                if (icon.classList.contains('fa-chevron-down')) {
                    icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
                } else {
                    icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
                }
            }
        });
    });
}

/**
 * Initialize theme toggler
 * @param {HTMLElement} toggler - The theme toggle button
 */
function initializeThemeToggler(toggler) {
    toggler.addEventListener('click', function() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-bs-theme');
        
        if (currentTheme === 'dark') {
            html.setAttribute('data-bs-theme', 'light');
            toggler.innerHTML = '<i class="fas fa-moon"></i>';
            localStorage.setItem('theme', 'light');
        } else {
            html.setAttribute('data-bs-theme', 'dark');
            toggler.innerHTML = '<i class="fas fa-sun"></i>';
            localStorage.setItem('theme', 'dark');
        }
    });
    
    // Set initial theme based on localStorage or system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        toggler.innerHTML = savedTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
        toggler.innerHTML = '<i class="fas fa-sun"></i>';
    }
}

/**
 * Format currency value
 * @param {number} value - The value to format
 * @param {string} currency - The currency symbol
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted currency string
 */
function formatCurrency(value, currency = '$', decimals = 2) {
    if (isNaN(value)) return `${currency}0.00`;
    return `${currency}${parseFloat(value).toFixed(decimals).replace(/\d(?=(\d{3})+\.)/g, '$&,')}`;
}

/**
 * Format percentage value
 * @param {number} value - The value to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage string
 */
function formatPercentage(value, decimals = 2) {
    if (isNaN(value)) return '0.00%';
    return `${parseFloat(value).toFixed(decimals)}%`;
}

/**
 * Format large numbers with abbreviations
 * @param {number} num - The number to format
 * @returns {string} Formatted number string
 */
function formatNumber(num) {
    if (isNaN(num)) return '0';
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1) + 'B';
    }
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/**
 * Display a notification
 * @param {string} message - The notification message
 * @param {string} type - The notification type (success, danger, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.querySelector('.notification-container') || createNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    container.appendChild(notification);
    
    // Remove notification after duration
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

/**
 * Create notification container if it doesn't exist
 * @returns {HTMLElement} Notification container
 */
function createNotificationContainer() {
    const container = document.createElement('div');
    container.className = 'notification-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

/**
 * Load CSV data from a file
 * @param {File} file - The CSV file
 * @returns {Promise<Array>} Array of objects representing CSV data
 */
function loadCSV(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const text = e.target.result;
            const result = parseCSV(text);
            resolve(result);
        };
        
        reader.onerror = function() {
            reject(new Error('Error reading file'));
        };
        
        reader.readAsText(file);
    });
}

/**
 * Parse CSV text into an array of objects
 * @param {string} text - CSV text content
 * @returns {Array} Array of objects representing CSV data
 */
function parseCSV(text) {
    const lines = text.split('\n');
    const headers = lines[0].split(',').map(header => header.trim());
    const result = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        
        const obj = {};
        const currentLine = lines[i].split(',');
        
        for (let j = 0; j < headers.length; j++) {
            let value = currentLine[j].trim();
            
            // Try to convert to number if possible
            if (!isNaN(value) && value !== '') {
                value = parseFloat(value);
            }
            
            obj[headers[j]] = value;
        }
        
        result.push(obj);
    }
    
    return result;
}

/**
 * Format date string
 * @param {string} dateStr - Date string in ISO format
 * @param {boolean} includeTime - Whether to include time
 * @returns {string} Formatted date string
 */
function formatDate(dateStr, includeTime = false) {
    if (!dateStr) return '';
    
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleDateString(undefined, options);
}
