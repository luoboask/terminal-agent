import chalk from 'chalk';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'none';

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
  none: 999, // 最高级别，过滤所有日志
};

// 默认不打印任何日志到用户侧
let currentLevel: LogLevel = (process.env.LOG_LEVEL as LogLevel) || 'none';

export function setLogLevel(level: LogLevel) {
  currentLevel = level;
}

export function log(level: LogLevel, message: string, ...args: unknown[]) {
  if (LOG_LEVELS[level] < LOG_LEVELS[currentLevel]) {
    return;
  }

  const timestamp = new Date().toISOString().slice(11, 19);
  const prefix = `[${timestamp}]`;

  switch (level) {
    case 'debug':
      console.log(chalk.gray(`${prefix} [DEBUG] ${message}`), ...args);
      break;
    case 'info':
      console.log(chalk.blue(`${prefix} [INFO] ${message}`), ...args);
      break;
    case 'warn':
      console.log(chalk.yellow(`${prefix} [WARN] ${message}`), ...args);
      break;
    case 'error':
      console.log(chalk.red(`${prefix} [ERROR] ${message}`), ...args);
      break;
  }
}

export const debug = (msg: string, ...args: unknown[]) => log('debug', msg, ...args);
export const info = (msg: string, ...args: unknown[]) => log('info', msg, ...args);
export const warn = (msg: string, ...args: unknown[]) => log('warn', msg, ...args);
export const error = (msg: string, ...args: unknown[]) => log('error', msg, ...args);
