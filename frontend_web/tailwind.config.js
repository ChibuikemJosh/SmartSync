/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        mobile: '0 24px 60px rgba(0,0,0,0.18)',
      },
      colors: {
        forest: '#0F5257',
        amber: '#FFB100',
        paper: '#F8F9FA',
      },
    },
  },
  plugins: [],
};
