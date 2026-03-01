// SidePanel.tsx ---  displays a side panel in the chat interface that shows current weather information for key locations in Kenya, a quick trip planner form for users to generate travel itineraries based on their preferences, and the current local time in Nairobi. It fetches weather data using a custom hook and allows users to send a message to the chat assistant to plan their trip based on selected criteria. The component is styled with a modern, semi-transparent design to complement the overall UI of the application.

import React, { useState } from 'react';
import { useWeather } from '../../hooks/useWeather';

interface SidePanelProps {
  onSendMessage: (msg: string) => void;
}

export default function SidePanel({ onSendMessage }: SidePanelProps) {
  const { weather, loading } = useWeather();
  const [days, setDays] = useState('3');
  const [budget, setBudget] = useState('medium');
  const [interest, setInterest] = useState('');

  const handlePlan = () => {
    if (!interest.trim()) return;
    onSendMessage(
      `Plan a ${days}-day ${budget}-budget trip to Kenya focused on ${interest}. Give me an itinerary with cost estimates.`
    );
  };

  const sectionStyle: React.CSSProperties = {
    background: 'rgba(255,255,255,0.07)',
    backdropFilter: 'blur(12px)',
    border: '1px solid rgba(255,255,255,0.14)',
    borderRadius: 'var(--radius-md)',
    padding: '16px',
    marginBottom: 12,
  };

  const labelStyle: React.CSSProperties = {
    fontSize: 11,
    letterSpacing: '0.12em',
    textTransform: 'uppercase',
    color: 'rgba(255,255,255,0.5)',
    fontWeight: 600,
    marginBottom: 10,
    display: 'block',
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    background: 'rgba(255,255,255,0.1)',
    border: '1px solid rgba(255,255,255,0.18)',
    borderRadius: 8,
    padding: '8px 12px',
    color: '#fff',
    fontSize: 13,
    outline: 'none',
  };

  return (
    <div
      style={{
        width: 260,
        flexShrink: 0,
        overflowY: 'auto',
        padding: '16px 12px',
        scrollbarWidth: 'thin',
        scrollbarColor: 'rgba(255,255,255,0.15) transparent',
      }}
    >
      {/* Weather */}
      <div style={sectionStyle}>
        <span style={labelStyle}>🌤 Kenya Weather</span>
        {loading ? (
          <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 13 }}>Loading...</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {weather.map((w) => (
              <div key={w.city} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ color: '#fff', fontWeight: 600, fontSize: 13 }}>{w.city}</div>
                  <div style={{ color: 'rgba(255,255,255,0.55)', fontSize: 11 }}>{w.condition}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <span style={{ fontSize: 18 }}>{w.icon}</span>
                  <span style={{ color: '#FCD34D', fontWeight: 700, fontSize: 14 }}>{w.temp}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick planner */}
      <div style={sectionStyle}>
        <span style={labelStyle}>🗺 Quick Planner</span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div>
            <label style={{ ...labelStyle, marginBottom: 4 }}>Days</label>
            <select
              value={days}
              onChange={(e) => setDays(e.target.value)}
              style={{ ...inputStyle, cursor: 'pointer' }}
            >
              {['1','2','3','5','7','10','14'].map(d => (
                <option key={d} value={d} style={{ background: '#1a1a1a' }}>{d} day{parseInt(d) > 1 ? 's' : ''}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ ...labelStyle, marginBottom: 4 }}>Budget</label>
            <select
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              style={{ ...inputStyle, cursor: 'pointer' }}
            >
              <option value="budget" style={{ background: '#1a1a1a' }}>💰 Budget</option>
              <option value="medium" style={{ background: '#1a1a1a' }}>💳 Mid-range</option>
              <option value="luxury" style={{ background: '#1a1a1a' }}>✨ Luxury</option>
            </select>
          </div>

          <div>
            <label style={{ ...labelStyle, marginBottom: 4 }}>Interest</label>
            <input
              type="text"
              value={interest}
              onChange={(e) => setInterest(e.target.value)}
              placeholder="e.g. safari, beach..."
              style={inputStyle}
              onKeyDown={(e) => e.key === 'Enter' && handlePlan()}
            />
          </div>

          <button
            onClick={handlePlan}
            disabled={!interest.trim()}
            style={{
              padding: '10px',
              borderRadius: 8,
              border: 'none',
              background: interest.trim()
                ? 'linear-gradient(135deg, #F59E0B, #F97316)'
                : 'rgba(255,255,255,0.1)',
              color: '#fff',
              fontWeight: 700,
              fontSize: 13,
              cursor: interest.trim() ? 'pointer' : 'not-allowed',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => { if (interest.trim()) (e.currentTarget as HTMLButtonElement).style.transform = 'scale(1.02)'; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.transform = 'scale(1)'; }}
          >
            Plan my trip ✨
          </button>
        </div>
      </div>

      {/* Kenya time */}
      <div style={{ ...sectionStyle, textAlign: 'center' }}>
        <span style={labelStyle}>🕐 Nairobi Time (EAT)</span>
        <div style={{ color: '#FCD34D', fontWeight: 700, fontSize: 20 }}>
          {new Date().toLocaleTimeString('en-KE', {
            timeZone: 'Africa/Nairobi',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
        <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11, marginTop: 4 }}>UTC+3</div>
      </div>
    </div>
  );
}
