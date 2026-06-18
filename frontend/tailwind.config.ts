import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Backgrounds
        bg:      "#FAFAF8",
        bg2:     "#F4F3EF",
        bg3:     "#EEECEA",
        
        // Surfaces
        surface: "#FFFFFF",
        surface2:"#FDFCFB",
        
        // Primary — Coral Red (refined terracotta)
        coral: {
          50:  "#FFF5F3",
          100: "#FFE8E3",
          200: "#FFC9BE",
          300: "#FFA090",
          400: "#FF7260",
          500: "#E8523A",
          600: "#C4391E",
          700: "#A32D16",
          800: "#82230F",
          900: "#5E1A0A",
        },
        
        // Navy — text & structure  
        navy: {
          50:  "#F0F2F7",
          100: "#D8DDE9",
          200: "#A8B3CA",
          300: "#7485A8",
          400: "#4A5D87",
          500: "#2D4068",
          600: "#1E2E52",
          700: "#162240",
          800: "#0F1830",
          900: "#080F20",
        },
        
        // Warm gray text
        slate: {
          50:  "#F8F7F5",
          100: "#EEECE8",
          200: "#D8D4CC",
          300: "#B8B2A8",
          400: "#948E84",
          500: "#726C62",
          600: "#565049",
          700: "#3D3932",
          800: "#282420",
          900: "#161310",
        },
        
        // Teal — complementary accent
        teal: {
          400: "#2DD4C0",
          500: "#0FBFAA",
          600: "#0A9E8E",
        },
        
        // Amber — warmth
        amber: {
          400: "#FBBF24",
          500: "#F59E0B",
          600: "#D97706",
        },
      },
      
      fontFamily: {
        display: ["var(--font-bricolage)", "system-ui", "sans-serif"],
        body:    ["var(--font-inter)", "system-ui", "sans-serif"],
        mono:    ["var(--font-jetbrains)", "Menlo", "monospace"],
      },
      
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "1rem", letterSpacing: "0.05em" }],
      },
      
      boxShadow: {
        "card":    "0 1px 3px rgba(0,0,0,0.05), 0 4px 16px rgba(0,0,0,0.06)",
        "card-md": "0 2px 8px rgba(0,0,0,0.06), 0 8px 32px rgba(0,0,0,0.08)",
        "card-lg": "0 4px 16px rgba(0,0,0,0.08), 0 16px 48px rgba(0,0,0,0.10)",
        "coral":   "0 4px 20px rgba(196,57,30,0.20)",
        "coral-lg":"0 8px 32px rgba(196,57,30,0.25)",
        "teal":    "0 4px 16px rgba(11,191,170,0.20)",
        "inner":   "inset 0 1px 3px rgba(0,0,0,0.06)",
      },
      
      borderRadius: {
        "2xl": "16px",
        "3xl": "24px",
        "4xl": "32px",
      },
      
      animation: {
        "fade-up":    "fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) both",
        "fade-in":    "fadeIn 0.4s ease both",
        "slide-in":   "slideIn 0.4s cubic-bezier(0.16,1,0.3,1) both",
        "shimmer":    "shimmer 2s linear infinite",
        "pulse-dot":  "pulseDot 2s ease-in-out infinite",
        "bounce-sm":  "bounceSm 0.6s cubic-bezier(0.36,0.07,0.19,0.97) both",
        "progress":   "progress 1.5s cubic-bezier(0.16,1,0.3,1) both",
      },
      
      keyframes: {
        fadeUp: {
          "0%":   { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideIn: {
          "0%":   { opacity: "0", transform: "translateX(-12px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% center" },
          "100%": { backgroundPosition: "200% center" },
        },
        pulseDot: {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(11,191,170,0.5)" },
          "50%":       { boxShadow: "0 0 0 6px rgba(11,191,170,0)" },
        },
        bounceSm: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%":       { transform: "translateY(-4px)" },
        },
        progress: {
          "0%":   { width: "0%" },
          "100%": { width: "var(--progress-width, 0%)" },
        },
      },
      
      transitionTimingFunction: {
        "spring": "cubic-bezier(0.16, 1, 0.3, 1)",
      },
    },
  },
  plugins: [],
};

export default config;