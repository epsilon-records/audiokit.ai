import { LRUCache } from 'lru-cache';

interface CacheOptions {
  ttl: number;
  maxSize: number;
}

export function createCache<T>(name: string, options: CacheOptions) {
  return new LRUCache<string, T>({
    max: options.maxSize,
    ttl: options.ttl,
    allowStale: false,
    updateAgeOnGet: true,
    updateAgeOnHas: true,
    sizeCalculation: (value) => JSON.stringify(value).length,
  });
}
