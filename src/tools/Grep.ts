import { exec } from 'child_process';
import { promisify } from 'util';
import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { debug } from '../utils/logger.js';

const execAsync = promisify(exec);

/**
 * Grep 搜索工具输入 Schema
 */
const GrepInputSchema = z.object({
  pattern: z.string().describe('搜索模式（正则表达式）'),
  path: z.string().optional().describe('搜索路径（默认为当前目录）'),
  include: z.string().optional().describe('文件匹配模式（如 "*.ts"）'),
  exclude: z.string().optional().describe('排除模式（如 "node_modules"）'),
  maxResults: z.number().optional().describe('最大结果数（默认 100）'),
  contextLines: z.number().optional().describe('上下文行数（默认 0）'),
  head_limit: z.number().optional().describe('限制输出行数（默认 250，设为 0 表示无限制）'),
  offset: z.number().optional().describe('偏移量（用于分页，默认 0）'),
});

/**
 * Grep 搜索工具
 * 
 * 使用系统 grep 或 ripgrep (rg) 进行文本搜索
 * 简化自 source/src/tools/Grep/Grep.ts
 */
export class GrepTool extends BaseTool<typeof GrepInputSchema> {
  readonly name = 'grep';
  readonly description = '在文件中搜索文本模式。支持正则表达式，类似 grep 命令。默认限制 250 条结果，使用 head_limit 调整，offset 分页。';
  readonly inputSchema = GrepInputSchema;

  // 默认结果限制（参考 claude-code-learning: 250）
  private readonly DEFAULT_HEAD_LIMIT = 250;
  
  // 最大结果字符数（参考 claude-code-learning: 20K）
  private readonly MAX_RESULT_CHARS = 20000;

  /**
   * 执行搜索
   */
  async execute(input: z.infer<typeof GrepInputSchema>): Promise<ToolResult> {
    const {
      pattern,
      path = '.',
      include,
      exclude,
      maxResults = 100,
      contextLines = 0,
    } = input;

    debug(`Grep searching for: ${pattern} in ${path}`);

    try {
      // 优先使用 ripgrep (更快)
      let command = 'rg';
      let args: string[] = [
        '--color', 'never',
        '--no-heading',
        '--line-number',
        '--max-count', maxResults.toString(),
      ];

      if (contextLines > 0) {
        args.push('--context', contextLines.toString());
      }

      if (include) {
        args.push('--glob', include);
      }

      if (exclude) {
        args.push('--glob', `!${exclude}`);
      }

      args.push(pattern, path);

      // 检查 rg 是否可用
      try {
        await execAsync('which rg');
      } catch {
        // 回退到 grep
        command = 'grep';
        args = [
          '-r',
          '-n',
          '--color=never',
          '-m', maxResults.toString(),
        ];

        if (include) {
          args.push('--include', include);
        }

        args.push(pattern, path);
      }

      const fullCommand = `${command} ${args.join(' ')}`;
      debug(`Executing: ${fullCommand}`);

      const { stdout, stderr } = await execAsync(fullCommand, {
        timeout: 30000,
        maxBuffer: 5 * 1024 * 1024,
      });

      let output = stdout || '(no matches found)';
      const matchCount = output.split('\n').filter(line => line.trim()).length;
      
      // 应用 head_limit 限制
      const headLimit = input.head_limit ?? this.DEFAULT_HEAD_LIMIT;
      if (headLimit > 0) {
        const lines = output.split('\n');
        if (lines.length > headLimit) {
          output = lines.slice(0, headLimit).join('\n');
          output += `\n\n[... 还有 ${matchCount - headLimit} 条结果未显示，使用 offset=${headLimit} 继续查看 ...]`;
        }
      }
      
      // 截断过大的结果
      if (output.length > this.MAX_RESULT_CHARS) {
        output = output.slice(0, this.MAX_RESULT_CHARS) + `\n\n[... 结果已截断（超过 ${this.MAX_RESULT_CHARS} 字符）...]`;
      }

      return {
        success: true,
        content: `${output}`,
      };
    } catch (err) {
      const error = err as Error & { code?: number };
      
      // grep/rg 返回 1 表示没有找到匹配，这不是错误
      if (error.code === 1) {
        return {
          success: true,
          content: 'No matches found.',
        };
      }

      debug(`Grep failed:`, error.message);

      return {
        success: false,
        content: `❌ 搜索失败

🔍 ${pattern}

❌ 错误：${error.message}`,
        error: error.message,
      };
    }
  }
}
