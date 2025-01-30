import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
    bindings: (bindings) => ({}), // Disable default bindings
  },
  timestamp: () => `,"time":"${new Date().toISOString()}"`,
  messageKey: 'msg',
  nestedKey: 'data', // Optional: if you want to nest some data
  serializers: {
    err: pino.stdSerializers.err, // Proper error serialization
  },
  transport:
    process.env.NODE_ENV === 'development'
      ? {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: true,
          },
        }
      : undefined,
});
