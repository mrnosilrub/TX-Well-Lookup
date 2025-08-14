import tailwind from "@astrojs/tailwind";

/**** Astro config ****/
/** SSR optional later via adapters; dev uses preview server */
export default {
  integrations: [tailwind({ applyBaseStyles: true })],
  server: { host: true }
};