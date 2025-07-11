// Main application JavaScript for Auto Email Responder

// Server connectivity status
let serverConnected = false;

// DOM Elements - Dashboard
const dashboardStatsElements = {
    emailsProcessed: document.querySelector('#dashboard .stats-grid .stat-card:nth-child(1) .stat-number'),
    responseRate: document.querySelector('#dashboard .stats-grid .stat-card:nth-child(2) .stat-number'),
    avgResponseTime: document.querySelector('#dashboard .stats-grid .stat-card:nth-child(3) .stat-number'),
    activePolicies: document.querySelector('#dashboard .stats-grid .stat-card:nth-child(4) .stat-number')
};

const recentActivityTable = document.querySelector('#dashboard .data-table tbody');

// DOM Elements - Inbox
const processInboxButton = document.querySelector('#inbox .filter-row .button');
const refreshInboxButton = document.querySelector('#inbox .filter-row .button.secondary:nth-child(3)');
const inboxContainer = document.querySelector('#inbox .main-content');
const inboxSearchInput = document.querySelector('#inbox .search-box input');

// DOM Elements - Compose
const singleEmailForm = document.querySelector('#compose .form-section:nth-child(1)');
const batchEmailForm = document.querySelector('#compose .form-section:nth-child(2)');
const sendEmailButton = singleEmailForm ? singleEmailForm.querySelector('.button') : null;
const generateResponseButton = singleEmailForm ? singleEmailForm.querySelector('.button.secondary') : null;
const processBatchButton = batchEmailForm ? batchEmailForm.querySelector('.button') : null;

// DOM Elements - Policies
const addPolicyForm = document.querySelector('#policies .card:nth-child(1)');
const policiesTable = document.querySelector('#policies .data-table tbody');
const addPolicyButton = addPolicyForm ? addPolicyForm.querySelector('.button') : null;
const policySearchInput = document.querySelector('#policies .search-box input');

// DOM Elements - Settings
const testConnectionButton = document.querySelector('#settings .card:nth-child(1) .button');
const testApiButton = document.querySelector('#settings .card:nth-child(2) .button');
const clearCacheButton = document.querySelector('#settings .card:nth-child(3) .button.secondary');
const saveSettingsButton = document.querySelector('#settings .card:nth-child(4) .button');
const systemStatusElements = document.querySelectorAll('#settings .stats-grid .stat-card');

