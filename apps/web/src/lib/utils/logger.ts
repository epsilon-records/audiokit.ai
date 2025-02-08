/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import pino from 'pino';

// Rename the Pino instance to avoid conflict
const pinoLogger = pino({
  // Basic configuration
  level: process.env.LOG_LEVEL || 'info',

  // Timestamp configuration
  timestamp: () => `,"time":"${new Date().toISOString()}"`,

  // Message formatting
  messageKey: 'message',

  formatters: {
    level: (label) => ({ level: label }),
    bindings: (bindings) => ({
      vercel: {
        deploymentId: process.env.VERCEL_GIT_COMMIT_SHA,
        deploymentURL: process.env.VERCEL_URL,
        environment: process.env.VERCEL_ENV,
        projectId: process.env.VERCEL_PROJECT_ID,
        projectName: process.env.VERCEL_PROJECT_NAME,
        region: process.env.VERCEL_REGION,
        route: process.env.VERCEL_ROUTE,
        source: process.env.VERCEL_GIT_REPO_SLUG,
      },
    }),
  },

  // Custom serializers
  serializers: {
    error: pino.stdSerializers.err,
    request: (req) => ({
      id: req.id,
      host: req.headers['host'],
      ip: req.headers['x-forwarded-for'] || req.socket.remoteAddress,
      method: req.method,
      path: req.url,
      scheme: req.protocol,
      statusCode: req.statusCode,
      userAgent: req.headers['user-agent'],
      vercelCache: req.headers['x-vercel-cache'],
    }),
    response: (res) => ({
      statusCode: res.statusCode,
    }),
    data: (data) => data, // Add data serializer
    context: (context) => context, // Add context serializer
    report: (report) => ({
      durationMs: report?.durationMs,
      maxMemoryUsedMb: report?.maxMemoryUsedMb,
    }),
  },

  transport: {
    target: process.env.NODE_ENV === 'development' ? 'pino-pretty' : 'pino/file',
    options: {
      colorize: true,
      translateTime: 'SYS:standard',
      ignore: 'pid,hostname',
      messageFormat: '{message}',
      singleLine: true,
      destination: 1,
    },
  },
});

// Create a production logger that uses console.log
const productionLogger = {
  info: (data: any) => console.log(JSON.stringify(data, null, 2)),
  warn: (data: any) => console.warn(JSON.stringify(data, null, 2)),
  error: (data: any) => console.error(JSON.stringify(data, null, 2)),
};

// Choose logger based on environment
const activeLogger = process.env.NODE_ENV === 'development' ? pinoLogger : productionLogger;

// Updated logging functions
const logStart = (requestId: string, message: string, context?: any) => {
  activeLogger.info({
    request: { id: requestId },
    message: `🚀 ${message}`,
    ...context,
  });
};

const logDataRetrieval = (requestId: string, msg: string, data?: any, context?: any) => {
  activeLogger.info({
    request: { id: requestId },
    message: `📥 ${msg}`,
    data,
    ...context,
  });
};

const logProcessing = (requestId: string, msg: string, details?: any, context?: any) => {
  activeLogger.info({
    request: { id: requestId },
    message: `🔄 ${msg}`,
    details,
    ...context,
  });
};

const logSuccess = (
  requestId: string,
  message: string,
  result?: any,
  report?: any,
  context?: any
) => {
  activeLogger.info({
    request: { id: requestId },
    message: `✅ ${message}`,
    result,
    report,
    ...context,
  });
};

const logWarning = (requestId: string, msg: string, context?: any) => {
  activeLogger.warn({
    request: { id: requestId },
    message: `⚠️ ${msg}`,
    ...context,
  });
};

const logError = (requestId: string, msg: string, error: Error, context?: any) => {
  activeLogger.error({
    request: { id: requestId },
    message: `❌ ${msg}`,
    error: {
      message: error.message,
      stack: error.stack,
    },
    ...context,
  });
};

const logCompletion = (requestId: string, msg: string, stats: any, context?: any) => {
  activeLogger.info({
    request: { id: requestId },
    message: `🎉 ${msg}`,
    stats,
    ...context,
  });
};

// Export the logging functions as the primary interface
const logger = {
  start: logStart,
  data: logDataRetrieval,
  process: logProcessing,
  success: logSuccess,
  warning: logWarning,
  error: logError,
  complete: logCompletion,
};

// Deprecate direct logger export
export default logger;
