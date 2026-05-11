/**
 * Centralized Axios API Client for SmartSync
 * All frontend API calls should use this instance
 */

import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';
import Constants from 'expo-constants';

// Get API URL from environment or use default
const API_URL = process.env.EXPO_PUBLIC_API_URL || Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000/api';

/**
 * Create and configure the Axios instance
 */
const client: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

/**
 * Request interceptor
 * Add authentication token if available
 */
client.interceptors.request.use(
  (config) => {
    // TODO: Add bearer token from AsyncStorage if authenticated
    // const token = await AsyncStorage.getItem('auth_token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor
 * Handle common error scenarios
 */
client.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data as Record<string, unknown>;

      switch (status) {
        case 401:
          // Unauthorized - handle logout
          console.error('Authentication failed. Please login again.');
          // TODO: Trigger logout action
          break;
        case 403:
          console.error('Access forbidden');
          break;
        case 404:
          console.error('Resource not found');
          break;
        case 500:
          console.error('Server error');
          break;
        default:
          console.error(`API Error: ${status} - ${(data?.detail as string) || 'Unknown error'}`);
      }
    } else if (error.request) {
      console.error('No response from server:', error.message);
    } else {
      console.error('Request setup error:', error.message);
    }

    return Promise.reject(error);
  }
);

export default client;
