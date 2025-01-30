import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ 'metadata.level': label }),
    bindings: (bindings) => ({
      'metadata.environment': process.env.NODE_ENV,
      'metadata.executionRegion': process.env.AWS_REGION || 'local',
      'metadata.host': bindings.hostname,
    }),
  },
  timestamp: () => `,"timestamp":"${new Date().toISOString()}"`,
  messageKey: 'event_message',
  nestedKey: 'metadata',
  serializers: {
    err: (err) => ({
      ...pino.stdSerializers.err(err),
      'metadata.parsedLambdaMessage': {
        path: err.path,
        method: err.method,
        status: err.statusCode,
        request_id: err.requestId,
      },
    }),
    req: (req) => ({
      'metadata.proxy': {
        clientIp: req.ip,
        host: req.hostname,
        method: req.method,
        path: req.url,
        timestamp: Date.now(),
        userAgent: req.headers['user-agent'],
      },
    }),
    res: (res) => ({
      'metadata.statusCode': res.statusCode,
      'metadata.proxy.statusCode': res.statusCode,
    }),
  },
  base: {
    id: crypto.randomUUID(),
    'metadata.projectId': process.env.PROJECT_ID,
    'metadata.projectName': process.env.PROJECT_NAME,
    'metadata.branch': process.env.GIT_BRANCH,
  },
  transport:
    process.env.NODE_ENV === 'development'
      ? {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: true,
            messageKey: 'event_message',
            ignore: 'pid,hostname',
          },
        }
      : {
          target: 'pino/file',
          options: {
            destination: 1,
            colorize: true,
            translateTime: true,
            messageKey: 'event_message',
            ignore: 'pid,hostname',
          },
        },
});

// Example usage:
// logger.info({
//   metadata: {
//     path: '/api/endpoint',
//     requestId: 'abc123',
//     parsedLambdaMessage: {
//       duration_ms: 120,
//       memory_size_mb: 512
//     }
//   }
// }, 'Processing request');
