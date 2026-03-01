// defines shared TypeScript types used across the frontend application, ensuring type safety and consistency in data structures.

export type Mode = 'adventure' | 'everyday';
export type Currency = 'KES' | 'USD' | 'BOTH';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatState {
  messages: Message[];
  mode: Mode;
  sessionId: string;
  isTyping: boolean;
  currency: Currency;

}

export interface ChatContextValue extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  setMode: (mode: Mode) => void;
  clearChat: () => void;
}

export interface WeatherData {
  city: string;
  temp: string;
  condition: string;
  icon: string;
}

export interface QuickSuggestion {
  label: string;
  icon: string;
  prompt: string;
}

// for API types
export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
}

export interface WeatherRequest {
  location: string;
  days?: number;
}

export interface WeatherResponse {
  location: string;
  weather: string;
}

export interface EstimateRequest {
  location: string;
  days: number;
  budget_level: 'budget' | 'mid' | 'luxury';
}

export interface EstimateResponse {
  location: string;
  days: number;
  budget_level: string;
  estimate: string;
}

export interface WeatherInfo {
  location: string;
  weather: string;
  timestamp?: string;
}

