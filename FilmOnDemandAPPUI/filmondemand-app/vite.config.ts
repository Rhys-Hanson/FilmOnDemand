import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig, loadEnv} from 'vite';

export default defineConfig(({mode}) => {
  const env = loadEnv(mode, '.', '');
  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      // Expose on LAN so phones can reach the dev server via the QR code URL
      host: true,
      // Serve index.html for all routes (e.g. /join/:roomCode) so React handles routing
      historyApiFallback: true,
    },
  };
});
