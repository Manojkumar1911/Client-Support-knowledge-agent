/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./src/Components/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      animation: {
        'pulse': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      backgroundColor: {
        'white/80': 'rgba(255, 255, 255, 0.8)',
        'white/50': 'rgba(255, 255, 255, 0.5)',
        'slate-900/80': 'rgba(15, 23, 42, 0.8)',
        'slate-800/50': 'rgba(30, 41, 59, 0.5)',
      },
      borderColor: {
        'white/20': 'rgba(255, 255, 255, 0.2)',
        'purple-500/20': 'rgba(168, 85, 247, 0.2)',
      },
    },
  },
  plugins: [],
}