import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
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
        source: process.env.VERCEL_SOURCE,
      },
    }),
  },
  timestamp: () => `,"timestamp":"${new Date().toISOString()}"`,
  messageKey: 'message',
  serializers: {
    err: (err) => ({
      ...pino.stdSerializers.err(err),
      report: {
        durationMs: err.duration,
        maxMemoryUsedMb: err.memory,
      },
    }),
    req: (req) => ({
      request: {
        host: req.hostname,
        id: req.id,
        ip: req.ip,
        method: req.method,
        path: req.url,
        scheme: req.protocol,
        statusCode: req.statusCode,
        userAgent: req.headers['user-agent'],
        vercelCache: req.headers['x-vercel-cache'],
      },
    }),
  },
  base: {
    vercel: {
      deploymentId: process.env.VERCEL_GIT_COMMIT_SHA,
      deploymentURL: process.env.VERCEL_URL,
      environment: process.env.VERCEL_ENV,
      projectId: process.env.VERCEL_PROJECT_ID,
      projectName: process.env.VERCEL_PROJECT_NAME,
      region: process.env.VERCEL_REGION,
      route: process.env.VERCEL_ROUTE,
      source: process.env.VERCEL_SOURCE,
    },
  },
  transport:
    process.env.NODE_ENV === 'development'
      ? {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: true,
            ignore: 'pid,hostname',
          },
        }
      : {
          target: 'pino/file',
          options: {
            destination: 1,
            colorize: true,
            translateTime: true,
            ignore: 'pid,hostname',
          },
        },
});

// Example usage:
// logger.info({
//   report: {
//     durationMs: 120,
//     maxMemoryUsedMb: 512
//   },
//   request: {
//     host: 'example.com',
//     id: 'abc123',
//     ip: '192.168.1.1',
//     method: 'GET',
//     path: '/api/endpoint',
//     scheme: 'https',
//     statusCode: 200,
//     userAgent: 'Mozilla/5.0',
//     vercelCache: 'HIT'
//   }
// }, 'Processing request');
