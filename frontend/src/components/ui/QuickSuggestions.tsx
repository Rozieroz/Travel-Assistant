import React, { useState } from 'react';
import type { Mode, QuickSuggestion } from '../../types';

const SUGGESTIONS: Record<Mode, QuickSuggestion[]> = {
  adventure: [
    { icon: '🦁', label: 'Best safaris', prompt: 'What are the best safari experiences in Kenya and how much do they cost?' },
    { icon: '🏖️', label: 'Beach getaway', prompt: 'Tell me about the best beaches in Kenya — Diani, Watamu, Lamu?' },
    { icon: '🎒', label: '3-day budget', prompt: 'Plan a 3-day budget trip to Kenya for under $200' },
    { icon: '🏔️', label: 'Mt. Kenya hike', prompt: 'How do I plan a hike up Mount Kenya? What should I know?' },
    { icon: '📸', label: 'Photo spots', prompt: 'What are the most photogenic places in Kenya for photography?' },
  ],
  everyday: [
    { icon: '🍖', label: 'Nyama choma', prompt: 'Where are the best nyama choma spots in Nairobi?' },
    { icon: '👨‍👩‍👧', label: 'Kids activities', prompt: 'What are fun kid-friendly activities in Nairobi this weekend?' },
    { icon: '💑', label: 'Date night', prompt: 'Suggest a great date night spot in Nairobi — something romantic and special' },
    { icon: '☕', label: 'Coffee spots', prompt: 'What are the best coffee shops in Nairobi to work or hang out?' },
    { icon: '🎉', label: 'Free events', prompt: 'What free or affordable events are happening in Nairobi this weekend?' },
  ],
};

interface QuickSuggestionsProps {
  mode: Mode;
  onSelect: (prompt: string) => void;
  small?: boolean;
}

export default function QuickSuggestions({ mode, onSelect, small = false }: QuickSuggestionsProps) {
  const [hovered, setHovered] = useState<number | null>(null);

  return (
    <div
      style={{
        display: 'flex',
        gap: 8,
        flexWrap: 'wrap',
        justifyContent: 'center',
      }}
      role="list"
      aria-label="Quick suggestions"
    >
      {SUGGESTIONS[mode].map((s, i) => (
        <button
          key={`${mode}-${i}`}
          role="listitem"
          onClick={() => onSelect(s.prompt)}
          onMouseEnter={() => setHovered(i)}
          onMouseLeave={() => setHovered(null)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: small ? '6px 12px' : '8px 16px',
            borderRadius: 'var(--radius-full)',
            border: `1px solid ${hovered === i ? 'rgba(245,158,11,0.5)' : 'rgba(255,255,255,0.2)'}`,
            background: hovered === i ? 'rgba(245,158,11,0.18)' : 'rgba(255,255,255,0.08)',
            backdropFilter: 'blur(8px)',
            color: hovered === i ? '#FCD34D' : 'rgba(255,255,255,0.82)',
            fontSize: small ? 12 : 13,
            fontWeight: 500,
            transition: 'all 0.2s ease',
            whiteSpace: 'nowrap',
          }}
          aria-label={`Quick suggestion: ${s.label}`}
        >
          <span style={{ fontSize: small ? 13 : 15 }}>{s.icon}</span>
          {s.label}
        </button>
      ))}
    </div>
  );
}