// Add server status indicator
function createServerStatusIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'server-status';
    indicator.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        z-index: 1000;
        transition: all 0.3s ease;
    `;
    document.body.appendChild(indicator);
    return indicator;
}

const serverStatusIndicator = createServerStatusIndicator();

// Update server status indicator
function updateServerStatus(connected) {
    serverConnected = connected;
    if (connected) {
        serverStatusIndicator.textContent = '🟢 Server Connected';
        serverStatusIndicator.style.backgroundColor = '#4CAF50';
        serverStatusIndicator.style.color = 'white';
    } else {
        serverStatusIndicator.textContent = '🔴 Server Disconnected';
        serverStatusIndicator.style.backgroundColor = '#f44336';
        serverStatusIndicator.style.color = 'white';
    }
}

// Check server connectivity
async function checkServerConnectivity() {
    try {
        const isConnected = await API.System.checkConnectivity();
        updateServerStatus(isConnected);
        return isConnected;
    } catch (error) {
        updateServerStatus(false);
        return false;
    }
}

// Wrapper function to check connectivity before API calls
async function withConnectivityCheck(apiCall) {
    if (!serverConnected) {
        const isConnected = await checkServerConnectivity();
        if (!isConnected) {
            throw new Error('Server is not available. Please start the backend server first.');
        }
    }
    return await apiCall();
}

// Navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.wireframe-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected section
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.classList.add('active');
    }
    
    // Add active class to selected tab
    const selectedTab = document.querySelector(`[onclick="showSection('${sectionId}')"]`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type === 'error' ? 'status-danger' : 'status-success'}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 70px;
        right: 10px;
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 1001;
        max-width: 300px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Show loading spinner
function showLoading(container) {
    const loading = document.createElement('div');
    loading.className = 'loading';
    loading.innerHTML = `
        <div class="spinner"></div>
        <p>Loading...</p>
    `;
    if (container) {
        container.appendChild(loading);
    }
    return loading;
}

// Dashboard functions
async function loadDashboardData() {
    try {
        await withConnectivityCheck(async () => {
            // Get cache statistics
            const cacheStats = await API.Cache.getCacheStats();
            
            // Get all policies
            const policiesData = await API.Policy.getAllPolicies();
            
            // Update dashboard stats
            if (dashboardStatsElements.activePolicies) {
                dashboardStatsElements.activePolicies.textContent = policiesData.count;
            }
            
            // Get health check data
            const healthData = await API.System.healthCheck();
            
            // For demo purposes, we'll use some placeholder data
            // In a real application, these would come from the API
            if (dashboardStatsElements.emailsProcessed) {
                dashboardStatsElements.emailsProcessed.textContent = '247';
            }
            if (dashboardStatsElements.responseRate) {
                dashboardStatsElements.responseRate.textContent = '89%';
            }
            if (dashboardStatsElements.avgResponseTime) {
                dashboardStatsElements.avgResponseTime.textContent = '2.3s';
            }
            
            // Load recent activity (placeholder for now)
            // In a real app, this would come from an API endpoint
        });
    } catch (error) {
        showNotification(`Error loading dashboard data: ${error.message}`, 'error');
    }
}

// Inbox functions
async function loadInboxEmails() {
    if (!inboxContainer) return;
    
    const loadingSpinner = showLoading(inboxContainer);
    
    try {
        await withConnectivityCheck(async () => {
            // Clear existing emails
            const emailItems = inboxContainer.querySelectorAll('.email-item');
            emailItems.forEach(item => item.remove());
            
            // Get inbox emails from API
            const inboxData = await API.Email.getInboxEmails();
            
            // Remove loading spinner
            if (loadingSpinner && loadingSpinner.parentNode) {
                loadingSpinner.remove();
            }
            
            // If no emails, show message
            if (inboxData.emails.length === 0) {
                const noEmails = document.createElement('div');
                noEmails.className = 'notification';
                noEmails.textContent = 'No emails found in inbox.';
                inboxContainer.appendChild(noEmails);
                return;
            }
            
            // Create email items
            inboxData.emails.forEach(email => {
                const emailItem = createEmailItem(email);
                inboxContainer.appendChild(emailItem);
            });
        });
    } catch (error) {
        if (loadingSpinner && loadingSpinner.parentNode) {
            loadingSpinner.remove();
        }
        showNotification(`Error loading inbox: ${error.message}`, 'error');
    }
}

function createEmailItem(email) {
    const emailItem = document.createElement('div');
    emailItem.className = 'email-item';
    
    // Format date
    const emailDate = new Date(email.date);
    const timeAgo = getTimeAgo(emailDate);
    
    emailItem.innerHTML = `
        <div class="email-header">
            <div class="email-subject">${email.subject}</div>
            <div class="email-time">${timeAgo}</div>
        </div>
        <div class="email-sender">${email.from}</div>
        <div class="email-preview">${email.snippet}</div>
        <div style="margin-top: 15px;">
            <button class="button">Generate Response</button>
            <button class="button secondary">View Full Email</button>
            <span class="status-badge ${email.responded ? 'status-success' : 'status-warning'}">
                ${email.responded ? 'Responded' : 'Pending'}
            </span>
        </div>
    `;
    
    // Add event listener for generate response button
    const generateButton = emailItem.querySelector('.button');
    generateButton.addEventListener('click', () => generateResponseForEmail(email));
    
    return emailItem;
}

async function generateResponseForEmail(email) {
    try {
        // In a real app, this would call an API endpoint to generate a response
        showNotification(`Generating response for email: ${email.subject}`);
    } catch (error) {
        showNotification(`Error generating response: ${error.message}`, 'error');
    }
}

async function processInbox() {
    try {
        const response = await API.Email.processInboxEmails();
        showNotification(response.message);
        
        // Reload inbox after processing
        setTimeout(() => {
            loadInboxEmails();
        }, 2000);
    } catch (error) {
        showNotification(`Error processing inbox: ${error.message}`, 'error');
    }
}

// Compose functions
async function sendEmail(event) {
    event.preventDefault();
    
    if (!singleEmailForm) return;
    
    try {
        const toInput = singleEmailForm.querySelector('input[type="email"]');
        const subjectInput = singleEmailForm.querySelector('input[type="text"]');
        const bodyInput = singleEmailForm.querySelector('textarea');
        const prioritySelect = singleEmailForm.querySelector('select');
        
        if (!toInput || !subjectInput || !bodyInput || !prioritySelect) {
            showNotification('Form elements not found', 'error');
            return;
        }
        
        const emailData = {
            to: toInput.value,
            subject: subjectInput.value,
            body: bodyInput.value,
            priority: prioritySelect.value.toLowerCase()
        };
        
        // Validate inputs
        if (!emailData.to || !emailData.subject || !emailData.body) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        await withConnectivityCheck(async () => {
            // Send email via API
            const response = await API.Email.sendEmail(emailData);
            
            // Show success notification
            showNotification(`Email sent successfully to ${emailData.to}`);
            
            // Clear form
            toInput.value = '';
            subjectInput.value = '';
            bodyInput.value = '';
            prioritySelect.value = 'Medium';
        });
    } catch (error) {
        showNotification(`Error sending email: ${error.message}`, 'error');
    }
}

async function processBatchEmails(event) {
    event.preventDefault();
    
    try {
        const fileInput = batchEmailForm.querySelector('input[type="file"]');
        
        if (!fileInput.files || fileInput.files.length === 0) {
            showNotification('Please select a CSV file', 'error');
            return;
        }
        
        // In a real app, this would parse the CSV and send batch emails
        showNotification('Batch processing started');
    } catch (error) {
        showNotification(`Error processing batch: ${error.message}`, 'error');
    }
}

// Policy functions
async function loadPolicies() {
    if (!policiesTable) return;
    
    try {
        await withConnectivityCheck(async () => {
            // Clear existing policies
            policiesTable.innerHTML = '';
            
            // Get all policies from API
            const policiesData = await API.Policy.getAllPolicies();
            
            // Create policy rows
            policiesData.policies.forEach(policy => {
                const row = document.createElement('tr');
                
                row.innerHTML = `
                    <td>${policy.title}</td>
                    <td>${policy.category}</td>
                    <td>${policy.keywords.join(', ')}</td>
                    <td>${getTimeAgo(new Date(policy.created_at))}</td>
                    <td>
                        <button class="button">Edit</button>
                        <button class="button danger">Delete</button>
                    </td>
                `;
                
                policiesTable.appendChild(row);
            });
        });
    } catch (error) {
        showNotification(`Error loading policies: ${error.message}`, 'error');
    }
}

async function addPolicy(event) {
    event.preventDefault();
    
    if (!addPolicyForm) return;
    
    try {
        const titleInput = addPolicyForm.querySelector('input[type="text"]:nth-of-type(1)');
        const categorySelect = addPolicyForm.querySelector('select');
        const keywordsInput = addPolicyForm.querySelector('input[type="text"]:nth-of-type(2)');
        const contentInput = addPolicyForm.querySelector('textarea');
        
        if (!titleInput || !categorySelect || !keywordsInput || !contentInput) {
            showNotification('Form elements not found', 'error');
            return;
        }
        
        const policyData = {
            title: titleInput.value,
            category: categorySelect.value,
            keywords: keywordsInput.value.split(',').map(k => k.trim()),
            content: contentInput.value
        };
        
        // Validate inputs
        if (!policyData.title || !policyData.content || policyData.keywords.length === 0) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        await withConnectivityCheck(async () => {
            // Add policy via API
            const response = await API.Policy.addPolicy(policyData);
            
            // Show success notification
            showNotification(`Policy "${policyData.title}" added successfully`);
            
            // Clear form
            titleInput.value = '';
            keywordsInput.value = '';
            contentInput.value = '';
            
            // Reload policies
            loadPolicies();
        });
    } catch (error) {
        showNotification(`Error adding policy: ${error.message}`, 'error');
    }
}

async function searchPolicies() {
    try {
        const query = policySearchInput.value.trim();
        
        if (!query) {
            loadPolicies();
            return;
        }
        
        // Clear existing policies
        policiesTable.innerHTML = '';
        
        // Search policies via API
        const searchResults = await API.Policy.searchPolicies(query);
        
        // Create policy rows
        searchResults.policies.forEach(policy => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${policy.title}</td>
                <td>${policy.category}</td>
                <td>${policy.keywords.join(', ')}</td>
                <td>${getTimeAgo(new Date(policy.created_at))}</td>
                <td>
                    <button class="button">Edit</button>
                    <button class="button danger">Delete</button>
                </td>
            `;
            
            policiesTable.appendChild(row);
        });
    } catch (error) {
        showNotification(`Error searching policies: ${error.message}`, 'error');
    }
}

