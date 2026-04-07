/**
 * DirectoryCreate Tool - 创建目录工具
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { mkdirSync, existsSync } from 'fs';
import { resolve } from 'path';

const DirectoryCreateInputSchema = z.object({
  path: z.string().describe('要创建的目录路径（绝对或相对路径）'),
  directory_path: z.string().optional().describe('要创建的目录路径（备选参数名）'),
  recursive: z.boolean().optional().describe('是否递归创建父目录（默认 true）'),
});

type Input = z.infer<typeof DirectoryCreateInputSchema>;

export class DirectoryCreateTool extends BaseTool<typeof DirectoryCreateInputSchema> {
  readonly name = 'directory_create';
  readonly description = '创建新目录，支持递归创建父目录';
  readonly inputSchema = DirectoryCreateInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    // 兼容多种字段名
    let dirPath = (input as any).path || (input as any).directory_path || (input as any).paths || (input as any).dir_path;
    const recursive = (input as any).recursive ?? true;
    
    if (!dirPath) {
      return {
        success: false,
        content: `❌ 缺少路径参数\n\n请提供 path 或 directory_path 参数`,
        error: 'Missing path parameter',
      };
    }

    // 处理路径：如果是绝对路径且在只读目录，改为当前目录
    if (dirPath.startsWith('/workspace') || dirPath.startsWith('/root') || dirPath.startsWith('/tmp')) {
      dirPath = dirPath.split('/').pop() || 'new_directory';
    }

    try {
      // 安全检查：解析路径
      const resolvedPath = resolve(dirPath);
      
      // 检查目录是否已存在
      if (existsSync(resolvedPath)) {
        return {
          success: true,
          content: `📁 目录已存在（无需创建）

📍 路径：${resolvedPath}

✅ 目录已就绪`,
        };
      }

      // 创建目录
      mkdirSync(resolvedPath, { recursive });

      return {
        success: true,
        content: `📁 目录已创建

📍 路径：${resolvedPath}
📂 递归：${recursive ? '是' : '否'}

✅ 创建成功`,
      };
    } catch (err) {
      const error = err as Error & { code?: string };
      
      let errorMessage = error.message;
      
      if (error.code === 'EACCES') {
        errorMessage = '权限不足，无法创建目录';
      } else if (error.code === 'EPERM') {
        errorMessage = '操作不被允许';
      }
      
      return {
        success: false,
        content: `❌ 创建目录失败

📍 路径：${dirPath}
❌ 错误：${errorMessage}`,
        error: errorMessage,
      };
    }
  }
}
