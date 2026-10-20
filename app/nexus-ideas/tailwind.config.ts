import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: { sans: ['Open Sans', 'sans-serif'] },
      colors: {
        cth: {
          blue: '#0C498A',
          cyan: '#B2EEFA',
          green: '#9DC384',
          forest: '#669348',
          sky: '#69B5FA',
        },
      },
    },
  },
  plugins: [],
};

export default config;
