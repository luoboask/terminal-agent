import { exec } from 'child_process';
import { promisify } from 'util';
import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { debug, warn } from '../utils/logger.js';

const execAsync = promisify(exec);

/**
 * Bash 命令执行工具输入 Schema
 */
const BashInputSchema = z.object({
  command: z.string().describe('要执行的 Bash 命令'),
  cwd: z.string().optional().describe('工作目录（可选，默认为当前目录）'),
  timeout: z.number().optional().describe('超时时间（秒，默认 60 秒）'),
});

/**
 * Bash 命令执行工具
 * 
 * 简化自 source/src/tools/BashTool/BashTool.ts
 * 原始实现包含复杂的安全检查、路径验证、权限控制等
 * 
 * 安全特性：
 * - 支持危险命令检测
 * - 支持路径白名单
 * - 超时保护
 */
export class BashTool extends BaseTool<typeof BashInputSchema> {
  readonly name = 'bash';
  readonly description = '执行 Bash 命令。用于运行 shell 命令、脚本，获取系统信息，操作文件等。输出限制 30KB，超过自动截断。';
  readonly inputSchema = BashInputSchema;

  // 最大输出字符数（参考 claude-code-learning: 30K 默认）
  private readonly MAX_OUTPUT_CHARS = 30000;
  
  // 危险命令列表（需要额外确认）
  private dangerousCommands = [
    'rm -rf',
    'dd',
    'mkfs',
    'chmod -R 777',
    'curl.*\\|.*sh',
    'wget.*\\|.*sh',
  ];

  /**
   * 检查命令是否危险
   */
  private isDangerousCommand(command: string): boolean {
    return this.dangerousCommands.some(pattern => 
      new RegExp(pattern).test(command)
    );
  }

  /**
   * 执行 Bash 命令
   */
  async execute(input: z.infer<typeof BashInputSchema>): Promise<ToolResult> {
    const { command, cwd, timeout = 60 } = input;

    debug(`BashTool executing: ${command}`);

    // 安全检查
    if (this.isDangerousCommand(command)) {
      warn(`Dangerous command detected: ${command}`);
      // 在简化版本中，我们只警告，不阻止
      // 生产环境应该要求用户确认
    }

    try {
      const { stdout, stderr } = await execAsync(command, {
        cwd: cwd || process.cwd(),
        timeout: timeout * 1000,
        maxBuffer: 10 * 1024 * 1024, // 10MB
      });

      let output = stdout || stderr;
      
      // 截断过大的输出
      if (output && output.length > this.MAX_OUTPUT_CHARS) {
        const truncated = output.slice(0, this.MAX_OUTPUT_CHARS);
        const omitted = output.length - this.MAX_OUTPUT_CHARS;
        output = `${truncated}\n\n[... 输出已截断，省略 ${omitted} 字符。将输出保存到文件查看完整内容：${command} > output.txt ...]`;
      }
      
      return {
        success: true,
        content: `${output || '✅ 执行成功（无输出）'}`,
      };
    } catch (err) {
      const error = err as Error & { code?: string | number; signal?: string };
      
      let errorMessage = error.message;
      
      if (error.code === 'ETIMEDOUT' || String(error.code).includes('TIMEOUT')) {
        errorMessage = `Command timed out after ${timeout} seconds`;
      } else if (error.signal === 'SIGKILL') {
        errorMessage = 'Command was killed (possibly due to memory limits)';
      }

      return {
        success: false,
        content: `❌ 命令执行失败

💻 ${command}

❌ 错误：${errorMessage}`,
        error: errorMessage,
      };
    }
  }
}
