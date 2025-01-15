import { error } from '@sveltejs/kit';

export function load() {
  const random = Math.random();
  
  if (random < 0.33) {
    throw error(404, 'Random 404 error');
  } else if (random < 0.66) {
    throw error(500, 'Random 500 error');
  }
  
  return {
    success: true,
    message: 'No error this time!'
  };
} 