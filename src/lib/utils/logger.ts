import pino from 'pino';

// Create a Pino logger instance
const logger = pino({
  // Basic configuration
  level: process.env.LOG_LEVEL || 'info',

  // Timestamp configuration
  timestamp: () => `,"time":"${new Date().toISOString()}"`,

  // Message formatting
  messageKey: 'msg',

  // Custom serializers
  serializers: {
    error: pino.stdSerializers.err,
    request: (req) => ({
      method: req.method,
      url: req.url,
      headers: req.headers,
    }),
    response: (res) => ({
      statusCode: res.statusCode,
    }),
  },

  // Pretty printing in development
  transport:
    process.env.NODE_ENV === 'development'
      ? {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: 'SYS:standard',
            ignore: 'pid,hostname',
            messageFormat: '{msg}',
            singleLine: true,
          },
        }
      : undefined,
});

// Export the configured logger instance
export default logger;
