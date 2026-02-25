/**
 * API SERVICE LAYER
 * 
 * Centralizes all backend API communication for the Safari Scouts application.
 * Provides typed methods for interacting with chat, weather, budget, and location endpoints.
 * Uses axios for HTTP requests with automatic error handling and response transformation.
 */

import axios from 'axios';
import { ChatRequest, ChatResponse, EstimateRequest, EstimateResponse, WeatherInfo } from '../types';

// Retrieve API base URL from environment configuration or default to local development server
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Initialize axios instance with base configuration
// Applies consistent headers and base URL to all requests
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Send a chat message to the LLM backend endpoint
// Accepts user query or follow-up messages and returns assistant response with optional trip data
export const sendChatMessage = async (data: ChatRequest): Promise<ChatResponse> => {
  const response = await apiClient.post('/chat', data);
  return response.data;
};

// Fetch weather conditions for a specified location and optional date
// Returns temperature, conditions, humidity, and wind data for trip planning
export const getWeather = async (location: string, date?: string): Promise<WeatherInfo> => {
  const params = new URLSearchParams({ location });
  if (date) params.append('date', date);
  const response = await apiClient.get(`/weather?${params.toString()}`);
  return response.data;
};

// Calculate budget estimate for a trip based on location, duration, and budget tier
// Returns itemized cost breakdown across accommodation, transport, activities, and fees
export const getBudgetEstimate = async (data: EstimateRequest): Promise<EstimateResponse> => {
  const response = await apiClient.post('/estimate', data);
  return response.data;
};

// Retrieve predefined suggested prompts to guide user interactions
// Provides example queries for common safari trip planning scenarios
// Currently uses static list; can be enhanced to fetch dynamic suggestions from backend
export const getSuggestedPrompts = async (): Promise<string[]> => {
  // Return static prompts for now; could be dynamic from backend
  return [
    'Plan a 4-day mid-range trip to Amboseli in July',
    'What is the best time to visit Diani Beach?',
    'Budget safari for 3 days in Masai Mara',
    'Weather in Naivasha next weekend',
    'Luxury resorts in Watamu with prices',
  ];
};