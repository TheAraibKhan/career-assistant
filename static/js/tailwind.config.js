// CareerAssist Tailwind v3 Configuration
// Added via CDN <script> tag — no build step needed
tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        display: ['Poppins', 'Inter', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        deep: {
          DEFAULT: '#0a0a1a',
          50: '#0d0d22',
          100: '#10102a',
          200: '#151535',
          300: '#1a1a40',
        },
        neon: {
          purple: '#8b5cf6',
          blue: '#3b82f6',
          cyan: '#06b6d4',
          green: '#10b981',
          pink: '#ec4899',
          gold: '#f59e0b',
        },
        glass: {
          DEFAULT: 'rgba(255,255,255,0.03)',
          light: 'rgba(255,255,255,0.05)',
          medium: 'rgba(255,255,255,0.08)',
          border: 'rgba(255,255,255,0.06)',
        },
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.25rem',
        '4xl': '1.5rem',
      },
      boxShadow: {
        'glow-sm': '0 4px 20px rgba(139,92,246,0.15)',
        'glow-md': '0 8px 40px rgba(139,92,246,0.2)',
        'glow-lg': '0 12px 60px rgba(139,92,246,0.3)',
        'glow-purple': '0 0 30px rgba(139,92,246,0.25)',
        'glow-blue': '0 0 30px rgba(59,130,246,0.2)',
        'glow-cyan': '0 0 30px rgba(6,182,212,0.2)',
        '3d': '0 20px 60px -12px rgba(0,0,0,0.5)',
        '3d-sm': '0 10px 30px -8px rgba(0,0,0,0.4)',
      },
      backgroundImage: {
        'grad-primary': 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
        'grad-accent': 'linear-gradient(135deg, #ec4899, #8b5cf6)',
        'grad-hero': 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 50%, #06b6d4 100%)',
        'grad-success': 'linear-gradient(135deg, #10b981, #06b6d4)',
        'grad-warm': 'linear-gradient(135deg, #f59e0b, #ec4899)',
        'grad-dark': 'linear-gradient(135deg, #0a0a1a, #151530)',
        'grad-glass': 'linear-gradient(135deg, rgba(139,92,246,0.08), rgba(59,130,246,0.05))',
        'mesh-1': 'radial-gradient(at 20% 80%, rgba(139,92,246,0.15) 0%, transparent 50%), radial-gradient(at 80% 20%, rgba(59,130,246,0.1) 0%, transparent 50%)',
        'mesh-2': 'radial-gradient(at 50% 0%, rgba(236,72,153,0.12) 0%, transparent 50%), radial-gradient(at 80% 80%, rgba(6,182,212,0.08) 0%, transparent 50%)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-slow': 'float 8s ease-in-out infinite',
        'float-fast': 'float 4s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 3s ease-in-out infinite',
        'slide-up': 'slide-up 0.6s ease-out',
        'slide-up-delay': 'slide-up 0.6s ease-out 0.15s both',
        'slide-up-delay-2': 'slide-up 0.6s ease-out 0.3s both',
        'fade-in': 'fade-in 0.8s ease-out',
        'spin-slow': 'spin 20s linear infinite',
        'gradient-shift': 'gradient-shift 8s ease infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-15px)' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(139,92,246,0.15)' },
          '50%': { boxShadow: '0 0 40px rgba(139,92,246,0.35)' },
        },
        'slide-up': {
          from: { opacity: '0', transform: 'translateY(30px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'gradient-shift': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
      perspective: {
        '1000': '1000px',
        '1500': '1500px',
        '2000': '2000px',
      },
    },
  },
};
