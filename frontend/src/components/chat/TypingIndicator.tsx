// TypingIndicator.tsx ---  renders a typing indicator in the chat interface when the assistant is generating a response. It features an animated avatar and bouncing dots to visually indicate that the assistant is "typing". The component is styled with a modern, semi-transparent design and includes accessibility features for screen readers. It also uses CSS animations for a smooth and engaging user experience while waiting for the assistant's reply.

import React from 'react';

export default function TypingIndicator() {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, marginBottom: 12, animation: 'fade-in 0.3s ease' }}>
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

      {/* Dots */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 5,
          padding: '12px 18px',
          background: 'rgba(255,255,255,0.14)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255,255,255,0.2)',
          borderRadius: '20px 20px 20px 4px',
        }}
        role="status"
        aria-label="Safari Scout is typing"
      >
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: '#F59E0B',
              animation: 'bounce-dot 1.2s infinite',
              animationDelay: `${i * 0.18}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
}
