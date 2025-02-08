/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import Bottleneck from 'bottleneck';
import { serializeError } from 'serialize-error';
import logger from '../../utils/logger.js';

export class BaseIntegration {
  protected limiter: Bottleneck;
  protected serviceName: string;

  constructor(serviceName: string, rateLimit: number, windowMs: number) {
    this.serviceName = serviceName;
    this.limiter = new Bottleneck({
      minTime: windowMs / rateLimit,
      maxConcurrent: 1,
      reservoir: rateLimit,
      reservoirRefreshInterval: windowMs,
      reservoirRefreshAmount: rateLimit,
      trackDoneStatus: true,
    });
  }

  protected async makeRequest<T>(
    requestId: string,
    requestFn: () => Promise<T>,
    context: Record<string, unknown> = {}
  ): Promise<T | null> {
    const startTime = Date.now();
    logger.start(requestId, `Starting ${this.serviceName} API request`, context);

    try {
      const result = await this.limiter.schedule(() => requestFn());
      logger.success(requestId, `Successfully completed ${this.serviceName} API request`, {
        ...context,
        duration: Date.now() - startTime,
      });
      return result;
    } catch (err) {
      const serializedError = serializeError(err) as Error;
      logger.error(requestId, `Error in ${this.serviceName} API request`, serializedError, {
        ...context,
        duration: Date.now() - startTime,
      });
      return null;
    }
  }
}
