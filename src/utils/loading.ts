/**
 * 加载状态指示器（大模型思考中）
 */

import chalk from 'chalk';

let loadingInterval: NodeJS.Timeout | null = null;
let spinnerIndex = 0;

/**
 * 开始加载动画（使用 终端风格 spinner）
 */
export function startLoading(message: string = '思考中'): void {
  const messages = [
    '思考中',
    '分析中',
    '处理中',
    '生成中',
  ];
  
  const randomMessage = messages[Math.floor(Math.random() * messages.length)];
  
  console.log(chalk.cyan(`\n🤖 ${randomMessage}`));
  
  spinnerIndex = 0;
  // 使用 终端风格的 spinner
  const spinnerFrames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
  
  loadingInterval = setInterval(() => {
    spinnerIndex = (spinnerIndex + 1) % spinnerFrames.length;
    // 移动到加载行开头，清除该行，然后写入新内容（使用青色）
    process.stdout.write(`\r\x1b[K${chalk.cyan(`   ${spinnerFrames[spinnerIndex]} 处理中...`)}`);
  }, 80);
}

/**
 * 停止加载动画
 */
export function stopLoading(success: boolean = true): void {
  if (loadingInterval) {
    clearInterval(loadingInterval);
    loadingInterval = null;
  }
  
  // 清除加载行（不移动光标）
  process.stdout.write('\r\x1b[K');
  // 不显示"✅ 完成"，直接换行
  console.log();
}

/**
 * 更新加载消息
 */
export function updateLoading(message: string): void {
  if (loadingInterval) {
    clearInterval(loadingInterval);
    console.log(`\r\x1b[K${chalk.cyan(`   ${message}`)}\n`);
    startLoading(message);
  }
}

/**
 * 显示工具执行状态
 */
export function showToolStatus(toolName: string, status: 'start' | 'success' | 'error'): void {
  const icons: Record<string, string> = {
    start: '🔧',
    success: '✅',
    error: '❌',
  };
  
  const colors: Record<string, typeof chalk.white> = {
    start: chalk.cyan,
    success: chalk.green,
    error: chalk.red,
  };
  
  const messages: Record<string, string> = {
    start: `正在使用 ${toolName}...`,
    success: `${toolName} 执行完成`,
    error: `${toolName} 执行失败`,
  };
  
  console.log(colors[status](`${icons[status]} ${messages[status]}\n`));
}
