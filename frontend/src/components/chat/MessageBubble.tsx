// MessageBubble.tsx ---  renders individual chat messages as styled bubbles, differentiating between user and assistant messages with distinct styles and animations. It also formats the timestamp for display.

import React from 'react';
import type { Message } from '../../types';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-KE', { hour: '2-digit', minute: '2-digit' });
  };

  if (isUser) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'flex-end',
          marginBottom: 12,
          animation: 'slide-in-right 0.3s ease forwards',
        }}
      >
        <div style={{ maxWidth: '72%', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4 }}>
          <div
            style={{
              padding: '12px 18px',
              background: 'linear-gradient(135deg, #F59E0B, #F97316)',
              borderRadius: '20px 20px 4px 20px',
              color: '#fff',
              fontSize: 15,
              lineHeight: 1.6,
              fontWeight: 400,
              boxShadow: '0 4px 20px rgba(249,115,22,0.35)',
            }}
          >
            {message.content}
          </div>
          <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.45)' }}>
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'flex-start',
        alignItems: 'flex-end',
        gap: 8,
        marginBottom: 12,
        animation: 'slide-in-left 0.35s ease forwards',
      }}
    >
      {/* Avatar */}
      <div
        style={{
          width: 34,
          height: 34,
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #F59E0B, #EF4444)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 16,
          flexShrink: 0,
          boxShadow: 'var(--shadow-glow-orange)',
        }}
        aria-hidden="true"
      >
        🦒
      </div>

      <div style={{ maxWidth: '72%', display: 'flex', flexDirection: 'column', gap: 4 }}>
        <div
          style={{
            padding: '12px 18px',
            background: 'rgba(255,255,255,0.14)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255,255,255,0.22)',
            borderRadius: '20px 20px 20px 4px',
            color: '#fff',
            fontSize: 15,
            lineHeight: 1.7,
            boxShadow: '0 4px 24px rgba(0,0,0,0.2)',
          }}
        >
          {message.content}
        </div>
        <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginLeft: 4 }}>
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}
