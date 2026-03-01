import React from 'react';
import { useChat } from '../../contexts/ChatContext';

export default function CurrencyToggle() {
  const { currency, setCurrency } = useChat();

  return (
    <div className="flex bg-gray-100 rounded-full p-1">
      <button
        onClick={() => setCurrency('KES')}
        className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
          currency === 'KES'
            ? 'bg-safari-primary text-white'
            : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        KES 🇰🇪
      </button>
      <button
        onClick={() => setCurrency('USD')}
        className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
          currency === 'USD'
            ? 'bg-safari-primary text-white'
            : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        USD 💵
      </button>
      <button
        onClick={() => setCurrency('BOTH')}
        className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
          currency === 'BOTH'
            ? 'bg-safari-primary text-white'
            : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        Both
      </button>
    </div>
  );
}