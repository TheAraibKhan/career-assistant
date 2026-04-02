/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}", "./static/**/*.{js,css}"],
  theme: {
    extend: {
      colors: {
        "dark-primary": "#050505",
        "dark-secondary": "#0a0a0a",
        "dark-tertiary": "#111111",
        "neon-purple": "#a855f7",
        "neon-pink": "#ec4899",
        "neon-gold": "#fbbf24",
        glass: "rgba(255,255,255,0.04)",
        "glass-hover": "rgba(255,255,255,0.08)",
      },
      backgroundColor: {
        glass: "rgba(255,255,255,0.04)",
        "glass-dark": "rgba(0,0,0,0.3)",
      },
      fontSize: {
        display: ["4rem", { lineHeight: "1.2", fontWeight: "700" }],
        "display-lg": ["5rem", { lineHeight: "1.1", fontWeight: "700" }],
        "heading-xl": ["3rem", { lineHeight: "1.2", fontWeight: "700" }],
        "heading-lg": ["2.25rem", { lineHeight: "1.3", fontWeight: "700" }],
        heading: ["1.875rem", { lineHeight: "1.3", fontWeight: "700" }],
        subheading: ["1.25rem", { lineHeight: "1.4", fontWeight: "600" }],
        "body-lg": ["1.125rem", { lineHeight: "1.5", fontWeight: "400" }],
        body: ["1rem", { lineHeight: "1.6", fontWeight: "400" }],
        small: ["0.875rem", { lineHeight: "1.5", fontWeight: "400" }],
        tiny: ["0.75rem", { lineHeight: "1.5", fontWeight: "500" }],
      },
      fontFamily: {
        display: ["Playfair Display", "serif"],
        body: ["Inter", "sans-serif"],
      },
      backdropBlur: {
        xs: "2px",
        sm: "4px",
        md: "12px",
        lg: "16px",
        xl: "20px",
      },
      boxShadow: {
        glow: "0 0 20px rgba(168, 85, 247, 0.3)",
        "glow-pink": "0 0 30px rgba(236, 72, 153, 0.3)",
        "glow-gold": "0 0 30px rgba(251, 191, 36, 0.2)",
        "glow-lg": "0 0 40px rgba(168, 85, 247, 0.4)",
        glass: "0 8px 32px 0 rgba(31, 38, 135, 0.15)",
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        glow: "glow 3s ease-in-out infinite",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "slide-up": "slideUp 0.6s ease-out",
        "fade-in": "fadeIn 0.6s ease-out",
        "scroll-reveal": "scrollReveal 0.8s ease-out",
        "bounce-soft": "bounceSoft 2s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-20px)" },
        },
        glow: {
          "0%, 100%": { boxShadow: "0 0 20px rgba(168, 85, 247, 0.3)" },
          "50%": { boxShadow: "0 0 40px rgba(168, 85, 247, 0.6)" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.8" },
          "50%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(30px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        scrollReveal: {
          "0%": { transform: "translateY(40px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        bounceSoft: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
      },
      backgroundImage: {
        "gradient-purple":
          "linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #fbbf24 100%)",
        "gradient-dark":
          "linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%)",
      },
    },
  },
  plugins: [
    function ({ addUtilities }) {
      const newUtilities = {
        ".glass-effect": {
          background: "rgba(255, 255, 255, 0.04)",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
        },
        ".glass-effect-dark": {
          background: "rgba(0, 0, 0, 0.3)",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
        },
        ".gradient-text": {
          backgroundImage:
            "linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #fbbf24 100%)",
          backgroundClip: "text",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        },
        ".gradient-text-alt": {
          backgroundImage: "linear-gradient(135deg, #ec4899 0%, #a855f7 100%)",
          backgroundClip: "text",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        },
        ".blur-glass": {
          background: "rgba(255, 255, 255, 0.04)",
          backdropFilter: "blur(16px)",
        },
      };
      addUtilities(newUtilities);
    },
  ],
};
