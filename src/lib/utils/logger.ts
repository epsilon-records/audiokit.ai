import pino from 'pino';

// Configure pino logger
const logger = pino({
  level: process.env.NODE_ENV === 'development' ? 'info' : 'info',
  transport:
    process.env.NODE_ENV === 'development'
      ? {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: 'SYS:standard',
            ignore: 'pid,hostname',
          },
        }
      : undefined,
});

// Export the configured logger instance
export default logger;

// Export common logging methods for convenience
export const info = logger.info.bind(logger);
export const error = logger.error.bind(logger);
export const warn = logger.warn.bind(logger);
export const debug = logger.debug.bind(logger);
export const trace = logger.trace.bind(logger);
