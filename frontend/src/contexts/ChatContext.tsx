// src/contexts/ChatContext.tsx
import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import type { Message, Mode, ChatState, Currency } from '../types';

interface ChatContextValue extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  setMode: (mode: Mode) => void;
  setCurrency: (currency: Currency) => void;
  clearChat: () => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

// Make sure this matches your backend URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const WELCOME_MESSAGES: Record<Mode, string> = {
  adventure: "Habari! 🦒 Ready to explore Kenya? Ask me about safaris, beaches, hiking trails, budgets, or anything else for an incredible adventure!",
  everyday: "Karibu ☕ Looking for your next favourite spot? Ask me about restaurants, parks, weekend hangouts, date nights, or fun things to do today!",
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
  const [currency, setCurrencyState] = useState<Currency>('KES'); // Moved inside component
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

  // Check backend on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        console.log(`Checking backend at: ${API_URL}`);
        const res = await fetch(`${API_URL}/`, {
          method: 'GET',
          signal: AbortSignal.timeout(5000),
        });
        
        if (res.ok) {
          console.log(' Backend is reachable');
          setIsBackendAvailable(true);
        } else {
          console.log('❌ Backend returned error:', res.status);
          setIsBackendAvailable(false);
        }
      } catch (error) {
        console.log('❌ Backend connection failed:', error);
        setIsBackendAvailable(false);
      }
    };
    checkBackend();
  }, []);

  const setMode = useCallback((newMode: Mode) => {
    console.log('Setting mode to:', newMode);
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

  const setCurrency = useCallback((newCurrency: Currency) => {
    console.log('Setting currency to:', newCurrency);
    setCurrencyState(newCurrency);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    console.log('Sending message:', content);
    console.log('Backend URL:', API_URL);
    console.log('Backend available:', isBackendAvailable);
    console.log('Current currency:', currency);

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      // Try to send to backend
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          session_id: sessionId, 
          message: content,
          currency: currency // Send currency preference to backend
        }),
        signal: AbortSignal.timeout(10000),
      });

      console.log('Response status:', res.status);

      if (res.ok) {
        const data = await res.json();
        console.log(' Response data:', data);
        
        const reply = data.reply || '';
        
        const assistantMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: reply,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorText = await res.text();
        console.error('❌ Backend error:', res.status, errorText);
        
        // Fallback message
        const assistantMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: 'Pole! I had trouble connecting. Check your internet and try again 🙏',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('❌ Fetch error:', error);
      
      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: 'Pole! I had trouble connecting. Check your internet and try again 🙏',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [sessionId, isBackendAvailable, currency]);

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
      currency,  
      setCurrency,
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