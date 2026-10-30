/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ide: {
          bg: '#0d1117',
          surface: '#161b22',
          card: '#21262d',
          border: '#30363d',
          text: '#c9d1d9',
          muted: '#8b949e',
          accent: '#58a6ff',
          success: '#3fb950',
          warning: '#d29922',
          danger: '#f85149',
          purple: '#bc8cff'
        }
      }
    },
  },
  plugins: [],
}
