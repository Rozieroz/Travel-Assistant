import { useState, useEffect } from 'react';
import type { WeatherData } from '../types';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// Mock weather data for when backend is unavailable
const MOCK_WEATHER: WeatherData[] = [
  { city: 'Nairobi', temp: '22°C', condition: 'Partly Cloudy', icon: '⛅' },
  { city: 'Mombasa', temp: '29°C', condition: 'Sunny', icon: '☀️' },
  { city: 'Kisumu', temp: '26°C', condition: 'Warm', icon: '🌤️' },
];

export function useWeather(location?: string) {
  const [weather, setWeather] = useState<WeatherData[]>(MOCK_WEATHER);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchWeather = async () => {
      setLoading(true);
      try {
        const cities = location ? [location] : ['Nairobi', 'Mombasa', 'Kisumu'];
        const results = await Promise.all(
          cities.map(async (city) => {
            const res = await fetch(`${BACKEND_URL}/weather?location=${encodeURIComponent(city)}`, {
              signal: AbortSignal.timeout(4000),
            });
            if (!res.ok) throw new Error('fetch failed');
            return res.json() as Promise<WeatherData>;
          })
        );
        setWeather(results);
      } catch {
        setWeather(MOCK_WEATHER);
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
  }, [location]);

  return { weather, loading };
}
