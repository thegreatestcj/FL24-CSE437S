/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',  // Django template files in templates folder
    './**/templates/**/*.html',  // If you have multiple app-specific templates
    './static/js/**/*.js',    // Your JS files if you use Tailwind classes in JS
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

