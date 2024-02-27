/** @type {import('tailwindcss').Config}*/
const config = {
  content: [
    './src/**/*.{html,js,svelte,ts}',
    './node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}',
    './node_modules/flowbite-svelte-icons/**/*.{html,js,svelte,ts}'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // flowbite-svelte
        primary: {
          50: '#f5f5fa',
          100: '#f0f0f5',
          200: '#ccccf0',
          300: '#9999db',
          400: '#6666b6',
          500: '#5c57f2',
          600: '#303060',
          700: '#262653',
          800: '#1d1d46',
          900: '#131339'
        },
        'theme-orchid': '#c04bf2',
        'theme-blue': '#5c57f2',
        'theme-charcoal': '#2a4359',
        'theme-skyblue': '#05c7f2',
        'theme-orange': '#f27405',
        'theme-stale-grey': '#6b7e92',
        'theme-stale-light-grey': '#aeb8c2',
        'theme-stale-light-grey-2': '#cbd8e1',
        'theme-light-grey': '#f2f2f2'
      }
    }
  },
  plugins: [require('flowbite/plugin'), require('tailwind-scrollbar', { nocompatible: true })]
};

module.exports = config;
