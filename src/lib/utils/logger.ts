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

// New enricher logging functions
export const logStart = (requestId: string, msg: string, artistId?: string, context?: any) => {
  logger.info({
    requestId,
    artistId,
    msg: `🚀 ${msg}`,
    context,
    timestamp: new Date().toISOString(),
  });
};

export const logDataRetrieval = (requestId: string, msg: string, artistId: string, data?: any) => {
  logger.info({
    requestId,
    artistId,
    msg: `📥 ${msg}`,
    data,
    timestamp: new Date().toISOString(),
  });
};

export const logProcessing = (requestId: string, msg: string, artistId: string, details?: any) => {
  logger.info({
    requestId,
    artistId,
    msg: `🔄 ${msg}`,
    details,
    timestamp: new Date().toISOString(),
  });
};

export const logSuccess = (requestId: string, msg: string, artistId: string, result?: any) => {
  logger.info({
    requestId,
    artistId,
    msg: `✅ ${msg}`,
    result,
    timestamp: new Date().toISOString(),
  });
};

export const logWarning = (requestId: string, msg: string, artistId: string, warning?: any) => {
  logger.warn({
    requestId,
    artistId,
    msg: `⚠️ ${msg}`,
    warning,
    timestamp: new Date().toISOString(),
  });
};

export const logError = (requestId: string, msg: string, artistId: string, error: Error) => {
  logger.error({
    requestId,
    artistId,
    msg: `❌ ${msg}`,
    error: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString(),
  });
};

export const logCompletion = (requestId: string, msg: string, stats: any) => {
  logger.info({
    requestId,
    msg: `🎉 ${msg}`,
    stats,
    timestamp: new Date().toISOString(),
  });
};

// Export the configured logger instance
export default logger;
