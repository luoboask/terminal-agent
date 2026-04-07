/**
 * ProjectSummary Tool - 项目总结工具
 * 
 * 批量读取项目文件并生成总结报告
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { readdirSync, readFileSync, statSync } from 'fs';
import { join, extname, resolve } from 'path';

const ProjectSummaryInputSchema = z.object({
  project_path: z.string().optional().describe('项目路径（默认当前目录）'),
  file_extensions: z.array(z.string()).optional().describe('要分析的文件扩展名（默认：[".py", ".js", ".ts", ".md"]）'),
  max_files: z.number().optional().describe('最大分析文件数（默认 50）'),
  include_content: z.boolean().optional().describe('是否包含文件内容预览（默认 false）'),
});

type Input = z.infer<typeof ProjectSummaryInputSchema>;

export class ProjectSummaryTool extends BaseTool<Input> {
  readonly name = 'project_summary';
  readonly description = '批量读取项目文件并生成总结报告，包括项目结构、文件统计、功能分析等';
  readonly inputSchema = ProjectSummaryInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { 
      project_path = '.', 
      file_extensions = ['.py', '.js', '.ts', '.md', '.txt'],
      max_files = 50,
      include_content = false 
    } = input;

    try {
      // 转换为绝对路径
      const absolutePath = resolve(project_path);
      
      // 收集项目文件
      const files = this.collectFiles(absolutePath, file_extensions, max_files);
      
      if (files.length === 0) {
        return {
          success: false,
          content: `❌ 未找到文件\n\n在 ${project_path} 目录下没有找到 ${file_extensions.join(', ')} 类型的文件`,
          error: 'No files found',
        };
      }

      // 分析项目结构
      const structure = this.analyzeStructure(files, project_path);
      
      // 统计信息
      const stats = this.calculateStats(files, project_path);
      
      // 读取文件内容（可选）
      const fileContents = include_content ? this.readFileContents(files, project_path) : [];
      
      // 生成总结报告
      const report = this.generateReport(structure, stats, fileContents, absolutePath);

      return {
        success: true,
        content: report,
      };
    } catch (err) {
      const error = err as Error;
      return {
        success: false,
        content: `❌ 项目分析失败\n\n❌ 错误：${error.message}`,
        error: error.message,
      };
    }
  }

  /**
   * 收集项目文件
   */
  private collectFiles(dir: string, extensions: string[], maxFiles: number, files: string[] = []): string[] {
    if (files.length >= maxFiles) return files;

    const entries = readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      if (entry.name.startsWith('.') || entry.name === '__pycache__' || entry.name === 'node_modules') {
        continue;
      }

      const fullPath = join(dir, entry.name);
      
      if (entry.isDirectory()) {
        this.collectFiles(fullPath, extensions, maxFiles, files);
      } else if (entry.isFile() && extensions.includes(extname(entry.name))) {
        files.push(fullPath);
        if (files.length >= maxFiles) break;
      }
    }

    return files;
  }

  /**
   * 分析项目结构
   */
  private analyzeStructure(files: string[], basePath: string): Record<string, string[]> {
    const structure: Record<string, string[]> = {};
    
    for (const file of files) {
      const relativePath = file.replace(basePath + '/', '');
      const dir = relativePath.split('/').slice(0, -1).join('/') || 'root';
      
      if (!structure[dir]) {
        structure[dir] = [];
      }
      structure[dir].push(relativePath);
    }

    return structure;
  }

  /**
   * 统计信息
   */
  private calculateStats(files: string[], basePath: string): {
    totalFiles: number;
    totalLines: number;
    totalSize: number;
    byExtension: Record<string, number>;
    largestFile: { path: string; lines: number; size: number };
  } {
    let totalLines = 0;
    let totalSize = 0;
    const byExtension: Record<string, number> = {};
    let largestFile = { path: '', lines: 0, size: 0 };

    for (const file of files) {
      try {
        const stats = statSync(file);
        const content = readFileSync(file, 'utf-8');
        const lines = content.split('\n').length;
        const ext = extname(file);

        totalLines += lines;
        totalSize += stats.size;
        byExtension[ext] = (byExtension[ext] || 0) + 1;

        if (lines > largestFile.lines) {
          largestFile = {
            path: file.replace(basePath + '/', ''),
            lines,
            size: stats.size,
          };
        }
      } catch {
        // 跳过无法读取的文件
      }
    }

    return {
      totalFiles: files.length,
      totalLines,
      totalSize,
      byExtension,
      largestFile,
    };
  }

  /**
   * 读取文件内容（预览）
   */
  private readFileContents(files: string[], basePath: string): Array<{ path: string; content: string; lines: number }> {
    const contents: Array<{ path: string; content: string; lines: number }> = [];
    
    for (const file of files.slice(0, 10)) { // 最多预览 10 个文件
      try {
        const content = readFileSync(file, 'utf-8');
        const lines = content.split('\n').slice(0, 50); // 每个文件最多 50 行
        contents.push({
          path: file.replace(basePath + '/', ''),
          content: lines.join('\n'),
          lines: content.split('\n').length,
        });
      } catch {
        // 跳过无法读取的文件
      }
    }

    return contents;
  }

  /**
   * 生成总结报告
   */
  private generateReport(
    structure: Record<string, string[]>,
    stats: {
      totalFiles: number;
      totalLines: number;
      totalSize: number;
      byExtension: Record<string, number>;
      largestFile: { path: string; lines: number; size: number };
    },
    fileContents: Array<{ path: string; content: string; lines: number }>,
    projectPath: string
  ): string {
    const lines: string[] = [];

    // 标题和项目路径
    lines.push('📊 项目总结报告');
    lines.push('=' .repeat(50));
    lines.push('');
    lines.push(`📁 **项目路径**: ${projectPath}`);
    lines.push('');

    // 统计信息
    lines.push('## 📈 统计信息');
    lines.push('');
    lines.push(`- **总文件数**: ${stats.totalFiles}`);
    lines.push(`- **总代码行数**: ${stats.totalLines.toLocaleString()}`);
    lines.push(`- **总大小**: ${(stats.totalSize / 1024).toFixed(2)} KB`);
    lines.push('');

    // 文件类型分布
    lines.push('### 文件类型分布');
    lines.push('');
    for (const [ext, count] of Object.entries(stats.byExtension)) {
      lines.push(`- **${ext || '无扩展名'}**: ${count} 个文件`);
    }
    lines.push('');

    // 最大文件
    lines.push(`### 📄 最大文件`);
    lines.push('');
    lines.push(`- **文件**: ${stats.largestFile.path}`);
    lines.push(`- **行数**: ${stats.largestFile.lines.toLocaleString()}`);
    lines.push(`- **大小**: ${(stats.largestFile.size / 1024).toFixed(2)} KB`);
    lines.push('');

    // 项目结构
    lines.push('## 📁 项目结构');
    lines.push('');
    for (const [dir, files] of Object.entries(structure)) {
      lines.push(`### ${dir === 'root' ? '根目录' : dir}`);
      lines.push('');
      for (const file of files.slice(0, 10)) { // 每个目录最多显示 10 个文件
        const fileName = file.split('/').pop() || file;
        lines.push(`- ${fileName}`);
      }
      if (files.length > 10) {
        lines.push(`- ... 还有 ${files.length - 10} 个文件`);
      }
      lines.push('');
    }

    // 文件内容预览
    if (fileContents.length > 0) {
      lines.push('## 📄 文件内容预览');
      lines.push('');
      lines.push('*(每个文件显示前 50 行)*');
      lines.push('');
      
      for (const { path, content, lines: totalLines } of fileContents) {
        lines.push(`### ${path} (${totalLines} 行)`);
        lines.push('');
        lines.push('```');
        lines.push(content);
        lines.push('```');
        lines.push('');
      }
    }

    // 总结和建议
    lines.push('## 💡 总结和建议');
    lines.push('');
    lines.push('### 项目特点');
    lines.push('- ' + (stats.totalFiles > 20 ? '中大型项目' : stats.totalFiles > 5 ? '小型项目' : '微型项目'));
    lines.push('- ' + (stats.totalLines > 5000 ? '代码量较大' : stats.totalLines > 1000 ? '代码量适中' : '代码量较小'));
    lines.push('');

    lines.push('### 建议');
    if (stats.totalLines > stats.totalFiles * 300) {
      lines.push('- ⚠️ 部分文件过大，建议拆分');
    }
    if (Object.keys(structure).length < 3 && stats.totalFiles > 10) {
      lines.push('- 📁 建议按功能模块组织目录结构');
    }
    if (stats.byExtension['.py'] && !stats.byExtension['.txt']) {
      lines.push('- 📝 建议添加 README.md 文档');
    }
    lines.push('- ✨ 保持代码整洁，定期重构');
    lines.push('');

    return lines.join('\n');
  }
}
