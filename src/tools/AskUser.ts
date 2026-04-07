import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { debug, error } from '../utils/logger.js';

/**
 * AskUser 工具 - 向用户提问
 * 
 * 参考自 claude-code-learning 的 AskUserQuestionTool
 * 支持交互式问答和非交互式环境检测
 */

const AskUserInputSchema = z.object({
  question: z.string().describe('要问用户的问题'),
  allow_multiple: z.boolean().optional().describe('是否允许多个问题（默认 false）'),
});

type Input = z.infer<typeof AskUserInputSchema>;

export class AskUserTool extends BaseTool<Input> {
  readonly name = 'ask_user';
  readonly description = '向用户提问并等待回答。需要在交互式终端中运行。';
  readonly inputSchema = AskUserInputSchema;

  // 检测是否在交互式环境
  private isInteractive(): boolean {
    return process.stdin.isTTY === true;
  }

  async execute(input: Input): Promise<ToolResult> {
    const { question } = input;

    // 检查是否在非交互式环境
    if (!this.isInteractive()) {
      return {
        success: false,
        content: `❌ 非交互式环境

💡 说明：ask_user 工具需要在交互式终端中运行。
当前环境不支持用户输入。

问题：${question}

建议：
1. 在本地终端运行 source-deploy
2. 或者在上下文中直接提供答案`,
        error: 'Non-interactive environment',
      };
    }

    try {
      debug(`Asking user: "${question}"`);

      // 显示问题
      console.log('\n' + '='.repeat(60));
      console.log(`❓ ${question}`);
      console.log('='.repeat(60));

      // 读取用户输入
      const answer = await this.readUserInput();

      return {
        success: true,
        content: `✅ 用户回答

问题：${question}
回答：${answer}`,
      };
    } catch (err) {
      error('AskUser execution failed:', err);
      return {
        success: false,
        content: `❌ 提问失败

问题：${question}

错误：${err instanceof Error ? err.message : String(err)}`,
        error: 'ASK_FAILED',
      };
    }
  }

  /**
   * 读取用户输入（支持 EOFError）
   */
  private async readUserInput(): Promise<string> {
    return new Promise((resolve, reject) => {
      const readline = require('readline');
      const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
      });

      rl.question('你的回答：', (answer: string) => {
        rl.close();
        resolve(answer);
      });

      rl.on('error', (err: Error) => {
        rl.close();
        reject(err);
      });
    });
  }
}
