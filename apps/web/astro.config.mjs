import react from '@astrojs/react';

/** @type {import('astro').AstroUserConfig} */
export default {
  integrations: [react()],
  server: {
    host: '127.0.0.1',
    port: 4321,
  },
};


