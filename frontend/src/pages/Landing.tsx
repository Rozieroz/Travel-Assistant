import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChat } from '../hooks/useChat';
import type { Mode } from '../types';
import QuickSuggestions from '../components/ui/QuickSuggestions';

const MODES: { key: Mode; icon: string; title: string; tagline: string; desc: string; gradient: string; glow: string }[] = [
  {
    key: 'adventure',
    icon: '🦒',
    title: 'Discover Kenya',
    tagline: 'For the curious explorer',
    desc: 'Safari parks, pristine beaches, mountain treks, ancient cultures, and hidden gems — wherever your curiosity takes you.',
    gradient: 'linear-gradient(135deg, rgba(245,158,11,0.28), rgba(249,115,22,0.18))',
    glow: 'rgba(245,158,11,0.35)',
  },
  {
    key: 'everyday',
    icon: '☕',
    title: 'Everyday Kenya',
    tagline: 'For the good life, right here',
    desc: 'The best nyama choma joints, hidden coffee spots, weekend parks, date nights, and everything that makes living here special.',
    gradient: 'linear-gradient(135deg, rgba(16,185,129,0.28), rgba(5,150,105,0.18))',
    glow: 'rgba(16,185,129,0.35)',
  },
];

export default function Landing() {
  const navigate = useNavigate();
  const { setMode, sendMessage } = useChat();
  const [hovered, setHovered] = useState<Mode | null>(null);

  const handleCardClick = (m: Mode) => {
    setMode(m);
    navigate('/chat');
  };

  const handleChipClick = (prompt: string, m: Mode) => {
    setMode(m);
    sendMessage(prompt);
    navigate('/chat');
  };

  return (
    <div
      style={{
        height: '100%',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '32px 20px',
        gap: 40,
        fontFamily: 'var(--font)',
      }}
    >
      {/* Hero */}
      <div style={{ textAlign: 'center', animation: 'fade-up 0.6s ease forwards' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            background: 'rgba(245,158,11,0.18)',
            border: '1px solid rgba(245,158,11,0.35)',
            borderRadius: 'var(--radius-full)',
            padding: '6px 18px',
            fontSize: 12,
            fontWeight: 600,
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            color: '#FCD34D',
            marginBottom: 20,
          }}
        >
          🇰🇪 Your Kenya companion
        </div>

        <h1
          style={{
            fontSize: 'clamp(42px, 7vw, 76px)',
            fontWeight: 900,
            color: '#fff',
            lineHeight: 1.05,
            letterSpacing: '-0.02em',
            textShadow: '0 4px 40px rgba(0,0,0,0.5)',
            margin: '0 0 16px',
          }}
        >
          Karibu Kenya! 🇰🇪
        </h1>

        <p
          style={{
            fontSize: 'clamp(16px, 2.2vw, 20px)',
            color: 'rgba(255,255,255,0.8)',
            maxWidth: 520,
            lineHeight: 1.65,
            fontWeight: 300,
            margin: '0 auto',
          }}
        >
          Your friendly guide for adventures and local hangouts
        </p>
      </div>

      {/* Cards */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 20,
          justifyContent: 'center',
          width: '100%',
          maxWidth: 860,
          animation: 'fade-up 0.6s 0.15s ease forwards',
          opacity: 0,
          animationFillMode: 'forwards',
        }}
      >
        {MODES.map((m) => (
          <button
            key={m.key}
            onClick={() => handleCardClick(m.key)}
            onMouseEnter={() => setHovered(m.key)}
            onMouseLeave={() => setHovered(null)}
            aria-label={`Enter ${m.title} mode`}
            style={{
              flex: '1 1 300px',
              maxWidth: 380,
              padding: '32px 28px',
              background: hovered === m.key
                ? m.gradient.replace('0.28', '0.42').replace('0.18', '0.28')
                : m.gradient,
              backdropFilter: 'blur(20px)',
              border: `1px solid rgba(255,255,255,${hovered === m.key ? 0.28 : 0.16})`,
              borderRadius: 'var(--radius-lg)',
              cursor: 'pointer',
              textAlign: 'left',
              transform: hovered === m.key ? 'translateY(-10px) scale(1.02)' : 'translateY(0) scale(1)',
              transition: 'all 0.32s cubic-bezier(0.34,1.56,0.64,1)',
              boxShadow: hovered === m.key
                ? `0 28px 60px ${m.glow}, 0 8px 32px rgba(0,0,0,0.3)`
                : '0 8px 32px rgba(0,0,0,0.2)',
            }}
          >
            <div style={{ fontSize: 52, marginBottom: 14, lineHeight: 1 }}>{m.icon}</div>
            <div style={{ fontSize: 11, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.55)', marginBottom: 6, fontWeight: 600 }}>
              {m.tagline}
            </div>
            <h2 style={{ fontSize: 26, fontWeight: 800, color: '#fff', margin: '0 0 10px', lineHeight: 1.2 }}>
              {m.title}
            </h2>
            <p style={{ color: 'rgba(255,255,255,0.75)', lineHeight: 1.65, fontSize: 14, margin: 0 }}>
              {m.desc}
            </p>
            <div
              style={{
                marginTop: 22,
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                color: m.key === 'adventure' ? '#FCD34D' : '#6EE7B7',
                fontWeight: 700,
                fontSize: 14,
                transition: 'gap 0.2s',
              }}
            >
              Let's go {hovered === m.key ? '→→' : '→'}
            </div>
          </button>
        ))}
      </div>

      {/* Quick chips */}
      <div
        style={{
          textAlign: 'center',
          animation: 'fade-up 0.6s 0.28s ease forwards',
          opacity: 0,
          animationFillMode: 'forwards',
        }}
      >
        <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 12 }}>
          Popular right now
        </p>
        <QuickSuggestions mode="adventure" onSelect={(p) => handleChipClick(p, 'adventure')} />
      </div>

      {/* Footer */}
      <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12, textAlign: 'center', animation: 'fade-in 1s 0.5s ease forwards', opacity: 0, animationFillMode: 'forwards' }}>
        Powered by Safari Scouts AI · Made with ❤️ for Kenya
      </div>
    </div>
  );
}
