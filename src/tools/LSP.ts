/**
 * LSP Tool - 代码智能提示（简化版）
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { readFileSync, existsSync } from 'fs';

const LSPInputSchema = z.object({
  file: z.string().describe('文件路径'),
  line: z.number().optional().describe('行号（从 1 开始）'),
  column: z.number().optional().describe('列号（从 1 开始）'),
  action: z.enum(['hover', 'definition', 'references', 'completion']).describe('操作类型'),
});

type Input = z.infer<typeof LSPInputSchema>;

export class LSPTool extends BaseTool<typeof LSPInputSchema> {
  readonly name = 'lsp';
  readonly description = '代码智能提示（简化版）- 支持悬停提示、定义跳转、引用查找、代码补全';
  readonly inputSchema = LSPInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { file, line, column, action } = input;

    try {
      // 检查文件是否存在
      if (!existsSync(file)) {
        return {
          success: false,
          content: `❌ 文件不存在：${file}`,
          error: 'File not found',
        };
      }

      // 读取文件内容
      const content = readFileSync(file, 'utf-8');
      const lines = content.split('\n');

      // 验证行号和列号
      if (line && (line < 1 || line > lines.length)) {
        return {
          success: false,
          content: `❌ 行号超出范围：${line}（文件共 ${lines.length} 行）`,
          error: 'Line out of range',
        };
      }

      const targetLine = line ? lines[line - 1] : '';

      // 根据操作类型返回结果
      switch (action) {
        case 'hover':
          return this.provideHover(file, targetLine, line || 0);
        
        case 'definition':
          return this.provideDefinition(file, targetLine, content);
        
        case 'references':
          return this.provideReferences(file, targetLine, content);
        
        case 'completion':
          return this.provideCompletion(file, targetLine, column || 0);
        
        default:
          return {
            success: false,
            content: `❌ 未知的操作类型：${action}`,
            error: 'Unknown action',
          };
      }
    } catch (err) {
      const error = err as Error;
      return {
        success: false,
        content: `❌ LSP 操作失败

📁 文件：${file}
❌ 错误：${error.message}`,
        error: error.message,
      };
    }
  }

  /**
   * 提供悬停提示
   */
  private provideHover(file: string, line: string, lineNum: number): ToolResult {
    // 简化实现：显示当前行信息
    return {
      success: true,
      content: `💡 悬停提示

📁 文件：${file}
📍 行号：${lineNum}
📝 内容：\`${line.trim()}\`

---

**注意**: 这是简化版实现。

完整 LSP 需要：
- 集成语言服务器（tsserver、pylsp 等）
- AST 分析
- 类型推断
- 符号解析

当前建议：使用代码编辑器查看详细信息。`,
    };
  }

  /**
   * 提供定义跳转
   */
  private provideDefinition(file: string, line: string, content: string): ToolResult {
    // 简化实现：查找可能的定义
    const words = line.match(/[a-zA-Z_][a-zA-Z0-9_]*/g) || [];
    
    let output = `🔍 定义查找

📁 文件：${file}
📍 当前行：\`${line.trim()}\`

---

**找到的标识符**: ${words.join(', ') || '无'}

`;

    // 在整个文件中查找这些标识符的定义
    for (const word of words) {
      const lines = content.split('\n');
      const definitions: number[] = [];
      
      lines.forEach((l, idx) => {
        if (l.includes(`function ${word}`) || 
            l.includes(`const ${word}`) || 
            l.includes(`let ${word}`) || 
            l.includes(`class ${word}`)) {
          definitions.push(idx + 1);
        }
      });

      if (definitions.length > 0) {
        output += `\n**${word}** 定义在：第 ${definitions.join(', ')} 行\n`;
      }
    }

    output += `\n---\n\n**注意**: 这是简化版实现，基于文本匹配。\n\n完整实现需要 AST 分析和语言服务器支持。`;

    return {
      success: true,
      content: output,
    };
  }

  /**
   * 提供引用查找
   */
  private provideReferences(file: string, line: string, content: string): ToolResult {
    const words = line.match(/[a-zA-Z_][a-zA-Z0-9_]*/g) || [];
    
    let output = `🔍 引用查找

📁 文件：${file}
📍 当前行：\`${line.trim()}\`

---

`;

    for (const word of words) {
      const lines = content.split('\n');
      const references: number[] = [];
      
      lines.forEach((l, idx) => {
        if (l.includes(word)) {
          references.push(idx + 1);
        }
      });

      if (references.length > 0) {
        output += `**${word}** 引用：${references.length} 次（第 ${references.slice(0, 10).join(', ')}${references.length > 10 ? '...' : ''} 行）\n`;
      }
    }

    output += `\n---\n\n**注意**: 这是简化版实现，基于文本匹配。`;

    return {
      success: true,
      content: output,
    };
  }

  /**
   * 提供代码补全
   */
  private provideCompletion(file: string, line: string, column: number): ToolResult {
    // 简化实现：基于当前行提供建议
    const beforeCursor = line.slice(0, column);
    const currentWord = beforeCursor.match(/[a-zA-Z_][a-zA-Z0-9_]*$/) || [];
    
    let output = `💡 代码补全

📁 文件：${file}
📍 位置：第 ${column} 列
💬 前缀：\`${currentWord[0] || ''}\`

---

**建议**:

由于这是简化版实现，无法提供智能补全。

**推荐方案**:
1. 使用代码编辑器（VS Code、JetBrains 等）
2. 集成完整的 LSP 服务器
3. 使用 tsserver（TypeScript）或 pylsp（Python）

---

**当前可用工具**:
- \`grep\` - 搜索代码
- \`glob\` - 查找文件
- \`file_read\` - 读取文件内容`;

    return {
      success: true,
      content: output,
    };
  }
}
