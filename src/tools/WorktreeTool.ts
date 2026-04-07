/**
 * WorktreeTool - Git Worktree 管理工具
 * 
 * 支持 Git worktree 的创建、删除、切换和管理
 * 参考 claude-code-learning 的 EnterWorktreeTool 设计
 */

import { z } from 'zod';
import { exec } from 'child_process';
import { promisify } from 'util';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { debug, warn } from '../utils/logger.js';
import { setProjectRoot, getProjectRoot } from '../bootstrap/state.js';

const execAsync = promisify(exec);

/**
 * Worktree 信息接口
 */
interface WorktreeInfo {
  path: string;
  branch: string;
  isCurrent: boolean;
}

/**
 * 输入 Schema
 */
const WorktreeInputSchema = z.object({
  action: z.enum(['list', 'create', 'switch', 'delete', 'prune']).describe('操作类型'),
  worktreePath: z.string().optional().describe('Worktree 路径'),
  branch: z.string().optional().describe('分支名称'),
  force: z.boolean().optional().describe('是否强制操作'),
});

type Input = z.infer<typeof WorktreeInputSchema>;

/**
 * WorktreeTool 类
 */
export class WorktreeTool extends BaseTool<Input> {
  readonly name = 'worktree';
  readonly description = '管理 Git Worktree。支持创建、删除、切换和列出 worktree。';
  readonly inputSchema = WorktreeInputSchema;

  /**
   * 检查 Git 是否可用
   */
  private async checkGit(): Promise<boolean> {
    try {
      await execAsync('git --version');
      return true;
    } catch {
      return false;
    }
  }

  /**
   * 检查是否是 Git 仓库
   */
  private async checkGitRepo(): Promise<boolean> {
    try {
      await execAsync('git rev-parse --git-dir');
      return true;
    } catch {
      return false;
    }
  }

  /**
   * 列出所有 worktree
   */
  private async listWorktrees(): Promise<WorktreeInfo[]> {
    try {
      const { stdout } = await execAsync('git worktree list --porcelain');
      const worktrees: WorktreeInfo[] = [];
      let currentWorktree: Partial<WorktreeInfo> = {};

      for (const line of stdout.split('\n')) {
        if (line.startsWith('worktree ')) {
          if (currentWorktree.path) {
            worktrees.push(currentWorktree as WorktreeInfo);
          }
          currentWorktree = { 
            path: line.replace('worktree ', ''),
            isCurrent: false
          };
        } else if (line.startsWith('branch ')) {
          currentWorktree.branch = line.replace('branch ', '');
        } else if (line === '') {
          if (currentWorktree.path) {
            worktrees.push(currentWorktree as WorktreeInfo);
            currentWorktree = {};
          }
        }
      }

      // 添加最后一个
      if (currentWorktree.path) {
        worktrees.push(currentWorktree as WorktreeInfo);
      }

      // 标记当前 worktree
      const { stdout: currentPath } = await execAsync('git rev-parse --show-toplevel');
      const currentWorktreePath = currentPath.trim();
      worktrees.forEach(w => {
        w.isCurrent = w.path === currentWorktreePath;
      });

      return worktrees;
    } catch (error) {
      warn(`Failed to list worktrees: ${error}`);
      return [];
    }
  }

  /**
   * 创建 worktree
   */
  private async createWorktree(path: string, branch?: string, force?: boolean): Promise<ToolResult> {
    try {
      const args = ['worktree', 'add'];
      
      if (force) {
        args.push('--force');
      }
      
      args.push(path);
      
      if (branch) {
        args.push('-b', branch);
      }

      const { stdout, stderr } = await execAsync(`git ${args.join(' ')}`);
      
      debug(`Created worktree at ${path}: ${stdout}`);
      
      return {
        success: true,
        content: `✅ Worktree 已创建

📁 路径：${path}
🌿 分支：${branch || '与主仓库相同'}
${stderr ? `\n⚠️ 警告：${stderr}` : ''}`,
      };
    } catch (error) {
      const err = error as Error & { stderr?: string };
      return {
        success: false,
        content: `❌ 创建 Worktree 失败

📁 路径：${path}
🌿 分支：${branch || '与主仓库相同'}

❌ 错误：${err.message}${err.stderr ? `\n\n详细信息：${err.stderr}` : ''}`,
        error: err.message,
      };
    }
  }

