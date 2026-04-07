import { exec } from 'child_process';
import { promisify } from 'util';
import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { debug } from '../utils/logger.js';

const execAsync = promisify(exec);

/**
 * Glob 文件查找工具输入 Schema
 */
const GlobInputSchema = z.object({
  pattern: z.string().describe('Glob 模式（如 "*.ts", "**/*.tsx"）'),
  path: z.string().optional().describe('搜索路径（默认为当前目录）'),
  exclude: z.string().optional().describe('排除目录（如 "node_modules"）'),
  maxResults: z.number().optional().describe('最大结果数（默认 100）'),
});

/**
 * Glob 文件查找工具
 * 
 * 使用系统 find 命令进行文件匹配
 * 简化自 source/src/tools/Glob/Glob.ts
 */
export class GlobTool extends BaseTool<typeof GlobInputSchema> {
  readonly name = 'glob';
  readonly description = '查找匹配 glob 模式的文件。支持通配符 * 和 **，类似 shell glob。默认限制 100 个结果。';
  readonly inputSchema = GlobInputSchema;

  // 默认结果限制（参考 claude-code-learning: 100）
  private readonly DEFAULT_LIMIT = 100;
  
  // 最大结果字符数
  private readonly MAX_RESULT_CHARS = 100000;

  /**
   * 执行文件查找
   */
  async execute(input: z.infer<typeof GlobInputSchema>): Promise<ToolResult> {
    const {
      pattern,
      path = '.',
      exclude,
      maxResults = 100,
    } = input;

    debug(`Glob finding: ${pattern} in ${path}`);

    try {
      // 将 glob 模式转换为 find 命令
      let command = `find "${path}" -type f`;
      
      // 处理 glob 模式
      if (pattern.includes('**')) {
        // ** 表示任意深度
        const basePattern = pattern.replace('**/', '');
        command += ` -name "${basePattern}"`;
      } else if (pattern.includes('*')) {
        // 单层通配符
        command += ` -name "${pattern}"`;
      } else {
        // 精确匹配
        command += ` -name "*${pattern}*"`;
      }

      // 排除目录
      if (exclude) {
        command += ` -not -path "*/${exclude}/*"`;
      }

      // 限制结果数量
      command += ` | head -n ${maxResults}`;

      debug(`Executing: ${command}`);

      const { stdout } = await execAsync(command, {
        timeout: 30000,
      });

      let files = stdout.split('\n').filter(line => line.trim());
      const totalFiles = files.length;
      
      // 应用默认限制
      if (files.length > this.DEFAULT_LIMIT) {
        files = files.slice(0, this.DEFAULT_LIMIT);
      }
      
      let content = files.join('\n');
      
      // 截断过大的结果
      if (content.length > this.MAX_RESULT_CHARS) {
        content = content.slice(0, this.MAX_RESULT_CHARS) + `\n\n[... 结果已截断 ...]`;
      }
      
      let summary = `找到 ${totalFiles} 个文件`;
      if (totalFiles > this.DEFAULT_LIMIT) {
        summary += `（显示前 ${this.DEFAULT_LIMIT} 个）`;
      }
      
      return {
        success: true,
        content: `${summary}\n${content}`,
      };
    } catch (err) {
      const error = err as Error;
      debug(`Glob failed:`, error.message);

      return {
        success: false,
        content: '搜索失败：',
        error: `File search failed: ${error.message}`,
      };
    }
  }
}
