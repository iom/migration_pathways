import react from '@vitejs/plugin-react-swc'
import { defineConfig } from 'vitest/config'

export default defineConfig({
        plugins: [react()],
        test: {
                setupFiles: './setupTests.js',
                environment: 'jsdom',
                globals: true
        },
})
