/**
 * FileCache Tool - 管理文件缓存
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';

const FileCacheInputSchema = z.object({
  action: z.enum(['list', 'clear', 'remove']).describe('操作类型：list（查看）, clear（清空）, remove（删除指定）'),
  filePath: z.string().optional().describe('要删除缓存的文件路径（remove 操作时使用）'),
});

type Input = z.infer<typeof FileCacheInputSchema>;

export class FileCacheTool extends BaseTool<Input> {
  readonly name = 'file_cache';
  readonly description = '管理文件缓存。查看已缓存的文件列表、清空缓存或删除指定文件的缓存。';
  readonly inputSchema = FileCacheInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { action, filePath } = input;
    const fileCache = (global as any).__fileCache || {};

    try {
      if (action === 'list') {
        const files = Object.keys(fileCache);
        if (files.length === 0) {
          return {
            success: true,
            content: `📂 文件缓存

💡 当前没有缓存的文件

💡 提示：读取过的文件会自动缓存，避免重复读取`,
          };
        }
        
        return {
          success: true,
          content: `📂 文件缓存

📊 缓存文件数量：${files.length}

📁 缓存的文件：
${files.map((f, i) => `${i + 1}. ${f}`).join('\n')}

💡 提示：使用 file_cache(action="clear") 清空所有缓存`,
        };
      } else if (action === 'clear') {
        (global as any).__fileCache = {};
        return {
          success: true,
          content: `✅ 缓存已清空

📊 清空文件数量：${files.length}

💡 提示：下次读取文件时会重新读取并缓存`,
        };
      } else if (action === 'remove') {
        if (!filePath) {
          return {
            success: false,
            content: `❌ 缺少文件路径

💡 提示：请使用 filePath 参数指定要删除缓存的文件`,
            error: 'Missing filePath',
          };
        }
        
        // 删除所有包含该路径的缓存
        const keysToRemove = Object.keys(fileCache).filter(k => k.includes(filePath));
        keysToRemove.forEach(key => delete fileCache[key]);
        (global as any).__fileCache = fileCache;
        
        return {
          success: true,
          content: `✅ 已删除缓存

📁 文件：${filePath}
📊 删除缓存条目：${keysToRemove.length} 个`,
        };
      }
      
      return {
        success: false,
        content: `❌ 未知操作：${action}`,
        error: 'Unknown action',
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ 操作失败

❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }
}
