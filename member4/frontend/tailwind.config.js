/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        darkbg: "#080c14",
        cardbg: "#101622",
        cyberblue: "#00d8ff",
        cybergreen: "#00ff66",
        cyberred: "#ff3b30",
        cyberamber: "#ff9500"
      }
    },
  },
  plugins: [],
}
