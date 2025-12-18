/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // OPAL brand colors derived from the logo
        opal: {
          // Navy blue (primary)
          navy: '#1a365d',
          'navy-light': '#2c5282',
          'navy-dark': '#0f2744',
          // Purple accent
          purple: '#6b46c1',
          'purple-light': '#805ad5',
          'purple-dark': '#553c9a',
          // Magenta/Pink accent
          magenta: '#d53f8c',
          'magenta-light': '#ed64a6',
          'magenta-dark': '#b83280',
          // Teal accent
          teal: '#319795',
          'teal-light': '#38b2ac',
          'teal-dark': '#285e61',
          // Gold accent
          gold: '#d69e2e',
          'gold-light': '#ecc94b',
          'gold-dark': '#b7791f',
          // Neutral grays
          50: '#f7fafc',
          100: '#edf2f7',
          200: '#e2e8f0',
          300: '#cbd5e0',
          400: '#a0aec0',
          500: '#718096',
          600: '#4a5568',
          700: '#2d3748',
          800: '#1a202c',
          900: '#171923',
        },
      },
      backgroundImage: {
        'opal-gradient': 'linear-gradient(135deg, #1a365d 0%, #2c5282 50%, #319795 100%)',
        'opal-gradient-light': 'linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%)',
      },
    },
  },
  plugins: [],
}