  /**
   * 切换 worktree
   */
  private async switchWorktree(path: string): Promise<ToolResult> {
    try {
      // 保存当前项目根目录
      const oldProjectRoot = getProjectRoot();
      
      // 切换项目根目录
      setProjectRoot(path);
      
      debug(`Switched to worktree at ${path} (was ${oldProjectRoot})`);
      
      return {
        success: true,
        content: `✅ 已切换到 Worktree

📁 路径：${path}
🏠 原路径：${oldProjectRoot}

💡 提示：项目根目录已更新，后续操作将在此 worktree 中进行。`,
        data: {
          oldProjectRoot,
          newProjectRoot: path,
        },
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ 切换 Worktree 失败

📁 路径：${path}

❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }

  /**
   * 删除 worktree
   */
  private async deleteWorktree(path: string, force?: boolean): Promise<ToolResult> {
    try {
      const args = ['worktree', 'remove'];
      
      if (force) {
        args.push('--force');
      }
      
      args.push(path);

      const { stdout, stderr } = await execAsync(`git ${args.join(' ')}`);
      
      debug(`Deleted worktree at ${path}: ${stdout}`);
      
      return {
        success: true,
        content: `✅ Worktree 已删除

📁 路径：${path}
${stderr ? `\n⚠️ 警告：${stderr}` : ''}`,
      };
    } catch (error) {
      const err = error as Error & { stderr?: string };
      return {
        success: false,
        content: `❌ 删除 Worktree 失败

📁 路径：${path}

❌ 错误：${err.message}${err.stderr ? `\n\n详细信息：${err.stderr}` : ''}`,
        error: err.message,
      };
    }
  }

  /**
   * 清理无效的 worktree
   */
  private async pruneWorktrees(): Promise<ToolResult> {
    try {
      const { stdout } = await execAsync('git worktree prune');
      
      debug(`Pruned worktrees: ${stdout}`);
      
      return {
        success: true,
        content: `✅ 已清理无效的 Worktree

${stdout || '没有需要清理的 worktree'}`,
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ 清理 Worktree 失败

❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }

  /**
   * 执行工具
   */
  async execute(input: Input): Promise<ToolResult> {
    const { action, worktreePath, branch, force } = input;

    // 检查 Git 是否可用
    if (!(await this.checkGit())) {
      return {
        success: false,
        content: '❌ Git 未安装或不在 PATH 中',
        error: 'Git not found',
      };
    }

    // 检查是否是 Git 仓库
    if (!(await this.checkGitRepo())) {
      return {
        success: false,
        content: '❌ 当前目录不是 Git 仓库',
        error: 'Not a git repository',
      };
    }

    // 执行操作
    switch (action) {
      case 'list':
        const worktrees = await this.listWorktrees();
        
        if (worktrees.length === 0) {
          return {
            success: true,
            content: '📋 没有 Worktree\n\n只有主仓库',
          };
        }
        
        const lines = worktrees.map(w => {
          const icon = w.isCurrent ? '✅' : '⚪';
          return `${icon} ${w.path} (${w.branch})`;
        });
        
        return {
          success: true,
          content: `📋 Worktree 列表\n\n${lines.join('\n')}`,
        };

      case 'create':
        if (!worktreePath) {
          return {
            success: false,
            content: '❌ 缺少 worktreePath 参数',
            error: 'Missing worktreePath',
          };
        }
        return await this.createWorktree(worktreePath, branch, force);

      case 'switch':
        if (!worktreePath) {
          return {
            success: false,
            content: '❌ 缺少 worktreePath 参数',
            error: 'Missing worktreePath',
          };
        }
        return await this.switchWorktree(worktreePath);

      case 'delete':
        if (!worktreePath) {
          return {
            success: false,
            content: '❌ 缺少 worktreePath 参数',
            error: 'Missing worktreePath',
          };
        }
        return await this.deleteWorktree(worktreePath, force);

      case 'prune':
        return await this.pruneWorktrees();

      default:
        return {
          success: false,
          content: `❌ 未知操作：${action}`,
          error: 'Unknown action',
        };
    }
  }
}
