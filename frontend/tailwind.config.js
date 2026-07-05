/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        owe: {
          bg: '#F6FBFA',
          surface: '#FFFFFF',
          accent: '#0F766E',
          accentLight: '#14B8A6',
          text: '#0F172A',
          muted: '#64748B',
          primary: '#0F766E',
          secondary: '#14B8A6',
          aqua: '#99F6E4',
          cyan: '#D2F4EF',
          card: '#FFFFFF',
          border: '#DCEFED',
          textPrimary: '#0F172A',
          textSecondary: '#475569',
          textMuted: '#94A3B8',
          success: '#22C55E',
          warning: '#F59E0B',
          danger: '#EF4444',
        }
      },
      boxShadow: {
        'soft': '0 10px 30px -10px rgba(15, 118, 110, 0.04), 0 1px 3px rgba(15, 118, 110, 0.02)',
        'premium': '0 20px 40px -15px rgba(15, 118, 110, 0.07), 0 1px 5px rgba(15, 118, 110, 0.03)',
      }
    },
  },
  plugins: [],
}
