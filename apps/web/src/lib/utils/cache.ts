/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import { LRUCache } from 'lru-cache';

interface CacheOptions {
  ttl: number; // in milliseconds
  maxSize: number; // in bytes
}

export function createCache<T>(name: string, options: CacheOptions) {
  return new LRUCache<string, T>({
    max: options.maxSize,
    ttl: options.ttl,
    allowStale: false,
    updateAgeOnGet: true,
    updateAgeOnHas: true,
    sizeCalculation: (value) => {
      // Calculate size in bytes
      if (typeof value === 'string') {
        return Buffer.byteLength(value, 'utf8');
      }
      return Buffer.byteLength(JSON.stringify(value), 'utf8');
    },
    // Explicitly set maxSize in bytes
    maxSize: options.maxSize,
  });
}
