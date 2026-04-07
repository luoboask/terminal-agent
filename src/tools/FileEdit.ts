import { readFileSync, writeFileSync, existsSync } from 'fs';
import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { debug, warn } from '../utils/logger.js';

/**
 * 文件编辑工具输入 Schema
 */
const FileEditInputSchema = z.object({
  file_path: z.string().describe('要编辑的文件路径'),
  oldText: z.string().describe('要替换的原始文本（必须精确匹配）'),
  newText: z.string().describe('替换后的新文本'),
});

/**
 * 文件编辑工具（类似 sed/replace）
 * 
 * 简化自 source/src/tools/FileEdit/FileEdit.ts
 * 原始实现包含复杂的 diff 生成、多位置匹配处理等
 */
export class FileEditTool extends BaseTool<typeof FileEditInputSchema> {
  readonly name = 'file_edit';
  readonly description = '编辑文件内容。通过查找和替换来修改文件，oldText 必须精确匹配（包括空格和换行）。';
  readonly inputSchema = FileEditInputSchema;

  /**
   * 检查路径是否安全
   */
  private isSafePath(path: string): boolean {
    const resolved = require('path').resolve(path);
    const cwd = process.cwd();
    
    return resolved.startsWith(cwd);
  }

  /**
   * 查找相似的行（用于错误提示）
   */
  private findSimilarLines(content: string, searchText: string): string {
    const lines = content.split('\n');
    const searchTerms = searchText.toLowerCase().split(/\s+/).filter(t => t.length > 3);
    
    const similarLines: string[] = [];
    
    for (const line of lines) {
      const lineLower = line.toLowerCase();
      const matchCount = searchTerms.filter(term => lineLower.includes(term)).length;
      
      if (matchCount >= Math.min(2, searchTerms.length)) {
        similarLines.push(line.trim());
        if (similarLines.length >= 3) break;
      }
    }
    
    return similarLines.length > 0 ? similarLines.map(l => `- ${l}`).join('\n') : '';
  }

  /**
   * 执行文件编辑
   */
  async execute(input: z.infer<typeof FileEditInputSchema>): Promise<ToolResult> {
    let { file_path, oldText, newText } = input;

    debug(`FileEdit editing: ${file_path}`);

    // 安全检查
    if (!this.isSafePath(file_path)) {
      return {
        success: false,
        content: '编辑失败：',
        error: `Access denied: cannot edit files outside current directory`,
      };
    }

    // 检查文件是否存在
    if (!existsSync(file_path)) {
      return {
        success: false,
        content: '编辑失败：',
        error: `File not found: ${file_path}`,
      };
    }

    try {
      // 读取文件
      const content = readFileSync(file_path, 'utf-8');

      // 查找匹配（尝试精确匹配和模糊匹配）
      let matchIndex = content.indexOf(oldText);
      let actualOldText = oldText;  // 保存实际匹配的文本
      
      if (matchIndex === -1) {
        // 尝试模糊匹配：忽略首尾空白
        const trimmedOldText = oldText.trim();
        const lines = content.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
          if (lines[i].includes(trimmedOldText)) {
            // 找到包含目标文本的行
            matchIndex = content.indexOf(lines[i]);
            // 使用整行作为实际匹配的文本
            actualOldText = lines[i];
            break;
          }
        }
      }
      
      oldText = actualOldText;  // 更新为实际匹配的文本
      
      if (matchIndex === -1) {
        // 提供更有帮助的错误信息
        const similarLines = this.findSimilarLines(content, oldText);
        return {
          success: false,
          content: '编辑失败：',
          error: `找不到要替换的文本。请确保 oldText 精确匹配（包括空格和换行）。

建议：
1. 读取文件查看实际内容
2. 使用更具体的文本（包含更多上下文）
3. 确保空格和换行匹配

${similarLines ? `找到相似的行：\n${similarLines}` : ''}`,
        };
      }

      // 检查是否有多个匹配
      const secondMatchIndex = content.indexOf(oldText, matchIndex + 1);
      if (secondMatchIndex !== -1) {
        return {
          success: false,
          content: '编辑失败：',
          error: `找到多个匹配的文本。请使 oldText 更具体以匹配唯一位置。`,
        };
      }

      // 执行替换
      const newContent = content.replace(oldText, newText);

      // 写入文件
      writeFileSync(file_path, newContent, 'utf-8');

      // 平衡输出：显示变更和预览
      const oldLines = oldText.split('\n').length;
      const newLines = newText.split('\n').length;
      const lineNum = content.slice(0, matchIndex).split('\n').length;
      
      // 提取变更预览
      const oldPreview = oldText.split('\n').slice(0, 3).join('\n');
      const newPreview = newText.split('\n').slice(0, 3).join('\n');

      let content = `Successfully edited ${file_path}:\n`;
      content += `Line ${lineNum}: replaced ${oldLines} lines with ${newLines} lines\n\n`;
      
      if (oldLines <= 5 && newLines <= 5) {
        // 小变更显示完整内容
        content += `Before:\n${oldPreview}\n\nAfter:\n${newPreview}`;
      } else {
        // 大变更显示前 3 行预览
        content += `Before (first 3 lines):\n${oldPreview}\n\nAfter (first 3 lines):\n${newPreview}`;
      }
      
      return {
        success: true,
        content: content,
      };
    } catch (err) {
      const error = err as Error;
      warn(`FileEdit failed for ${path}:`, error.message);

      return {
        success: false,
        content: '编辑失败：',
        error: `Failed to edit file: ${error.message}`,
      };
    }
  }
}
