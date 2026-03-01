/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        safari: {
          primary: "#F59E0B",
          secondary: "#10B981",
          accent: "#3B82F6",
          earth: "#8B5A2B",
          cream: "#FEF3C7",
        }
      },
      fontFamily: {
        friendly: ['Poppins', 'sans-serif'],
      },
      animation: {
        'bounce-slow': 'bounce 1.5s infinite',
        'pulse-slow': 'pulse 3s infinite',
        'float': 'float 3s ease-in-out infinite',
        'typing': 'typing 1.5s infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        typing: {
          '0%, 60%, 100%': { transform: 'translateY(0px)' },
          '30%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}