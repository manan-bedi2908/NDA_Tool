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
        background: "var(--background)",
        foreground: "var(--foreground)",
        secondary: {
          DEFAULT: "var(--secondary-accent)",
          text: "var(--secondary-text)",
          accent: "var(--secondary-accent)",
          light: "var(--secondary-light)",
        },
        muted: {
          DEFAULT: "var(--muted)",
          text: "var(--muted-text)",
        },
        primary: {
          DEFAULT: "var(--primary-accent)",
          hover: "var(--primary-hover)",
          light: "var(--primary-light)",
        },
        warning: {
          DEFAULT: "var(--warning)",
          light: "var(--warning-light)",
        },
        error: {
          DEFAULT: "var(--error)",
          light: "var(--error-light)",
        },
        success: {
          DEFAULT: "var(--success)",
          light: "var(--success-light)",
        },
        info: {
          DEFAULT: "var(--info)",
          light: "var(--info-light)",
        },
        border: {
          DEFAULT: "var(--border)",
          light: "var(--border-light)",
        },
        surface: {
          DEFAULT: "var(--surface)",
          hover: "var(--surface-hover)",
          secondary: "var(--surface-secondary)",
        },
      },
      boxShadow: {
        'sm': 'var(--shadow-sm)',
        'md': 'var(--shadow-md)',
        'lg': 'var(--shadow-lg)',
        'xl': 'var(--shadow-xl)',
      },
    },
  },
  plugins: [],
};
export default config;
