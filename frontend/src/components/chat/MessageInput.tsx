// MessageInput.tsx ---  provides a styled textarea input for users to type their messages, along with a send button. It handles user input, auto-growing the textarea, and sending messages on button click or pressing Enter. The component also manages disabled state and visual feedback for interactivity.

import React, { useState, useRef, useCallback } from 'react';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function MessageInput({ onSend, disabled = false, placeholder }: MessageInputProps) {
  const [value, setValue] = useState('');
  const [hovered, setHovered] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [value, disabled, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    // Auto-grow
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  };

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-end',
        gap: 10,
        padding: '10px 14px 10px 18px',
        background: 'rgba(255,255,255,0.1)',
        backdropFilter: 'blur(20px)',
        border: `1px solid rgba(255,255,255,${hovered ? 0.3 : 0.18})`,
        borderRadius: 20,
        transition: 'border-color 0.2s',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder || 'Ask me anything about Kenya...'}
        disabled={disabled}
        rows={1}
        aria-label="Type your message"
        style={{
          flex: 1,
          background: 'transparent',
          border: 'none',
          outline: 'none',
          resize: 'none',
          color: '#fff',
          fontSize: 15,
          lineHeight: 1.5,
          maxHeight: 120,
          overflowY: 'auto',
          scrollbarWidth: 'none',
          opacity: disabled ? 0.5 : 1,
        }}
      />

      {/* Send button */}
      <button
        onClick={handleSend}
        disabled={!canSend}
        aria-label="Send message"
        style={{
          width: 44,
          height: 44,
          borderRadius: '50%',
          border: 'none',
          background: canSend
            ? 'linear-gradient(135deg, #F59E0B, #F97316)'
            : 'rgba(255,255,255,0.15)',
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 18,
          flexShrink: 0,
          transition: 'var(--transition)',
          boxShadow: canSend ? 'var(--shadow-glow-orange)' : 'none',
          transform: canSend ? 'scale(1)' : 'scale(0.92)',
          cursor: canSend ? 'pointer' : 'not-allowed',
        }}
        onMouseEnter={(e) => {
          if (canSend) (e.currentTarget as HTMLButtonElement).style.transform = 'scale(1.1)';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.transform = canSend ? 'scale(1)' : 'scale(0.92)';
        }}
      >
        {disabled ? '⏳' : '➤'}
      </button>
    </div>
  );
}
