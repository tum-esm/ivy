const balancedSlate = {
  50: " hsl(210,30%,97.5%)",
  100: "hsl(210,30%,92.5%)",
  150: "hsl(210,30%,87.5%)",
  200: "hsl(210,30%,82.5%)",
  250: "hsl(210,30%,77.5%)",
  300: "hsl(210,30%,72.5%)",
  350: "hsl(210,30%,67.5%)",
  400: "hsl(210,30%,62.5%)",
  450: "hsl(210,30%,57.5%)",
  500: "hsl(210,30%,52.5%)",
  550: "hsl(210,30%,47.5%)",
  600: "hsl(210,30%,42.5%)",
  650: "hsl(210,30%,37.5%)",
  700: "hsl(210,30%,32.5%)",
  750: "hsl(210,30%,27.5%)",
  800: "hsl(210,30%,22.5%)",
  850: "hsl(210,30%,17.5%)",
  900: "hsl(210,30%,12.5%)",
  950: "hsl(210,30%,7.5%)",
};

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./theme.config.jsx",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ["var(--next-font-google-crimson-pro)", "serif"],
      },
      fontSize: {
        "2xs": ["0.625rem", "0.75rem"],
      },
      colors: {
        slate: balancedSlate,
        balancedSlate: balancedSlate,
      },
    },
  },
  plugins: [],
  darkMode: "class",
};
