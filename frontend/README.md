# Safari Scouts 🦒

A friendly AI travel and local guide for Kenya.

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## Modes

| Mode | Who it's for |
|------|-------------|
| 🦒 **Discover Kenya** | Anyone who wants to explore — safaris, beaches, hikes, budgets |
| ☕ **Everyday Kenya** | Anyone who wants great local spots — food, parks, date nights, events |

## API

The app falls back to the Anthropic API directly if the backend is unavailable.

Set `VITE_BACKEND_URL` in `.env` to point to your backend:
- `POST /chat` — `{ session_id, message }` → `{ response }`
- `GET /weather?location=Nairobi` → `{ city, temp, condition, icon }`
- `POST /estimate` — `{ location, days, budget_level }` → itinerary

## Stack

- React 18 + TypeScript + Vite
- React Router v6
- Poppins font (Google Fonts)
- Anthropic API (claude-sonnet-4-20250514)
