/** @type {import('tailwindcss').Config} */
module.exports = {
  presets: [require("nativewind/preset")],
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  // No darkMode key — light-theme only by default. See ../../_shared-mobile/states-and-motion.md.
  theme: {
    extend: {
      colors: {
        // Neutral placeholder brand — swap per project.
        brandBlue: {
          50: "#E6F4FE",
          100: "#CFEAFC",
          500: "#1F6F8B",
          600: "#1A5F77",
          700: "#154E62",
        },
        ink: {
          50: "#F8FAFC",
          100: "#F1F5F9",
          200: "#E2E8F0",
          300: "#CBD5E1",
          500: "#64748B",
          700: "#334155",
          900: "#0F172A",
        },
      },
    },
  },
  plugins: [],
};
