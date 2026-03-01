/**
 * TYPE DEFINITIONS FOR SAFARI SCOUTS APPLICATION
 * 
 * This file serves as the centralized location for all TypeScript interfaces and types
 * used throughout the Safari Scouts frontend application. These types ensure type safety
 * and provide clear contracts between the frontend and backend API.
 * 
 * Purpose: Define data structures for locations, messages, weather, budgets, and API requests/responses
 * to maintain consistency across components and services.
 */

// Activity details captured for each location
// Categorizes activities and tracks associated costs
export interface Activity {
  name: string;
  type: 'adventure' | 'relaxation' | 'wildlife' | 'cultural';
  estimated_cost: string; // e.g., "500 KES"
}

// Entry fee breakdown by visitor category
// Differentiates pricing for citizens, residents, and non-residents
export interface EntryFee {
  citizen: string;
  resident: string;
  non_resident: string;
}

// Daily cost estimates by travel tier
// Provides pricing for different budget levels (budget, mid-range, luxury)
export interface DailyCost {
  budget: string;
  mid: string;
  luxury: string;
}

// Available transportation methods to reach a location
// Tracks multiple transport options and associated costs
export interface TransportOption {
  type: 'road' | 'air' | 'train';
  estimated_cost: string;
}

// Complete location profile combining all location-related data
// Serves as the primary data structure for safari destinations
// Aggregates information about geography, activities, costs, transport, and environment
export interface Location {
  id: string;
  name: string;
  type: 'city' | 'park' | 'beach' | 'mountain' | 'forest';
  county: string;
  region: string;
  description: string;
  climate: string;
  best_time: string;
  activities: Activity[];
  entry_fee: EntryFee;
  estimated_daily_cost: DailyCost;
  transport_options: TransportOption[];
  nearby_locations: string[]; // array of location names or ids
  tags: string[];
}

// Individual message unit in the chat conversation
// Contains user inputs, assistant responses, and optional metadata like weather or budget
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  // optional structured data for rendering
  weather?: WeatherInfo;
  budget?: BudgetEstimate;
}

// Current weather conditions for a location
// Displayed in the chat interface and trip planning context
export interface WeatherInfo {
  location: string;
  temperature: number;
  condition: string; // e.g., "Rainy", "Sunny"
  humidity?: number;
  wind_speed?: number;
  icon?: string;
}

// Calculated budget breakdown for a safari trip
// Itemizes costs across all categories (accommodation, transport, activities, etc.)
// Supports multiple budget tiers and currency handling
export interface BudgetEstimate {
  daily_cost: {
    budget: number;
    mid: number;
    luxury: number;
  };
  accommodation: number;
  entry_fees: number;
  transport: number;
  activities: number;
  food: number;
  total: number;
  currency: 'KES';
}

// Payload structure for sending chat messages to the backend API
// Contains the user message and optional session identifier for conversation continuity
export interface ChatRequest {
  message: string;
  session_id?: string;
}

// Response payload returned from the chat API endpoint
// Includes the assistant's message and optional supplementary data for UI rendering
export interface ChatResponse {
  message: string;
  session_id: string;
  weather?: WeatherInfo;
  budget?: BudgetEstimate;
}

// Request structure for generating budget estimates
// Specifies the trip parameters needed to calculate costs
export interface EstimateRequest {
  location: string;
  days: number;
  budget_level: 'budget' | 'mid' | 'luxury';
}

// Response payload containing calculated budget estimate with detailed breakdown
// Extends BudgetEstimate with a narrative explanation from the LLM
export interface EstimateResponse extends BudgetEstimate {
  breakdown: string; // LLM explanation
}