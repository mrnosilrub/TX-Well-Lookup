import type { APIRoute } from 'astro';
import { wells as items } from '../../lib/stubWells';

export const GET: APIRoute = () => {
  return new Response(JSON.stringify({ items }), {
    headers: { 'Content-Type': 'application/json' },
  });
};

export const prerender = true;


