/**
 * API SERVICE LAYER
 * 
 * Centralizes all backend API communication for the Safari Scouts application.
 * Provides typed methods for interacting with chat, weather, budget, and location endpoints.
 * Uses axios for HTTP requests with automatic error handling and response transformation.
 */

import axios from 'axios';
import type {  ChatResponse, EstimateResponse, WeatherResponse } from '../types';



// Base URL for the backend API, configurable via environment variable
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';


// Create an axios instance with default configuration
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Add timeout and other defaults
  timeout: 30000,
});

// Request interceptor for logging (optional)
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API methods
// Each method corresponds to a backend endpoint and returns typed data for use in the frontend application.



export const chatApi = {
  /**
   * Send a message to the chat assistant and get a reply
   * @param sessionId - Unique session identifier
   * @param message - User's message
   * @returns Promise with assistant's reply
   */
  sendMessage: async (sessionId: string, message: string): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat', {
      session_id: sessionId,
      message,
    });
    return response.data;
  },

  /**
   * Get weather information for a location
   * @param location - City or place name
   * @param days - Number of days ahead (0 for current)
   * @returns Weather information
   */
  getWeather: async (location: string, days: number = 0): Promise<WeatherResponse> => {
    const response = await api.get<WeatherResponse>('/weather', {
      params: { location, days },
    });
    return response.data;
  },

  /**
   * Get a budget estimate for a trip
   * @param location - Destination
   * @param days - Number of days
   * @param budgetLevel - 'budget', 'mid', or 'luxury'
   * @returns Cost breakdown and total
   */
  getEstimate: async (
    location: string, 
    days: number, 
    budgetLevel: 'budget' | 'mid' | 'luxury'
  ): Promise<EstimateResponse> => {
    const response = await api.post<EstimateResponse>('/estimate', {
      location,
      days,
      budget_level: budgetLevel,
    });
    return response.data;
  },

  /**
   * Check if the API is reachable
   */
  healthCheck: async (): Promise<boolean> => {
    try {
      await api.get('/');
      return true;
    } catch {
      return false;
    }
  },
};

