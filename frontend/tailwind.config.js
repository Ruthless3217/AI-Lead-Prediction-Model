/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            colors: {
                slate: {
                    50: '#f8fafc',
                    100: '#f1f5f9',
                    200: '#e2e8f0',
                    300: '#cbd5e1',
                    400: '#94a3b8',
                    500: '#64748b',
                    600: '#475569',
                    700: '#334155',
                    800: '#1e293b',
                    900: '#0f172a',
                    950: '#020617',
                },
                indigo: {
                    50: '#eef2ff',
                    100: '#e0e7ff',
                    200: '#c7d2fe',
                    300: '#a5b4fc',
                    400: '#818cf8',
                    500: '#6366f1',
                    600: '#4f46e5',
                    700: '#4338ca',
                    800: '#3730a3',
                    900: '#312e81',
                    950: '#1e1b4b',
                },
                primary: {
                    DEFAULT: '#005EAC',
                    foreground: '#ffffff',
                    50: '#f0f9ff',
                    100: '#e0f2fe',
                    200: '#bae6fd',
                    300: '#7dd3fc',
                    400: '#38bdf8',
                    500: '#0ea5e9',
                    600: '#005EAC', // Main Brand Color
                    700: '#014b8d',
                    800: '#073e70',
                    900: '#0c3459',
                    950: '#08223c',
                },
                secondary: {
                    DEFAULT: '#f1f5f9', // Slate 100
                    foreground: '#0f172a', // Slate 900
                },
                accent: {
                    DEFAULT: '#f8fafc', // Slate 50
                    foreground: '#0f172a',
                },
                muted: {
                    DEFAULT: '#f1f5f9', // Slate 100
                    foreground: '#64748b', // Slate 500
                },
                destructive: {
                    DEFAULT: '#ef4444', // Red 500
                    foreground: '#ffffff',
                },
                border: '#e2e8f0', // Slate 200
                input: '#e2e8f0', // Slate 200
                ring: '#4f46e5', // Indigo 600
                background: '#ffffff',
                foreground: '#0f172a', // Slate 900
            },
            boxShadow: {
                'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                'DEFAULT': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
                'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
                'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -2px rgb(0 0 0 / 0.05)',
                'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.05)',
            }
        },
    },
    plugins: [],
}
