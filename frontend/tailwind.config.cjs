/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        violet: { 50:'#F6F3FF', 200:'#DDD2FB', 300:'#C4B5FD', 500:'#7C3AED', 600:'#6D28D9', 900:'#1E1B4B' },
        ember:  { 300:'#FDBA74', 500:'#F97316', 600:'#EA580C' },
        paper:  { DEFAULT:'#FAF7F2', deep:'#F1ECE1' },
        ink:    { DEFAULT:'#2A1E4A', soft:'#5B4E7A' },
        night:  { DEFAULT:'#17122E', deeper:'#0F0B22', card:'#221B42' },
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
      },
      fontFamily: {
        sans:    ['"LXGW WenKai"', 'ui-serif', 'serif'],
        display: ['"DingTalk JinBuTi"', '"LXGW WenKai"', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      keyframes: {
        rise:   { from:{ opacity:'0', transform:'translateY(14px)' }, to:{ opacity:'1', transform:'translateY(0)' } },
        float:  { '0%,100%':{ transform:'translateY(0) rotate(-1deg)' }, '50%':{ transform:'translateY(-6px) rotate(1deg)' } },
        flicker:{ '0%,100%':{ transform:'scale(1) rotate(-2deg)' }, '50%':{ transform:'scale(1.08) rotate(2deg)' } },
        twinkle:{ '0%,100%':{ opacity:'.2', transform:'scale(.8)' }, '50%':{ opacity:'1', transform:'scale(1.2)' } },
        thought:{ '0%,100%':{ transform:'translateY(0)' }, '50%':{ transform:'translateY(-3px)' } },
        slideUp:{ from:{ transform:'translateY(100%)' }, to:{ transform:'translateY(0)' } },
        rollup: { from:{ transform:'translateY(40%)', opacity:'0' }, to:{ transform:'translateY(0)', opacity:'1' } },
        waveJump:{ '0%,100%':{ transform:'scaleY(.4)' }, '50%':{ transform:'scaleY(1.4)' } },
      },
      animation: {
        'rise':     'rise .8s cubic-bezier(.2,1.4,.3,1) both',
        'float':    'float 4.5s ease-in-out infinite',
        'flicker':  'flicker 1.6s ease-in-out infinite',
        'twinkle':  'twinkle 2.6s ease-in-out infinite',
        'thought':  'thought 3.2s ease-in-out infinite',
        'slide-up': 'slideUp .5s cubic-bezier(.2,1.4,.3,1) both',
        'rollup':   'rollup .9s cubic-bezier(.2,1.4,.3,1) both',
        'wave-jump':'waveJump 1s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
