// API integration for Auto Email Responder

// Base URL for API endpoints
const API_BASE_URL = 'http://localhost:8000';

// Utility function for making API requests
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            let errorMessage = 'API request failed';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                // If we can't parse the error response, use status text
                errorMessage = response.statusText || `HTTP ${response.status}`;
            }
            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        
        // Handle specific error types
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Unable to connect to the server. Please make sure the backend API is running at http://localhost:8000');
        }
        
        if (error.message.includes('ERR_CONNECTION_REFUSED')) {
            throw new Error('Connection refused. Please start the backend server first.');
        }
        
        throw error;
    }
}

// Add a function to check server connectivity
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch (error) {
        return false;
    }
}

// Email API functions
const EmailAPI = {
    // Send a single email
    async sendEmail(emailData) {
        return await fetchAPI('/emails/send', {
            method: 'POST',
            body: JSON.stringify(emailData)
        });
    },

    // Send batch emails
    async sendBatchEmails(batchData) {
        return await fetchAPI('/emails/batch', {
            method: 'POST',
            body: JSON.stringify(batchData)
        });
    },

    // Get inbox emails
    async getInboxEmails() {
        return await fetchAPI('/emails/inbox');
    },

    // Process inbox emails
    async processInboxEmails() {
        return await fetchAPI('/emails/process-inbox', {
            method: 'POST'
        });
    }
};

// Policy API functions
const PolicyAPI = {
    // Add a new policy
    async addPolicy(policyData) {
        return await fetchAPI('/policies/add', {
            method: 'POST',
            body: JSON.stringify(policyData)
        });
    },

    // Search policies
    async searchPolicies(query) {
        return await fetchAPI(`/policies/search?query=${encodeURIComponent(query)}`);
    },

    // Get all policies
    async getAllPolicies() {
        return await fetchAPI('/policies/all');
    }
};

// Cache API functions
const CacheAPI = {
    // Get cache statistics
    async getCacheStats() {
        return await fetchAPI('/cache/stats');
    },

    // Clear cache
    async clearCache() {
        return await fetchAPI('/cache/clear', {
            method: 'POST'
        });
    }
};

// System API functions
const SystemAPI = {
    // Health check
    async healthCheck() {
        return await fetchAPI('/health');
    },

    // Check server connectivity
    async checkConnectivity() {
        return await checkServerHealth();
    }
};

// Export all API functions
const API = {
    Email: EmailAPI,
    Policy: PolicyAPI,
    Cache: CacheAPI,
    System: SystemAPI
};