import { defineConfig } from 'vite';
import basicSsl from '@vitejs/plugin-basic-ssl';

export default defineConfig({
  plugins: [
    // Generates a self-signed cert on the fly to bypass Facebook's HTTPS requirement
    basicSsl()
  ],
  server: {
    port: 5173,
    https: true, // Force HTTPS
  }
});
