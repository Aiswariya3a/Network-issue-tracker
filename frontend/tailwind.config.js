/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#1E88E5",
        primaryDark: "#1565C0",
        primaryLight: "#64B5F6",
        accentRed: "#E53935",
        bgLight: "#F5F7FA",
        success: "#16A34A",
        warning: "#F59E0B",
        danger: "#DC2626",
        cardBorder: "#E5E7EB"
      },
      fontFamily: {
        sans: ["Inter", "Poppins", "ui-sans-serif", "system-ui", "sans-serif"],
        poppins: ["Poppins", "ui-sans-serif", "system-ui", "sans-serif"]
      },
      boxShadow: {
        soft: "0 8px 24px rgba(21, 101, 192, 0.08)"
      },
      borderRadius: {
        xl2: "12px"
      }
    }
  },
  plugins: []
};
