import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { info, debug, error } from '../utils/logger.js';

/**
 * WebSearch 工具 - 网络搜索
 * 
 * 参考自 source/src/tools/WebSearchTool/WebSearchTool.ts
 * 简化版本，使用 Brave Search API（与 OpenClaw 一致）
 */

interface WebSearchInput {
  query: string;
  count?: number;
  freshness?: 'day' | 'week' | 'month' | 'year';
}

interface SearchResult {
  title: string;
  url: string;
  snippet: string;
}

export class WebSearchTool extends BaseTool {
  readonly name = 'web_search';
  readonly description = 'Search the web for information. Returns search results with titles, URLs, and snippets.';
  readonly inputSchema = z.object({
    query: z.string().describe('The search query'),
    count: z.number().min(1).max(10).optional().describe('Number of results (1-10, default: 5)'),
    freshness: z.enum(['day', 'week', 'month', 'year']).optional().describe('Filter by time period'),
  });

  validateInput(input: unknown): WebSearchInput | null {
    try {
      return this.inputSchema.parse(input);
    } catch (err) {
      if (err instanceof z.ZodError) {
        error('WebSearch validation failed:', err.errors.map(e => e.message).join(', '));
      }
      return null;
    }
  }

  async execute(input: WebSearchInput): Promise<ToolResult> {
    const { query, count = 5, freshness } = input;

    try {
      // 检查是否配置了 Brave Search API
      const apiKey = process.env.BRAVE_SEARCH_API_KEY;
      
      if (!apiKey) {
        // 如果没有 API key，尝试使用 web_search 技能（OpenClaw 内置）
        // 或者返回错误提示
        return {
          success: false,
          content: 'Brave Search API key not configured. Set BRAVE_SEARCH_API_KEY environment variable.',
          error: 'API_KEY_NOT_CONFIGURED',
        };
      }

      debug(`Searching web: "${query}" (count=${count}, freshness=${freshness || 'any'})`);

      // 调用 Brave Search API
      const url = new URL('https://api.search.brave.com/res/v1/web/search');
      url.searchParams.set('q', query);
      url.searchParams.set('count', String(Math.min(count, 10)));
      if (freshness) {
        url.searchParams.set('freshness', freshness);
      }

      const response = await fetch(url.toString(), {
        headers: {
          'Accept': 'application/json',
          'X-Subscription-Token': apiKey,
        },
      });

      if (!response.ok) {
        throw new Error(`Brave API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // 解析结果
      const results: SearchResult[] = [];
      
      if (data.web?.results) {
        for (const result of data.web.results.slice(0, count)) {
          results.push({
            title: result.title,
            url: result.url,
            snippet: result.description,
          });
        }
      }

      info(`Web search completed: ${results.length} results`);

      return {
        success: true,
        content: JSON.stringify({
          query,
          results,
          total: results.length,
        }, null, 2),
      };
    } catch (err) {
      error('WebSearch execution failed:', err);
      return {
        success: false,
        content: `Web search failed: ${err instanceof Error ? err.message : String(err)}`,
        error: 'SEARCH_FAILED',
      };
    }
  }
}
