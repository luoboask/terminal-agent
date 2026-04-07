import { readFileSync, existsSync, statSync } from 'fs';
import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { debug, warn } from '../utils/logger.js';
import { formatBytes } from '../utils/helpers.js';

/**
 * 文件读取工具输入 Schema
 */
const FileReadInputSchema = z.object({
  file_path: z.string().describe('要读取的文件路径（单个文件时使用）'),
  file_paths: z.array(z.string()).optional().describe('要读取的多个文件路径列表（批量读取时使用）'),
  maxLines: z.number().optional().describe('每个文件最大读取行数（默认 1000）'),
  offset: z.number().optional().describe('起始行号（从 1 开始，默认从开头读取）'),
  limit: z.number().optional().describe('读取行数限制（默认 2000 行）'),
});

/**
 * 文件读取工具
 * 
 * 简化自 source/src/tools/FileRead/FileRead.ts
 * 原始实现包含复杂的路径验证、符号链接处理、大文件优化等
 */
export class FileReadTool extends BaseTool<typeof FileReadInputSchema> {
  readonly name = 'file_read';
  readonly description = `读取文件内容。

**使用方式：**
1. 单文件：file_read(file_path="pet.py")
2. 批量读取：file_read(file_paths=["pet.py", "main.py"])
3. 大文件分块：file_read(file_path="large.py", offset=1, limit=500)

**参数说明：**
- file_path: 单个文件路径
- file_paths: 多个文件路径数组
- offset: 起始行号（从 1 开始）
- limit: 读取行数限制（默认 2000）
- maxLines: 每个文件最大行数（默认 1000）

**文件大小限制：** 256KB，超过请分块读取`;
  readonly inputSchema = FileReadInputSchema;

  // 最大文件大小限制 (256KB - 参考 claude-code-learning)
  private readonly MAX_FILE_SIZE = 256 * 1024;
  
  // 最大输出 token 数（约 25K tokens）
  private readonly MAX_OUTPUT_TOKENS = 25000;
  
  // 默认读取行数
  private readonly DEFAULT_MAX_LINES = 2000;

  /**
   * 检查路径是否安全
   */
  private isSafePath(path: string): boolean {
    const resolved = require('path').resolve(path);
    const cwd = process.cwd();
    
    // 不允许访问父目录
    return resolved.startsWith(cwd);
  }

