/** @type {import('astro').AstroUserConfig} */
export default {
  output: 'static',
  base: process.env.PUBLIC_BASE_PATH || '/',
  server: {
    host: true,
    port: 4321,
  },
  vite: {
    server: {
      proxy: {
        '/health': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
        '/v1': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  },
};


