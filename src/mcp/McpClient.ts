import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { debug, warn, info } from '../utils/logger.js';

/**
 * MCP 服务器配置
 */
export interface McpServerConfig {
  name: string;
  command: string;
  args?: string[];
  env?: Record<string, string>;
}

/**
 * MCP 工具定义
 */
export interface McpTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

/**
 * MCP 资源定义
 */
export interface McpResource {
  uri: string;
  name: string;
  description?: string;
  mimeType?: string;
}

/**
 * MCP 客户端配置
 */
export interface McpClientConfig {
  servers: McpServerConfig[];
}

/**
 * MCP 客户端
 * 
 * 简化自 source/src/services/mcp/client.ts
 * 原始实现包含复杂的服务器管理、资源缓存、错误恢复等
 * 
 * 功能：
 * - 连接 MCP 服务器
 * - 调用远程工具
 * - 读取远程资源
 */
export class McpClient {
  private config: McpClientConfig;
  private connections: Map<string, { client: Client; transport: StdioClientTransport }> = new Map();
  private connected = false;

  constructor(config: McpClientConfig) {
    this.config = config;
  }

  /**
   * 连接到所有配置的 MCP 服务器
   */
  async connect(): Promise<void> {
    if (this.connected) {
      return;
    }

    for (const serverConfig of this.config.servers) {
      try {
        await this.connectToServer(serverConfig);
        info(`Connected to MCP server: ${serverConfig.name}`);
      } catch (err) {
        warn(`Failed to connect to MCP server ${serverConfig.name}:`, err);
      }
    }

    this.connected = true;
  }

  /**
   * 连接到单个 MCP 服务器
   */
  private async connectToServer(config: McpServerConfig): Promise<void> {
    const transport = new StdioClientTransport({
      command: config.command,
      args: config.args || [],
      env: config.env,
    });

    const client = new Client(
      { name: 'source-deploy', version: '0.1.0' },
      { capabilities: {} }
    );

    await client.connect(transport);
    
    this.connections.set(config.name, { client, transport });
    debug(`Established connection to ${config.name}`);
  }

  /**
   * 列出所有可用工具
   */
  async listTools(): Promise<McpTool[]> {
    const tools: McpTool[] = [];

    for (const [serverName, { client }] of this.connections) {
      try {
        const result = await client.listTools();
        
        for (const tool of result.tools) {
          tools.push({
            name: `${serverName}:${tool.name}`,
            description: tool.description || '',
            inputSchema: tool.inputSchema as Record<string, unknown>,
          });
        }
      } catch (err) {
        warn(`Failed to list tools from ${serverName}:`, err);
      }
    }

    return tools;
  }

  /**
   * 调用 MCP 工具
   */
  async callTool(
    serverName: string,
    toolName: string,
    args: Record<string, unknown>
  ): Promise<string> {
    const connection = this.connections.get(serverName);
    
    if (!connection) {
      throw new Error(`MCP server not found: ${serverName}`);
    }

    try {
      const result = await connection.client.callTool({
        name: toolName,
        arguments: args,
      });

      // 提取文本内容
      const content = (result.content as any[])
        .filter((block: any) => block.type === 'text')
        .map((block: any) => block.text)
        .join('\n');

      return content || JSON.stringify(result);
    } catch (err) {
      throw new Error(`Tool call failed: ${err}`);
    }
  }

  /**
   * 列出所有可用资源
   */
  async listResources(): Promise<McpResource[]> {
    const resources: McpResource[] = [];

    for (const [serverName, { client }] of this.connections) {
      try {
        const result = await client.listResources();
        
        for (const resource of result.resources) {
          resources.push({
            ...resource,
            uri: `${serverName}:${resource.uri}`,
          });
        }
      } catch (err) {
        warn(`Failed to list resources from ${serverName}:`, err);
      }
    }

    return resources;
  }

  /**
   * 读取 MCP 资源
   */
  async readResource(uri: string): Promise<string> {
    // 解析 URI 获取服务器名称
    const parts = uri.split(':');
    if (parts.length < 2) {
      throw new Error(`Invalid resource URI: ${uri}`);
    }

    const serverName = parts[0];
    const resourceUri = parts.slice(1).join(':');

    const connection = this.connections.get(serverName);
    
    if (!connection) {
      throw new Error(`MCP server not found: ${serverName}`);
    }

    try {
      const result = await connection.client.readResource({
        uri: resourceUri,
      });

      return (result.contents as any[])
        .filter((c: any) => c.type === 'text')
        .map((c: any) => c.text)
        .join('\n');
    } catch (err) {
      throw new Error(`Resource read failed: ${err}`);
    }
  }

  /**
   * 断开所有连接
   */
  async disconnect(): Promise<void> {
    for (const [serverName, { client, transport }] of this.connections) {
      try {
        await client.close();
        await transport.close();
        debug(`Disconnected from ${serverName}`);
      } catch (err) {
        warn(`Error disconnecting from ${serverName}:`, err);
      }
    }

    this.connections.clear();
    this.connected = false;
  }
}
