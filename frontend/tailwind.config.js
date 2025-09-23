/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ['class'],
    content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
  	extend: {
  		colors: {
  			primary: {
  				light: '#5F9EA0',
  				DEFAULT: '#4682B4',
  				dark: '#2F4F4F'
  			},
  			secondary: {
  				light: '#87CEEB',
  				DEFAULT: '#4682B4',
  				dark: '#4682B4'
  			},
  			accent: {
  				light: '#90EE90',
  				DEFAULT: '#32CD32',
  				dark: '#228B22'
  			},
  			background: {
  				light: '#F0F8FF',
  				DEFAULT: '#87CEEB',
  				dark: '#4682B4'
  			}
  		},
  		keyframes: {
  			'accordion-down': {
  				from: {
  					height: '0'
  				},
  				to: {
  					height: 'var(--radix-accordion-content-height)'
  				}
  			},
  			'accordion-up': {
  				from: {
  					height: 'var(--radix-accordion-content-height)'
  				},
  				to: {
  					height: '0'
  				}
  			}
  		},
  		animation: {
  			'accordion-down': 'accordion-down 0.2s ease-out',
  			'accordion-up': 'accordion-up 0.2s ease-out'
  		}
  	}
  },
  plugins: [],
}