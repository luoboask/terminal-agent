/**
 * ReadMcpResource Tool - 读取 MCP 资源
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';

const ReadMcpResourceInputSchema = z.object({
  server: z.string().describe('MCP 服务器名称'),
  uri: z.string().describe('资源 URI'),
});

type Input = z.infer<typeof ReadMcpResourceInputSchema>;

export class ReadMcpResourceTool extends BaseTool<typeof ReadMcpResourceInputSchema> {
  readonly name = 'read_mcp_resource';
  readonly description = '读取 MCP 服务器的资源内容';
  readonly inputSchema = ReadMcpResourceInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { server, uri } = input;

    try {
      // 获取 MCP 配置
      const mcpConfigStr = process.env.MCP_SERVERS_CONFIG || '{}';
      const mcpConfig = JSON.parse(mcpConfigStr);
      const serverConfig = mcpConfig.servers?.[server];

      if (!serverConfig) {
        return {
          success: false,
          content: `❌ 未找到 MCP 服务器：${server}\n\n可用服务器：${Object.keys(mcpConfig.servers || {}).join(', ')}`,
          error: `Server not found: ${server}`,
        };
      }

      // 简化实现：模拟读取资源
      // 完整实现需要调用 MCP SDK
      const resource = {
        uri,
        server,
        name: uri.split('/').pop() || 'unknown',
        mimeType: 'text/plain',
        content: `[模拟资源内容]\n\n服务器：${server}\nURI: ${uri}\n\n注意：完整实现需要集成 @modelcontextprotocol/sdk`,
      };

      return {
        success: true,
        content: `📄 MCP 资源内容

🖥️ **服务器**: ${server}
🔗 **URI**: ${uri}
📝 **名称**: ${resource.name}
📄 **类型**: ${resource.mimeType}

---

${resource.content}`,
        data: resource,
      };
    } catch (err) {
      const error = err as Error;
      return {
        success: false,
        content: `❌ 读取 MCP 资源失败

🖥️ 服务器：${server}
🔗 URI: ${uri}
❌ 错误：${error.message}`,
        error: error.message,
      };
    }
  }
}
