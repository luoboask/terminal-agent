/**
 * Markdown 工具函数
 * 
 * 简单 Markdown 清理（流式友好）
 * 不使用 marked 库，使用正则表达式清理
 */

import chalk from 'chalk';
import { debug } from './logger.js';

/**
 * 简单 Markdown 清理（流式友好）
 * 用于流式输出时的实时清理
 */
export function cleanMarkdownSimple(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')      // 粗体
    .replace(/\*(.*?)\*/g, '$1')          // 斜体
    .replace(/`(.*?)`/g, '$1')            // 行内代码
    .replace(/^#\s+/gm, '')               // 标题
    .replace(/^[-*]\s+/gm, '  • ')        // 列表
    .replace(/^\d+\.\s+/gm, '  $&. ');    // 有序列表
}

/**
 * 检测是否包含 Markdown 语法
 * 用于快速路径优化
 */
const MD_SYNTAX_RE = /[#*`|[>\-_~]|\n\n|^\d+\. /;

export function hasMarkdownSyntax(s: string): boolean {
  // 只检查前 500 字符
  return MD_SYNTAX_RE.test(s.length > 500 ? s.slice(0, 500) : s);
}

/**
 * 完整 Markdown 渲染（不使用 marked，使用简单渲染）
 * 用于完整内容的渲染
 */
export function renderMarkdownFull(content: string): string {
  // 如果没有 Markdown 语法，直接返回
  if (!hasMarkdownSyntax(content)) {
    return content;
  }
  
  try {
    // 使用简单渲染（不使用 marked）
    return renderMarkdownSimple(content);
  } catch (error) {
    debug(`Markdown render error: ${error}`);
    // 降级：返回原始内容
    return content;
  }
}

/**
 * 简单 Markdown 渲染（不使用 marked）
 */
export function renderMarkdownSimple(content: string): string {
  let result = content;
  
  // 处理代码块
  result = result.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const langTag = lang ? chalk.gray(`[${lang}]\n`) : '';
    return `${langTag}${chalk.gray(code)}`;
  });
  
  // 处理粗体
  result = result.replace(/\*\*(.*?)\*\*/g, chalk.bold('$1'));
  
  // 处理斜体
  result = result.replace(/\*(.*?)\*/g, chalk.italic('$1'));
  
  // 处理行内代码
  result = result.replace(/`(.*?)`/g, chalk.blue('$1'));
  
  // 处理标题
  result = result.replace(/^### (.*$)/gim, chalk.cyan.bold('$1'));
  result = result.replace(/^## (.*$)/gim, chalk.blue.bold('$1'));
  result = result.replace(/^# (.*$)/gim, chalk.magenta.bold.underline('$1'));
  
  // 处理列表
  result = result.replace(/^[-*] (.*$)/gim, chalk.white('  • $1'));
  result = result.replace(/^\d+\. (.*$)/gim, chalk.white('  $&'));
  
  // 处理引用块
  result = result.replace(/^> (.*$)/gim, chalk.dim.italic('│ $1'));
  
  // 处理水平线
  result = result.replace(/^---$/gm, chalk.dim('─'.repeat(40)));
  
  return result;
}

/**
 * 流式 Markdown 处理器
 * 
 * 用于流式输出时的 Markdown 处理
 */
export class StreamingMarkdownProcessor {
  private buffer = '';
  private inCodeBlock = false;
  private codeBlockBuffer: string[] = [];
  
  /**
   * 处理 chunk
   */
  process(chunk: string): string {
    this.buffer += chunk;
    
    // 检测代码块边界（更精确的检测）
    const codeBlockMatches = chunk.match(/```/g);
    if (codeBlockMatches) {
      // 每个 ``` 切换一次状态
      this.inCodeBlock = codeBlockMatches.length % 2 === 1 ? !this.inCodeBlock : this.inCodeBlock;
    }
    
    // 如果在代码块内，缓存内容
    if (this.inCodeBlock) {
      this.codeBlockBuffer.push(chunk);
      return chalk.gray(chunk);  // 灰色显示代码块内容
    }
    
    // 不在代码块内，简单清理 Markdown
    return cleanMarkdownSimple(chunk);
  }
  
  /**
   * 完成处理，返回完整渲染结果
   */
  finish(): string {
    if (this.buffer.includes('```')) {
      // 有代码块，使用完整渲染
      return renderMarkdownSimple(this.buffer);
    } else {
      // 无代码块，简单清理即可
      return cleanMarkdownSimple(this.buffer);
    }
  }
}
