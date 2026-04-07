/**
 * WebFetch Tool - 获取网页内容
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';

const WebFetchInputSchema = z.object({
  url: z.string().url().describe('要获取的网页 URL'),
  maxLines: z.number().optional().describe('最大返回行数（默认 100）'),
});

type Input = z.infer<typeof WebFetchInputSchema>;

export class WebFetchTool extends BaseTool<typeof WebFetchInputSchema> {
  readonly name = 'web_fetch';
  readonly description = '获取网页内容并提取可读文本';
  readonly inputSchema = WebFetchInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { url, maxLines = 100 } = input;

    try {
      // 使用 OpenClaw 的 web_fetch 工具（如果可用）
      // 或者使用简单的 fetch + 文本提取
      
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; SourceDeploy/1.0)',
        },
      });

      if (!response.ok) {
        return {
          success: false,
          content: `❌ 获取失败\n\nURL: ${url}\n状态码：${response.status} ${response.statusText}`,
          error: `HTTP ${response.status}`,
        };
      }

      const html = await response.text();
      
      // 简单提取文本（移除 HTML 标签）
      const text = html
        .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
        .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
        .replace(/<[^>]+>/g, '')
        .replace(/\s+/g, ' ')
        .trim();

      const lines = text.split('\n').slice(0, maxLines);
      const truncated = text.split('\n').length > maxLines;

      return {
        success: true,
        content: `🌐 网页内容

📍 URL: ${url}
📏 长度：${lines.length} 行${truncated ? '（已截断）' : ''}

---

${lines.join('\n')}

${truncated ? '\n... (内容已截断)' : ''}`,
      };
    } catch (err) {
      const error = err as Error;
      return {
        success: false,
        content: `❌ 获取网页失败

📍 URL: ${url}
❌ 错误：${error.message}`,
        error: error.message,
      };
    }
  }
}
