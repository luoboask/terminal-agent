/**
 * FileWrite Tool - 文件写入工具
 * 
 * 简化自开源项目 的 FileWriteTool
 * 原始实现：~500 行，包含权限检查、Git 集成、团队记忆等
 * 简化版：保留核心写入功能，移除复杂依赖
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { writeFileSync, existsSync, readFileSync, mkdirSync } from 'fs';
import { dirname, resolve } from 'path';

const inputSchema = z.object({
  file_path: z.string().describe('文件的绝对路径'),
  content: z.string().describe('要写入的文件内容'),
  // 分块写入支持
  is_chunk: z.boolean().optional().describe('是否是分块写入（默认 false）'),
  chunk_index: z.number().optional().describe('当前是第几块（从 0 开始）'),
  total_chunks: z.number().optional().describe('总共多少块'),
});

type Input = z.infer<typeof inputSchema>;

export class FileWriteTool extends BaseTool<Input> {
  name = 'file_write';
  description = '创建新文件或覆盖现有文件。支持大文件分块写入。参数：file_path（文件路径，必需），content（文件内容，必需），is_chunk（是否分块，可选），chunk_index（块索引，可选），total_chunks（总块数，可选）';
  
  schema = inputSchema;

  /**
   * 分块写入文件
   */
  private async executeChunkedWrite(
    file_path: string,
    content: string,
    chunk_index: number,
    total_chunks: number
  ): Promise<ToolResult> {
    try {
      const absolutePath = resolve(file_path);
      const dir = dirname(absolutePath);
      
      // 确保目录存在
      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }

      // 第一块：覆盖写入；后续块：追加写入
      const flag = chunk_index === 0 ? 'w' : 'a';
      
      // 写入文件
      const fs = await import('fs/promises');
      await fs.appendFile(absolutePath, content, 'utf-8');

      return {
        success: true,
        content: `📝 分块写入成功

📁 文件：${absolutePath}
📦 块：${chunk_index + 1}/${total_chunks}
📏 本块大小：${content.length} 字符
${flag === 'w' ? '🔄 模式：覆盖写入（第一块）' : '➕ 模式：追加写入'}`,
      };
    } catch (err) {
      const error = err as Error;
      return {
        success: false,
        content: `❌ 分块写入失败

📁 文件：${file_path}
📦 块：${chunk_index + 1}/${total_chunks}

❌ 错误：${error.message}`,
        error: error.message,
      };
    }
  }

  async execute(input: Input): Promise<ToolResult> {
    const { file_path, content, is_chunk, chunk_index, total_chunks } = input;

    // 检查必要参数
    if (!file_path) {
      return {
        success: false,
        content: `❌ 缺少文件路径参数\n\n请提供 file_path 参数`,
        error: 'Missing file_path parameter',
      };
    }

    // 检查 content 是否为空
    if (!content || content.trim() === '') {
      return {
        success: false,
        content: `❌ 文件内容为空

📁 文件：${file_path}

❌ 错误：content 参数不能为空

💡 可能原因:
1. AI 模型没有生成文件内容
2. content 参数传递错误
3. 文件内容被意外截断

✅ 解决方法:
1. 请提供完整的文件内容
2. 对于大文件，使用分块写入 (is_chunk=true)
3. 检查 content 参数是否正确传递`,
        error: 'Empty content',
      };
    }

    // 分块写入模式
    if (is_chunk && total_chunks && total_chunks > 1) {
      return await this.executeChunkedWrite(file_path, content, chunk_index || 0, total_chunks);
    }

    const fileContent = content;

    try {
      // 处理路径：如果是绝对路径且在只读目录，改为当前目录
      let targetPath = file_path || '';
      
      // 检测只读目录（/workspace, /root 等）
      if (targetPath.startsWith('/workspace') || targetPath.startsWith('/root') || targetPath.startsWith('/tmp')) {
        // 提取文件名，保存到当前目录
        const fileName = targetPath.split('/').pop() || 'untitled.txt';
        targetPath = fileName;
      }
      
      // 权限检查：文件必须在 cwd 下（测试模式可跳过）
      if (!process.env.SKIP_PERMISSION_CHECK) {
        const cwd = process.cwd();
        const absolutePath = resolve(targetPath);
        if (!absolutePath.startsWith(cwd)) {
          return {
            success: false,
            content: `文件必须在当前工作目录下：${cwd}\n尝试写入：${absolutePath}`,
            error: 'Permission denied: outside working directory',
          };
        }
      }
      
      const absolutePath = resolve(targetPath);

      // 检查文件是否已存在
      const isUpdate = existsSync(absolutePath);
      const originalContent = isUpdate ? readFileSync(absolutePath, 'utf-8') : null;

      // 确保目录存在
      const dir = dirname(absolutePath);
      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }

      // 写入文件
      writeFileSync(absolutePath, fileContent, 'utf-8');

      // 平衡输出：简洁但有预览
      const lines = fileContent.split('\n');
      const totalLines = lines.length;
      const preview = lines.slice(0, 5).join('\n');
      
      let content = `Wrote ${totalLines} lines to ${absolutePath}`;
      
      if (totalLines <= 20) {
        // 小文件显示完整内容
        content += `\n\n${fileContent}`;
      } else {
        // 大文件显示前 5 行预览
        content += `\n\nPreview:\n${preview}\n… (+${totalLines - 5} more lines)`;
      }
      
      return {
        success: true,
        content: content,
      };
    } catch (error) {
      return {
        success: false,
        content: `文件写入失败：${error instanceof Error ? error.message : String(error)}`,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  /**
   * 生成简化 diff（按行比较）
   */
  private generateSimpleDiff(oldContent: string, newContent: string): string {
    const oldLines = oldContent.split('\n');
    const newLines = newContent.split('\n');
    
    const diff: string[] = [];
    const maxLen = Math.max(oldLines.length, newLines.length);
    
    for (let i = 0; i < maxLen; i++) {
      const oldLine = oldLines[i];
      const newLine = newLines[i];
      
      if (oldLine !== newLine) {
        if (oldLine !== undefined) {
          diff.push(`- ${oldLine}`);
        }
        if (newLine !== undefined) {
          diff.push(`+ ${newLine}`);
        }
      }
    }
    
    return diff.join('\n');
  }
}
