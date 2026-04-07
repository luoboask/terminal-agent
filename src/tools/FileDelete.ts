import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { unlinkSync, existsSync, statSync } from 'fs';
import { join } from 'path';
import { info, debug, error } from '../utils/logger.js';

/**
 * FileDelete 工具 - 删除文件
 * 
 * 参考自 source/src/tools/FileDeleteTool
 * 简化版本，保留核心功能：
 * - 删除单个文件
 * - 安全检查（文件必须存在且是文件而非目录）
 */

interface FileDeleteInput {
  file_path: string;
}

export class FileDeleteTool extends BaseTool {
  readonly name = 'file_delete';
  readonly description = 'Delete a file from the local filesystem. Cannot delete directories.';
  readonly inputSchema = z.object({
    file_path: z.string().describe('The absolute path to the file to delete (must be absolute, not relative)'),
  });

  validateInput(input: unknown): FileDeleteInput | null {
    try {
      return this.inputSchema.parse(input);
    } catch (err) {
      if (err instanceof z.ZodError) {
        error('FileDelete validation failed:', err.errors.map(e => e.message).join(', '));
      }
      return null;
    }
  }

  async execute(input: FileDeleteInput): Promise<ToolResult> {
    const { file_path } = input;

    try {
      // 展开路径（处理 ~ 等）
      const fullPath = file_path.startsWith('~') 
        ? join(process.env.HOME || '', file_path.slice(1))
        : file_path;

      // 检查文件是否存在
      if (!existsSync(fullPath)) {
        return {
          success: false,
          content: `File does not exist: ${file_path}`,
          error: 'FILE_NOT_FOUND',
        };
      }

      // 检查是否是文件（不是目录）
      const stats = statSync(fullPath);
      if (!stats.isFile()) {
        return {
          success: false,
          content: `Cannot delete directory with file_delete. Path is a directory: ${file_path}`,
          error: 'IS_DIRECTORY',
        };
      }

      // 删除文件
      unlinkSync(fullPath);
      info(`File deleted: ${fullPath}`);

      return {
        success: true,
        content: `Successfully deleted file: ${file_path}`,
      };
    } catch (err) {
      error('FileDelete execution failed:', err);
      return {
        success: false,
        content: `Failed to delete file: ${err instanceof Error ? err.message : String(err)}`,
        error: 'DELETE_FAILED',
      };
    }
  }
}
