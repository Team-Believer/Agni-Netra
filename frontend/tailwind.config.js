/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        surface: "#FFFFFF",
        border: "#E2E8F0",
        brand: {
          50: "#FFF7ED",
          100: "#FFEDD5",
          500: "#F97316",
          600: "#EA580C",
          700: "#C2410C",
        },
        priority: {
          critical: "#DC2626",
          high: "#EA580C",
          medium: "#D97706",
          low: "#16A34A",
          monitor: "#2563EB",
        }
      },
    },
  },
  plugins: [],
}