// Settings functions
async function clearCache() {
    try {
        const response = await API.Cache.clearCache();
        showNotification(response.message);
    } catch (error) {
        showNotification(`Error clearing cache: ${error.message}`, 'error');
    }
}

async function checkSystemStatus() {
    try {
        // Check health
        const healthData = await API.System.healthCheck();
        
        // Update system status indicators
        systemStatusElements[0].querySelector('.stat-number').textContent = '✅';
        systemStatusElements[1].querySelector('.stat-number').textContent = '✅';
        systemStatusElements[2].querySelector('.stat-number').textContent = '✅';
        systemStatusElements[3].querySelector('.stat-number').textContent = '✅';
    } catch (error) {
        // If health check fails, update status indicators
        systemStatusElements[0].querySelector('.stat-number').textContent = '❌';
        systemStatusElements[1].querySelector('.stat-number').textContent = '❌';
        systemStatusElements[2].querySelector('.stat-number').textContent = '❌';
        systemStatusElements[3].querySelector('.stat-number').textContent = '❌';
        
        showNotification(`Error checking system status: ${error.message}`, 'error');
    }
}

// Utility functions
function getTimeAgo(date) {
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Check server connectivity on page load
    checkServerConnectivity();

    // Dashboard
    loadDashboardData();
    
    // Inbox
    if (processInboxButton) {
        processInboxButton.addEventListener('click', processInbox);
    }
    if (refreshInboxButton) {
        refreshInboxButton.addEventListener('click', loadInboxEmails);
    }
    
    // Compose
    if (sendEmailButton) {
        sendEmailButton.addEventListener('click', sendEmail);
    }
    if (processBatchButton) {
        processBatchButton.addEventListener('click', processBatchEmails);
    }
    
    // Policies
    if (addPolicyButton) {
        addPolicyButton.addEventListener('click', addPolicy);
    }
    if (policySearchInput) {
        policySearchInput.addEventListener('input', debounce(searchPolicies, 500));
    }
    
    // Settings
    if (clearCacheButton) {
        clearCacheButton.addEventListener('click', clearCache);
    }
    if (testConnectionButton) {
        testConnectionButton.addEventListener('click', checkSystemStatus);
    }
});

// Make showSection globally available for the HTML onclick handlers
window.showSection = showSection;

// Debounce function for search inputs
function debounce(func, delay) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), delay);
    };
}