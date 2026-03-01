import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChat } from '../hooks/useChat';
import MessageList from '../components/chat/MessageList';
import MessageInput from '../components/chat/MessageInput';
import ModeToggle from '../components/ui/ModeToggle';
import QuickSuggestions from '../components/ui/QuickSuggestions';
import SidePanel from '../components/chat/SidePanel';

export default function Chat() {
  const navigate = useNavigate();
  const { messages, isTyping, mode, setMode, sendMessage, clearChat } = useChat();
  const [showSidePanel, setShowSidePanel] = useState(true);

  const inputPlaceholders: Record<typeof mode, string> = {
    adventure: 'Ask about safaris, beaches, budgets, hikes...',
    everyday: 'Ask about restaurants, hangouts, events, parks...',
  };

  return (
    <div
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        fontFamily: 'var(--font)',
      }}
    >
      {/* Header */}
      <header
        className="glass-dark"
        style={{
          padding: '12px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexShrink: 0,
          zIndex: 20,
          gap: 12,
        }}
      >
        {/* Left: logo + back */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            onClick={() => navigate('/')}
            aria-label="Back to home"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: 'rgba(255,255,255,0.1)',
              border: '1px solid rgba(255,255,255,0.18)',
              borderRadius: 'var(--radius-full)',
              padding: '6px 14px',
              color: 'rgba(255,255,255,0.8)',
              fontSize: 12,
              fontWeight: 500,
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.18)'; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.1)'; }}
          >
            ← Back
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div
              style={{
                width: 38,
                height: 38,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #F59E0B, #EF4444)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 20,
                boxShadow: 'var(--shadow-glow-orange)',
                flexShrink: 0,
              }}
              aria-hidden="true"
            >
              🦒
            </div>
            <div>
              <div style={{ color: '#fff', fontWeight: 700, fontSize: 15, lineHeight: 1.1 }}>Safari Scouts</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#10B981', boxShadow: '0 0 6px rgba(16,185,129,0.8)' }} />
                <span style={{ color: '#6EE7B7', fontSize: 11, fontWeight: 500 }}>Online</span>
              </div>
            </div>
          </div>
        </div>

        {/* Center: mode toggle */}
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
          <ModeToggle mode={mode} onChange={setMode} compact />
        </div>

        {/* Right: actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            onClick={clearChat}
            aria-label="Clear chat"
            title="Clear chat"
            style={{
              background: 'rgba(255,255,255,0.08)',
              border: '1px solid rgba(255,255,255,0.15)',
              borderRadius: 8,
              padding: '6px 10px',
              color: 'rgba(255,255,255,0.6)',
              fontSize: 14,
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.color = '#fff'; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.color = 'rgba(255,255,255,0.6)'; }}
          >
            🗑️
          </button>

          <button
            onClick={() => setShowSidePanel(!showSidePanel)}
            aria-label={showSidePanel ? 'Hide side panel' : 'Show side panel'}
            title="Toggle panel"
            style={{
              display: 'none', // shown via media query below — we handle via inline for demo
              background: 'rgba(255,255,255,0.08)',
              border: '1px solid rgba(255,255,255,0.15)',
              borderRadius: 8,
              padding: '6px 10px',
              color: 'rgba(255,255,255,0.6)',
              fontSize: 14,
            }}
          >
            📋
          </button>
        </div>
      </header>

      {/* Body */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Chat area */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <MessageList messages={messages} isTyping={isTyping} />

          {/* Bottom input area */}
          <div
            className="glass-dark"
            style={{
              flexShrink: 0,
              padding: '10px 16px 16px',
              borderTop: '1px solid rgba(255,255,255,0.1)',
            }}
          >
            <div style={{ maxWidth: 720, margin: '0 auto' }}>
              {/* Chips */}
              <div style={{ marginBottom: 10 }}>
                <QuickSuggestions mode={mode} onSelect={sendMessage} small />
              </div>

              {/* Input */}
              <MessageInput
                onSend={sendMessage}
                disabled={isTyping}
                placeholder={inputPlaceholders[mode]}
              />
            </div>
          </div>
        </div>

        {/* Side panel — hidden on narrow screens via responsive trick */}
        <div
          className="glass-dark"
          style={{
            borderLeft: '1px solid rgba(255,255,255,0.1)',
            display: 'flex',
            flexShrink: 0,
          }}
          aria-label="Side panel"
        >
          <SidePanel onSendMessage={sendMessage} />
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          [aria-label="Side panel"] { display: none !important; }
        }
      `}</style>
    </div>
  );
}
