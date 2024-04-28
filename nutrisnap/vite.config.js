import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath } from 'url';
import path from 'path';

// Resolve the path to the src directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcPath = path.resolve(__dirname, 'src');

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  server: {
    port: 5001 // Set the port to 5001 for the frontend
  },
  resolve: {
    alias: {
      '@': srcPath // Use the resolved path to the src directory
    }
  },
  html: {
    title: 'NutriSnap'
  }
});
