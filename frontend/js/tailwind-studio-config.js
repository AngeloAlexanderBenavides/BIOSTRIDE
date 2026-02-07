tailwind.config = {
    theme: {
        fontFamily: {
            sans: ['Nunito', 'sans-serif'],
        },
        extend: {
            colors: {
                // Official Google Palette
                'g-blue': '#4285F4',
                'g-red': '#EA4335',
                'g-yellow': '#FBBC05',
                'g-green': '#34A853',
                'aura-bg': '#F8F9FA',
            },
            animation: {
                'float': 'float 6s ease-in-out infinite',
                'float-delayed': 'float 6s ease-in-out 3s infinite',
                'gradient-x': 'gradient-x 3s ease infinite',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-20px)' },
                },
                'gradient-x': {
                    '0%, 100%': {
                        'background-size': '200% 200%',
                        'background-position': 'left center'
                    },
                    '50%': {
                        'background-size': '200% 200%',
                        'background-position': 'right center'
                    },
                },
            }
        }
    }
}
