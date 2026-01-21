import axios from 'axios';
import { API_BASE_URL } from '../config';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 120000, // 2 minutes for cold starts
    headers: {
        'Content-Type': 'application/json',
    }
});

// Add auth token to requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Handle response errors globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

/**
 * Retry a request with exponential backoff
 */
async function retryRequest(requestFn, maxRetries = 3, initialDelay = 1000) {
    let lastError;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await requestFn();
        } catch (error) {
            lastError = error;

            // Don't retry on client errors (4xx except 408, 429)
            if (error.response?.status >= 400 && error.response?.status < 500) {
                if (error.response.status !== 408 && error.response.status !== 429) {
                    throw error;
                }
            }

            // Don't retry on last attempt
            if (attempt === maxRetries - 1) {
                throw error;
            }

            // Wait before retrying (exponential backoff)
            const delay = initialDelay * Math.pow(2, attempt);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }

    throw lastError;
}

/**
 * Check if backend is awake and healthy
 */
export async function checkBackendHealth() {
    try {
        const response = await axios.get(`${API_BASE_URL}/health/status`, {
            timeout: 90000 // 90 seconds for cold start
        });
        return response.data;
    } catch (error) {
        console.error('Health check failed:', error);
        return null;
    }
}

/**
 * Wake up the backend (for cold starts)
 */
export async function wakeUpBackend(onProgress) {
    try {
        if (onProgress) onProgress('Connecting to server...');

        const startTime = Date.now();
        const health = await checkBackendHealth();
        const duration = Date.now() - startTime;

        if (health) {
            if (onProgress) {
                if (duration > 10000) {
                    onProgress('Server was sleeping, now awake!');
                } else {
                    onProgress('Server is ready!');
                }
            }
            return true;
        }

        return false;
    } catch (error) {
        console.error('Failed to wake up backend:', error);
        return false;
    }
}

/**
 * Login with retry and health check
 */
export async function login(email, password, onProgress) {
    // First, wake up the backend if needed
    if (onProgress) onProgress('Checking server status...');
    await wakeUpBackend(onProgress);

    if (onProgress) onProgress('Logging in...');

    return retryRequest(async () => {
        const response = await api.post('/auth/login', { email, password });
        return response.data;
    });
}

/**
 * Register with retry and health check
 */
export async function register(email, password, full_name, onProgress) {
    // First, wake up the backend if needed
    if (onProgress) onProgress('Checking server status...');
    await wakeUpBackend(onProgress);

    if (onProgress) onProgress('Creating account...');

    return retryRequest(async () => {
        const response = await api.post('/auth/register', { email, password, full_name });
        return response.data;
    });
}

/**
 * Send a query to the chatbot
 */
export async function sendQuery(query, useGoldenKB = false, persona = 'strict_formal') {
    return retryRequest(async () => {
        const response = await api.post('/query/ask', {
            query,
            use_golden_kb: useGoldenKB,
            persona
        });
        return response.data;
    });
}

/**
 * Get user profile
 */
export async function getUserProfile() {
    const response = await api.get('/auth/me');
    return response.data;
}

/**
 * Update user profile
 */
export async function updateUserProfile(updates) {
    const response = await api.patch('/auth/me', updates);
    return response.data;
}

export default api;