  /**
   * 执行文件读取
   */
  async execute(input: z.infer<typeof FileReadInputSchema>): Promise<ToolResult> {
    const { file_path, file_paths, maxLines = 1000, offset = 1, limit = 2000 } = input;

    // 支持批量读取
    const filesToRead = file_paths || (file_path ? [file_path] : []);
    
    // 检查必要参数
    if (filesToRead.length === 0) {
      return {
        success: false,
        content: `❌ 缺少文件路径参数

**正确使用方式：**
1. 单文件：file_read(file_path="pet.py")
2. 批量读取：file_read(file_paths=["pet.py", "main.py"])
3. 大文件分块：file_read(file_path="large.py", offset=1, limit=500)`,

        error: 'Missing file_path parameter',
      };
    }

    // 批量读取多个文件
    if (filesToRead.length > 1) {
      const results: string[] = [];
      for (const filePath of filesToRead) {
        const result = await this.readSingleFile(filePath, maxLines, offset, limit);
        if (result.success) {
          results.push(`📄 ${filePath}:\n${result.content}`);
        } else {
          results.push(`❌ ${filePath}: ${result.error}`);
        }
      }
      return {
        success: true,
        content: results.join('\n\n---\n\n'),
      };
    }

    // 单个文件读取
    const filePath = filesToRead[0];
    debug(`FileRead reading: ${filePath}`);

    // 安全检查
    if (!this.isSafePath(filePath)) {
      return {
        success: false,
        content: `❌ 访问被拒绝

📁 文件路径：${file_path}

❌ 错误：文件必须在当前工作目录下

💡 提示：请使用相对路径，如 "pet.py" 或 "pet-system/pet.py"`,
        error: `Access denied: cannot access files outside current directory`,
      };
    }

    // 检查文件是否存在
    if (!existsSync(file_path)) {
      return {
        success: false,
        content: `❌ 文件未找到

📁 ${file_path}

❌ 错误：File not found`,
        error: `File not found: ${file_path}`,
      };
    }

    try {
      const stats = statSync(file_path);

      // 检查是否是文件
      if (!stats.isFile()) {
        return {
          success: false,
          content: '',
          error: `Not a file: ${file_path}`,
        };
      }

      // 检查文件大小
      if (stats.size > this.MAX_FILE_SIZE) {
        return {
          success: false,
          content: `❌ 文件过大

📁 ${file_path}
📏 大小：${formatBytes(stats.size)}
📊 限制：${formatBytes(this.MAX_FILE_SIZE)}

💡 请使用 offset 和 limit 参数分块读取：
- offset: 起始行号（从 1 开始）
- limit: 读取行数（默认 2000）

示例：
file_read({ file_path: "${file_path}", offset: 1, limit: 2000 })
file_read({ file_path: "${file_path}", offset: 2001, limit: 2000 })`,
          error: `File too large (${formatBytes(stats.size)}). Max size is ${formatBytes(this.MAX_FILE_SIZE)}. Use offset and limit to read in chunks.`,
        };
      }

      // 读取文件
      const content = readFileSync(file_path, 'utf-8');
      const lines = content.split('\n');

      // 应用偏移和限制
      const limit = input.limit || this.DEFAULT_MAX_LINES;
      const startIndex = Math.max(0, offset - 1);
      const endIndex = startIndex + limit;
      const selectedLines = lines.slice(startIndex, endIndex);

      const result = selectedLines.join('\n');
      const totalLines = lines.length;
      
      // 大文件显示预览，小文件显示完整内容
      if (totalLines > 50) {
        // 大文件显示预览
        const preview = lines.slice(0, 30).join('\n');
        return {
          success: true,
          content: `📖 文件预览 (${totalLines} 行)\n\n${preview}\n\n… (+${totalLines - 30} more lines)`,
        };
      } else {
        // 小文件显示完整内容
        let output = result;
        if (endIndex < totalLines) {
          output += `\n\n[... 还有 ${totalLines - endIndex} 行未显示，使用 offset=${endIndex + 1} 继续读取 ...]`;
        }
        return {
          success: true,
          content: output,
        };
      }
    } catch (err) {
      const error = err as Error;
      warn(`FileRead failed for ${file_path}:`, error.message);

      return {
        success: false,
        content: '',
        error: `Failed to read file: ${error.message}`,
      };
    }
  }

  /**
   * 读取单个文件
   */
  private async readSingleFile(filePath: string, maxLines: number, offset: number, limit: number): Promise<any> {
    // 安全检查
    if (!this.isSafePath(filePath)) {
      return {
        success: false,
        error: 'Access denied: cannot access files outside current directory',
      };
    }

    // 检查文件是否存在
    if (!existsSync(filePath)) {
      return {
        success: false,
        error: `File not found: ${filePath}`,
      };
    }

    try {
      const stats = statSync(filePath);

      // 检查文件大小
      if (stats.size > this.MAX_FILE_SIZE) {
        return {
          success: false,
          error: `文件过大 (${formatBytes(stats.size)})。最大支持 ${formatBytes(this.MAX_FILE_SIZE)}，请使用 offset 和 limit 参数分块读取`,
        };
      }

      // 读取文件
      const content = readFileSync(filePath, 'utf-8');
      const lines = content.split('\n');
      const totalLines = lines.length;

      // 应用偏移和限制
      const startIndex = Math.max(0, offset - 1);
      const endIndex = Math.min(startIndex + limit, totalLines);
      const selectedLines = lines.slice(startIndex, endIndex);

      let output = selectedLines.join('\n');

      if (endIndex < totalLines) {
        output += `\n\n[... 还有 ${totalLines - endIndex} 行未显示，使用 offset=${endIndex + 1} 继续读取 ...]`;
      }

      // 大文件显示预览，小文件显示完整内容
      if (totalLines > 50) {
        const preview = lines.slice(0, 30).join('\n');
        return {
          success: true,
          content: `📖 文件预览 (${totalLines} 行)\n\n${preview}\n\n… (+${totalLines - 30} more lines)`,
        };
      } else {
        return {
          success: true,
          content: output,
        };
      }
    } catch (err) {
      const error = err as Error;
      return {
        success: false,
        error: `Failed to read file: ${error.message}`,
      };
    }
  }
}
