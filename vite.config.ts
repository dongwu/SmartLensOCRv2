import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
      // Development server configuration: use Vite default port (5173)
      // but allow running on all interfaces for device testing.
      server: {
        port: Number(env.VITE_PORT) || 5173,
        host: '0.0.0.0',
      },
      plugins: [react()],
      // Do NOT expose sensitive keys here. Frontend should use VITE_ prefixed
      // environment variables (e.g. VITE_API_URL) accessed via import.meta.env.
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
