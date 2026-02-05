import { defineConfig } from 'vite';

export default defineConfig({
    server: {
        proxy: {
            '/nodes': 'http://localhost:8000',
            '/logs': 'http://localhost:8000',
            '/graph': 'http://localhost:8000',
        },
    },
    build: {
        outDir: 'dist',
        assetsDir: 'assets',
    }
});
