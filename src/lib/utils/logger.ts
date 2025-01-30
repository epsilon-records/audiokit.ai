import pino from 'pino';

// Rename the Pino instance to avoid conflict
const pinoLogger = pino({
  // Basic configuration
  level: process.env.LOG_LEVEL || 'info',

  // Timestamp configuration
  timestamp: () => `,"time":"${new Date().toISOString()}"`,

  // Message formatting
  messageKey: 'msg',

  formatters: {
    level: (label) => ({ level: label }),
    bindings: () => ({}), // Disable default bindings
  },

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
    data: (data) => data, // Add data serializer
    context: (context) => context, // Add context serializer
  },

  transport: {
    target: process.env.NODE_ENV === 'development' ? 'pino-pretty' : 'pino-file',
    options: {
      colorize: true,
      translateTime: 'SYS:standard',
      ignore: 'pid,hostname',
      messageFormat: '{msg} {context}',
      singleLine: true,
      destination: 1,
    },
  },
});

// Updated logging functions
const logStart = (requestId: string, msg: string, context?: any) => {
  pinoLogger.info({
    requestId,
    msg: `🚀 ${msg}`,
    ...context,
    timestamp: new Date().toISOString(),
  });
};

const logDataRetrieval = (requestId: string, msg: string, data?: any, context?: any) => {
  pinoLogger.info({
    requestId,
    msg: `📥 ${msg}`,
    data,
    ...context,
  });
};

const logProcessing = (requestId: string, msg: string, details?: any, context?: any) => {
  pinoLogger.info({
    requestId,
    msg: `🔄 ${msg}`,
    details,
    ...context,
    timestamp: new Date().toISOString(),
  });
};

const logSuccess = (requestId: string, msg: string, result?: any, context?: any) => {
  pinoLogger.info({
    requestId,
    msg: `✅ ${msg}`,
    result,
    ...context,
    timestamp: new Date().toISOString(),
  });
};

const logWarning = (requestId: string, msg: string, warning?: any, context?: any) => {
  pinoLogger.warn({
    requestId,
    msg: `⚠️ ${msg}`,
    warning,
    ...context,
    timestamp: new Date().toISOString(),
  });
};

const logError = (requestId: string, msg: string, error: Error, context?: any) => {
  pinoLogger.error({
    requestId,
    msg: `❌ ${msg}`,
    error: {
      message: error.message,
      stack: error.stack,
    },
    ...context,
  });
};

const logCompletion = (requestId: string, msg: string, stats: any, context?: any) => {
  pinoLogger.info({
    requestId,
    msg: `🎉 ${msg}`,
    stats,
    ...context,
    timestamp: new Date().toISOString(),
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
