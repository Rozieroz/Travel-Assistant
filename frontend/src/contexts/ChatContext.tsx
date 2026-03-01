// ChatContext.tsx - Fixed version with better backend response handling
import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import type { Message, Mode, ChatState } from '../types';

interface ChatContextValue extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  setMode: (mode: Mode) => void;
  clearChat: () => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

// Use VITE_API_URL to match your .env file
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const SYSTEM_PROMPTS: Record<Mode, string> = {
  adventure: `You are Safari Scout 🦒, a warm and enthusiastic guide to Kenya's wonders. 
You help people discover Kenya's magic — from Maasai Mara safaris and Diani Beach sunsets to Mount Kenya hikes and Lamu's ancient streets. 
Give practical advice on costs, transport, safety, and hidden gems. 
Occasionally sprinkle Swahili phrases with translations for flavor. 
Keep responses friendly, informative, and concise (3–5 sentences). Use emojis naturally.`,

  everyday: `You are Safari Scout ☕, a friendly local guide who knows all the best spots across Kenya's cities and towns.
You help people find the best nyama choma joints, weekend parks, date night restaurants, family-friendly activities, coffee spots, and community events.
You're like that friend who always knows where to go — casual, warm, and full of great recommendations.
Use occasional Kenyan slang (poa, sawa, mtu) and keep things fun. 
Keep responses concise (3–5 sentences). Use emojis naturally.`,
};

const WELCOME_MESSAGES: Record<Mode, string> = {
  adventure: "Habari! 🦒 Ready to explore Kenya? Ask me about safaris, beaches, hiking trails, budgets, or anything else for an incredible adventure!",
  everyday: "Sawa sawa! ☕ Looking for your next favourite spot? Ask me about restaurants, parks, weekend hangouts, date nights, or fun things to do today!",
};

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [sessionId] = useState(() => {
    const stored = localStorage.getItem('safariScoutSessionId');
    if (stored) return stored;
    const newId = uuidv4();
    localStorage.setItem('safariScoutSessionId', newId);
    return newId;
  });
  
  const [mode, setModeState] = useState<Mode>('adventure');
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uuidv4(),
      role: 'assistant',
      content: WELCOME_MESSAGES['adventure'],
      timestamp: new Date(),
    },
  ]);
  const [isBackendAvailable, setIsBackendAvailable] = useState<boolean | null>(null);

  // Check if backend is available on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        console.log(`Checking backend at ${API_URL}...`);
        const res = await fetch(`${API_URL}/`, {
          method: 'GET',
          signal: AbortSignal.timeout(3000),
        });
        
        if (res.ok) {
          const data = await res.json();
          console.log('Backend response:', data);
          setIsBackendAvailable(true);
        } else {
          console.log(`Backend returned status ${res.status}`);
          setIsBackendAvailable(false);
        }
      } catch (error) {
        console.log(`Backend connection failed:`, error);
        setIsBackendAvailable(false);
      }
    };
    checkBackend();
  }, []);

  const setMode = useCallback((newMode: Mode) => {
    setModeState(newMode);
    setMessages([
      {
        id: uuidv4(),
        role: 'assistant',
        content: WELCOME_MESSAGES[newMode],
        timestamp: new Date(),
      },
    ]);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      let reply = '';

      // Try FastAPI backend first
      if (isBackendAvailable !== false) {
        try {
          console.log(`📤 Sending to backend: ${API_URL}/chat`, { 
            session_id: sessionId, 
            message: content.substring(0, 50) + '...' 
          });
          
          const res = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              session_id: sessionId, 
              message: content 
            }),
            signal: AbortSignal.timeout(15000), // 15 second timeout
          });

          console.log(`📥 Backend response status:`, res.status);

          if (res.ok) {
            const data = await res.json();
            console.log('📥 Backend response data:', data);
            
            // Check different possible response formats
            if (data.reply) {
              reply = data.reply;
              console.log('✅ Found reply field');
            } else if (data.response) {
              reply = data.response;
              console.log('✅ Found response field');
            } else if (data.message) {
              reply = data.message;
              console.log('✅ Found message field');
            } else if (typeof data === 'string') {
              reply = data;
              console.log('✅ Response is string');
            } else {
              console.log('❌ No recognizable reply field in response:', Object.keys(data));
              // Try to stringify the whole response as fallback
              reply = JSON.stringify(data);
            }
            
            setIsBackendAvailable(true);
          } else {
            const errorText = await res.text();
            console.error('❌ Backend error:', res.status, errorText);
            setIsBackendAvailable(false);
          }
        } catch (error) {
          console.error('❌ Backend connection failed:', error);
          setIsBackendAvailable(false);
        }
      } else {
        console.log('⚠️ Backend marked as unavailable, skipping...');
      }

      // If backend succeeded with a reply, use it
      if (reply) {
        console.log('✅ Using backend response');
        const assistantMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: reply,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      } 
      // If backend failed or returned empty, show a friendly error
      else {
        console.log('❌ No response from backend');
        
        

        // If still no reply, show error message
        if (!reply) {
          if (isBackendAvailable === false) {
            reply = 'Pole! 🌍 I cannot reach the Kenya travel server. Please make sure the backend is running at port 8000. Try:\n\n```bash\ncd backend\nuvicorn main:app --reload --port 8000\n```';
          } else if (isBackendAvailable === true) {
            reply = 'Pole! 🙏 The server responded but I couldn\'t understand the reply. Please try again or check the backend logs.';
          } else {
            reply = 'Pole! 🙏 I\'m having trouble connecting. Please check that your backend is running and try again.';
          }
        }

        const assistantMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: reply,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
      
    } catch (error) {
      console.error('💥 Fatal error in sendMessage:', error);
      
      setMessages(prev => [
        ...prev,
        {
          id: uuidv4(),
          role: 'assistant',
          content: 'Pole! Something went wrong. Please try again 🙏',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }, [messages, mode, sessionId, isBackendAvailable]);

  const clearChat = useCallback(() => {
    setMessages([
      {
        id: uuidv4(),
        role: 'assistant',
        content: WELCOME_MESSAGES[mode],
        timestamp: new Date(),
      },
    ]);
  }, [mode]);

  return (
    <ChatContext.Provider value={{ 
      messages, 
      mode, 
      sessionId, 
      isTyping, 
      sendMessage, 
      setMode, 
      clearChat 
    }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error('useChat must be used within ChatProvider');
  return ctx;
}