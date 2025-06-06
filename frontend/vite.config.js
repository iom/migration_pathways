// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react-swc'

// // https://vite.dev/config/
// export default defineConfig({
//   server: {
//     port: 8509,
//     host: '0.0.0.0'
//   },
//   plugins: [react()],
// })

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  server: {
    port: 8509,
    host: '0.0.0.0',
    allowedHosts: [
      'localhost',
      '*.azurewebsites.net'
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8510',
        changeOrigin: true,
        secure: false
      }
    }
  },
  plugins: [react()],
})
