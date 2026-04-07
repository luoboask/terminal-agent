/**
 * ListMcpResources Tool - 列出 MCP 服务器资源
 * 
 * 简化自开源项目 的 ListMcpResourcesTool
 * 显示已配置的 MCP 服务器和可用资源
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';

const inputSchema = z.object({});

type Input = z.infer<typeof inputSchema>;

export class ListMcpResourcesTool extends BaseTool<Input> {
  name = 'list_mcp_resources';
  description = '列出所有已配置的 MCP 服务器及其可用资源';
  
  schema = inputSchema;

  async execute(input: Input): Promise<ToolResult> {
    try {
      // 从环境变量读取 MCP 配置
      const mcpConfigStr = process.env.MCP_SERVERS_CONFIG || '{}';
      const mcpConfig = JSON.parse(mcpConfigStr);
      
      const servers = mcpConfig.servers || {};
      const serverNames = Object.keys(servers);
      
      if (serverNames.length === 0) {
        return {
          success: true,
          content: '未配置任何 MCP 服务器。\n\n在 .env 中设置 MCP_SERVERS_CONFIG 来添加服务器，例如：\nMCP_SERVERS_CONFIG={"servers":{"github":{"url":"https://api.githubcopilot.com/mcp/"}}}',
          data: { servers: [] },
        };
      }
      
      const resources: Array<{name: string; url?: string; transport?: string}> = [];
      
      for (const [name, config] of Object.entries(servers as Record<string, any>)) {
        resources.push({
          name,
          url: (config as any).url,
          transport: (config as any).transport || 'http',
        });
      }
      
      const output = [
        `已配置 ${serverNames.length} 个 MCP 服务器:`,
        '',
        ...resources.map(r => `- **${r.name}** (${r.transport})\n  URL: ${r.url || 'N/A'}`),
        '',
        '使用 `mcp` 工具调用这些服务器的功能。',
      ].join('\n');
      
      return {
        success: true,
        content: output,
        data: { servers: resources },
      };
    } catch (error) {
      return {
        success: false,
        content: `获取 MCP 资源失败：${error instanceof Error ? error.message : String(error)}\n\n请检查 MCP_SERVERS_CONFIG 是否为有效的 JSON。`,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }
}
