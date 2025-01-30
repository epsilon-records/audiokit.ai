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
      id: req?.id || 'unknown',
      host: req?.headers?.['host'] || 'unknown',
      ip: req?.headers?.['x-forwarded-for'] || req?.socket?.remoteAddress || 'unknown',
      method: req?.method || 'unknown',
      path: req?.url || 'unknown',
      scheme: req?.protocol || 'unknown',
      statusCode: req?.statusCode || 0,
      userAgent: req?.headers?.['user-agent'] || 'unknown',
      vercelCache: req?.headers?.['x-vercel-cache'] || 'unknown',
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

// Updated logging functions
const logStart = (requestId: string, message: string, context?: any) => {
  pinoLogger.info({
    request: { id: requestId },
    message: `🚀 ${message}`,
    ...context,
  });
};

const logDataRetrieval = (requestId: string, msg: string, data?: any, context?: any) => {
  pinoLogger.info({
    request: { id: requestId },
    message: `📥 ${msg}`,
    data,
    ...context,
  });
};

const logProcessing = (requestId: string, msg: string, details?: any, context?: any) => {
  pinoLogger.info({
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
  pinoLogger.info({
    request: { id: requestId },
    message: `✅ ${message}`,
    result,
    report,
    ...context,
  });
};

const logWarning = (requestId: string, msg: string, warning?: any, context?: any) => {
  pinoLogger.warn({
    request: { id: requestId },
    message: `⚠️ ${msg}`,
    warning,
    ...context,
  });
};

const logError = (requestId: string, msg: string, error: Error, context?: any) => {
  pinoLogger.error({
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
  pinoLogger.info({
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
