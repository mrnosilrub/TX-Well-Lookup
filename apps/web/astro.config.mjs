/** @type {import('astro').AstroUserConfig} */
export default {
  output: 'static',
  base: process.env.PUBLIC_BASE_PATH || '/',
  server: { host: true },
};


