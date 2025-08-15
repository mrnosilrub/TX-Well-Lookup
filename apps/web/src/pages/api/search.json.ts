import type { APIRoute } from 'astro';
import fs from 'node:fs';
import path from 'node:path';

// Load canonical stub from repo fixture so web and API can share one source
function loadStubItems(): unknown[] {
  try {
    const fixturePath = path.resolve(process.cwd(), '..', '..', 'data', 'fixtures', 'wells_stub.json');
    const fileContents = fs.readFileSync(fixturePath, 'utf-8');
    const parsed = JSON.parse(fileContents);
    return Array.isArray(parsed?.items) ? parsed.items : Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

const items = loadStubItems();

export const GET: APIRoute = () => {
  return new Response(JSON.stringify({ items }), {
    headers: { 'Content-Type': 'application/json' },
  });
};

export const prerender = true;


