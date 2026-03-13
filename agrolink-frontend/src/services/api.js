/**
 * API Service
 * 
 * Centralized service for making API calls to the backend.
 * Automatically includes Firebase ID token for authenticated requests.
 */

import axios from 'axios';
import { auth } from '../firebaseConfig';

// Base URL for the backend API
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add Firebase ID token
apiClient.interceptors.request.use(
    async (config) => {
        const user = auth.currentUser;
        if (user) {
            try {
                const token = await user.getIdToken();
                config.headers.Authorization = `Bearer ${token}`;
            } catch (error) {
                console.error('Error getting ID token:', error);
            }
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // Server responded with error
            console.error('API Error:', error.response.data);
        } else if (error.request) {
            // Request made but no response
            console.error('Network Error:', error.request);
        } else {
            console.error('Error:', error.message);
        }
        return Promise.reject(error);
    }
);

// API Functions

/**
 * Fertilizer Recommendation API
 */
export const fertilizer = {
    /**
     * Get fertilizer recommendation
     */
    recommend: async (data, lang = "en") => {
        const response = await apiClient.post(`/api/fertilizer/recommend?lang=${lang}`, data);
        return response.data;
    },

    /**
     * Get available soil types
     */
    getSoilTypes: async () => {
        const response = await apiClient.get('/api/fertilizer/soil-types');
        return response.data;
    },

    /**
     * Get available crop types
     */
    getCropTypes: async () => {
        const response = await apiClient.get('/api/fertilizer/crop-types');
        return response.data;
    },

    /**
     * Get fertilizer information
     */
    getFertilizerInfo: async (fertilizerName) => {
        const response = await apiClient.get(`/api/fertilizer/fertilizer-info/${fertilizerName}`);
        return response.data;
    },
};

/**
 * Price Prediction API
 */
export const price = {
    /**
     * Predict crop price
     */
    predict: async (data, lang = "en") => {
        const response = await apiClient.post(`/api/price/predict?lang=${lang}`, data);
        return response.data;
    },

    /**
     * Record actual sale price
     */
    recordPrice: async (data) => {
        const response = await apiClient.post('/api/price/record', data);
        return response.data;
    },

    /**
     * Get price history for a crop
     */
    getHistory: async (cropType, limit = 50) => {
        const response = await apiClient.get(`/api/price/history/${cropType}`, {
            params: { limit }
        });
        return response.data;
    },

    /**
     * Get available crops for prediction
     */
    getCrops: async () => {
        const response = await apiClient.get('/api/price/crops');
        return response.data;
    },

    /**
     * Get available states for prediction
     */
    getStates: async () => {
        const response = await apiClient.get('/api/price/states');
        return response.data;
    },
};

/**
 * Crop Recommendation API (existing)
 */
export const crop = {
    /**
     * Get crop recommendation
     */
    predict: async (data) => {
        const response = await apiClient.post('/api/crop/predict', data);
        return response.data;
    },
};

/**
 * Chatbot API (existing)
 */
export const chatbot = {
    /**
     * Send message to chatbot
     */
    ask: async (message, language) => {
        const response = await apiClient.post('/api/chatbot/ask', { message, language });
        return response.data;
    },
};

export default apiClient;
