// ModeToggle.tsx ---  provides a toggle switch component that allows users to switch between "Adventure" and "Everyday" modes in the application. Each mode is represented with a distinct icon and label, and the active mode is visually highlighted with a gradient background and shadow effect. The component is designed to be compact or full-sized based on the `compact` prop, making it versatile for different UI contexts. It also includes accessibility features such as ARIA attributes for better screen reader support.

import React from 'react';
import type { Mode } from '../../types';

interface ModeToggleProps {
  mode: Mode;
  onChange: (mode: Mode) => void;
  compact?: boolean;
}

const MODES: { key: Mode; icon: string; label: string; short: string }[] = [
  { key: 'adventure', icon: '🦒', label: 'Adventure', short: 'Adventure' },
  { key: 'everyday', icon: '☕', label: 'Everyday', short: 'Everyday' },
];

export default function ModeToggle({ mode, onChange, compact = false }: ModeToggleProps) {
  return (
    <div
      style={{
        display: 'inline-flex',
        background: 'rgba(0,0,0,0.35)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(255,255,255,0.15)',
        borderRadius: 'var(--radius-full)',
        padding: 4,
        gap: 2,
      }}
      role="group"
      aria-label="Switch mode"
    >
      {MODES.map((m) => {
        const isActive = mode === m.key;
        const bg = isActive
          ? m.key === 'adventure'
            ? 'linear-gradient(135deg, #F59E0B, #F97316)'
            : 'linear-gradient(135deg, #10B981, #059669)'
          : 'transparent';

        return (
          <button
            key={m.key}
            onClick={() => onChange(m.key)}
            aria-pressed={isActive}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: compact ? '6px 14px' : '8px 20px',
              borderRadius: 'var(--radius-full)',
              border: 'none',
              background: bg,
              color: isActive ? '#fff' : 'rgba(255,255,255,0.5)',
              fontWeight: isActive ? 700 : 500,
              fontSize: compact ? 12 : 13,
              transition: 'var(--transition)',
              boxShadow: isActive
                ? m.key === 'adventure'
                  ? 'var(--shadow-glow-orange)'
                  : 'var(--shadow-glow-green)'
                : 'none',
              whiteSpace: 'nowrap',
            }}
          >
            <span style={{ fontSize: compact ? 14 : 16 }}>{m.icon}</span>
            {compact ? m.short : m.label}
          </button>
        );
      })}
    </div>
  );
}
