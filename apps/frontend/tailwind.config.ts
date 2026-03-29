import type { Config } from 'tailwindcss';
import { tailwindExtend } from './src/styles/theme';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      ...tailwindExtend,
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #81ecff, #00e3fd)',
        'gradient-secondary': 'linear-gradient(135deg, #ac89ff, #7000ff)',
        'gradient-tertiary': 'linear-gradient(135deg, #aeffd4, #00feb1)',
        'gradient-surface': 'linear-gradient(180deg, #141a1f, #0a0f13)',
      },
      backdropBlur: {
        glass: '24px',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease forwards',
        'slide-up': 'slideUp 0.5s ease forwards',
        'score-fill': 'scoreFill 1s ease forwards',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scoreFill: {
          '0%': { strokeDashoffset: '283' },
          '100%': { strokeDashoffset: 'var(--score-offset)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(129, 236, 255, 0.1)' },
          '50%': { boxShadow: '0 0 30px rgba(129, 236, 255, 0.25)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
