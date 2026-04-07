import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { join } from 'path';
import { info, debug, error } from '../utils/logger.js';

/**
 * GitDiff 工具 - 获取 Git 差异
 * 
 * 参考自 source/src/utils/gitDiff.ts
 * 简化版本，保留核心功能：
 * - 获取单个文件的 diff
 * - 获取暂存区/工作区 diff
 * - 支持指定 commit 范围
 */

interface GitDiffInput {
  file_path?: string;
  staged?: boolean;
  commit_range?: string;
}

interface GitHunk {
  oldStart: number;
  oldLines: number;
  newStart: number;
  newLines: number;
  lines: string[];
}

export class GitDiffTool extends BaseTool {
  readonly name = 'git_diff';
  readonly description = 'Get git diff for files. Can show unstaged changes, staged changes, or diff between commits.';
  readonly inputSchema = z.object({
    file_path: z.string().optional().describe('Specific file path to diff (optional)'),
    staged: z.boolean().optional().describe('Show staged changes instead of unstaged'),
    commit_range: z.string().optional().describe('Commit range like "HEAD~1" or "abc123..def456"'),
  });

  validateInput(input: unknown): GitDiffInput | null {
    try {
      return this.inputSchema.parse(input);
    } catch (err) {
      if (err instanceof z.ZodError) {
        error('GitDiff validation failed:', err.errors.map(e => e.message).join(', '));
      }
      return null;
    }
  }

  async execute(input: GitDiffInput): Promise<ToolResult> {
    const { file_path, staged, commit_range } = input;

    try {
      // 展开路径
      const fullPath = file_path 
        ? (file_path.startsWith('~') 
            ? join(process.env.HOME || '', file_path.slice(1))
            : file_path)
        : undefined;

      // 检查是否在 git 仓库中
      try {
        execSync('git rev-parse --git-dir', { stdio: 'pipe' });
      } catch {
        return {
          success: false,
          content: 'Not in a git repository',
          error: 'NOT_GIT_REPO',
        };
      }

      // 构建 git diff 命令
      let args = ['diff', '--no-color'];
      
      if (staged) {
        args.push('--cached');
      }

      if (commit_range) {
        args.push(commit_range);
      }

      if (fullPath) {
        args.push('--', fullPath);
      }

      debug(`Running git ${args.join(' ')}`);

      // 执行 git diff
      const output = execSync(`git ${args.join(' ')}`, {
        encoding: 'utf-8',
        maxBuffer: 10 * 1024 * 1024, // 10MB buffer
      });

      // 解析 diff 输出为 hunks
      const hunks = this.parseDiff(output);

      info(`Git diff completed: ${hunks.length} hunks`);

      return {
        success: true,
        content: JSON.stringify({
          diff: output,
          hunks,
          filePath: fullPath,
          staged: staged || false,
        }, null, 2),
      };
    } catch (err) {
      // git diff 返回 1 表示有差异但不是错误
      if (err instanceof Error && 'status' in err && (err as any).status === 1) {
        // 有差异但没有文件匹配
        if ((err as any).stdout === '') {
          return {
            success: true,
            content: JSON.stringify({
              diff: '',
              hunks: [],
              message: 'No changes found',
            }, null, 2),
          };
        }
      }

      error('GitDiff execution failed:', err);
      return {
        success: false,
        content: `Git diff failed: ${err instanceof Error ? err.message : String(err)}`,
        error: 'DIFF_FAILED',
      };
    }
  }

  /**
   * 解析 unified diff 格式
   */
  private parseDiff(diffOutput: string): GitHunk[] {
    const hunks: GitHunk[] = [];
    const lines = diffOutput.split('\n');
    
    let currentHunk: GitHunk | null = null;

    for (const line of lines) {
      // 匹配 hunk header: @@ -oldStart,oldLines +newStart,newLines @@
      const hunkMatch = line.match(/^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@/);
      
      if (hunkMatch) {
        if (currentHunk) {
          hunks.push(currentHunk);
        }
        
        currentHunk = {
          oldStart: parseInt(hunkMatch[1], 10),
          oldLines: parseInt(hunkMatch[2] || '1', 10),
          newStart: parseInt(hunkMatch[3], 10),
          newLines: parseInt(hunkMatch[4] || '1', 10),
          lines: [],
        };
      } else if (currentHunk && (line.startsWith('+') || line.startsWith('-') || line.startsWith(' '))) {
        currentHunk.lines.push(line);
      }
    }

    if (currentHunk) {
      hunks.push(currentHunk);
    }

    return hunks;
  }
}
