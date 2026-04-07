/**
 * Agent Tool - 子代理管理
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';

const AgentInputSchema = z.object({
  action: z.enum(['list', 'create', 'assign', 'status']).describe('操作类型'),
  agentName: z.string().optional().describe('代理名称'),
  task: z.string().optional().describe('分配的任务'),
  parameters: z.record(z.any()).optional().describe('代理参数'),
});

type Input = z.infer<typeof AgentInputSchema>;

export class AgentTool extends BaseTool<typeof AgentInputSchema> {
  readonly name = 'agent';
  readonly description = '管理子代理：列出、创建、分配任务或查看状态';
  readonly inputSchema = AgentInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { action, agentName, task, parameters = {} } = input;

    try {
      // 获取所有代理
      const globalAgents = (global as any).__agents__ || this.getDefaultAgents();

      switch (action) {
        case 'list':
          return this.listAgents(globalAgents);
        
        case 'create':
          return this.createAgent(globalAgents, agentName, parameters);
        
        case 'assign':
          return this.assignTask(globalAgents, agentName, task);
        
        case 'status':
          return this.getAgentStatus(globalAgents, agentName);
        
        default:
          return {
            success: false,
            content: `❌ 未知的操作：${action}`,
            error: 'Unknown action',
          };
      }
    } catch (err) {
      const error = err as Error;
      return {
        success: false,
        content: `❌ 代理操作失败\n❌ 错误：${error.message}`,
        error: error.message,
      };
    }
  }

  /**
   * 获取默认代理
   */
  private getDefaultAgents(): any[] {
    return [
      {
        id: 'agent_coder',
        name: 'Coder',
        role: '代码开发',
        description: '负责代码编写和修改',
        status: 'idle',
        currentTask: null,
      },
      {
        id: 'agent_reviewer',
        name: 'Reviewer',
        role: '代码审查',
        description: '负责代码审查和质量检查',
        status: 'idle',
        currentTask: null,
      },
      {
        id: 'agent_tester',
        name: 'Tester',
        role: '测试',
        description: '负责测试用例编写和执行',
        status: 'idle',
        currentTask: null,
      },
    ];
  }

  /**
   * 列出所有代理
   */
  private listAgents(agents: any[]): ToolResult {
    if (agents.length === 0) {
      return {
        success: true,
        content: `🤖 **代理列表**\n\n暂无代理。\n\n使用 \`agent create\` 创建新代理。`,
        data: { agents: [], count: 0 },
      };
    }

    let output = `🤖 **代理列表** (${agents.length} 个)\n\n`;

    agents.forEach((agent: any, index: number) => {
      const statusEmoji = agent.status === 'busy' ? '🔴' : '🟢';
      output += `${index + 1}. **${agent.name}** ${statusEmoji}\n`;
      output += `   角色：${agent.role}\n`;
      output += `   描述：${agent.description}\n`;
      if (agent.currentTask) {
        output += `   当前任务：${agent.currentTask}\n`;
      }
      output += `\n`;
    });

    return {
      success: true,
      content: output,
      data: { agents, count: agents.length },
    };
  }

  /**
   * 创建代理
   */
  private createAgent(agents: any[], agentName?: string, parameters?: any): ToolResult {
    if (!agentName) {
      return {
        success: false,
        content: `❌ 请提供代理名称`,
        error: 'Agent name required',
      };
    }

    const newAgent = {
      id: `agent_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      name: agentName,
      role: parameters.role || '通用',
      description: parameters.description || '自定义代理',
      status: 'idle' as const,
      currentTask: null,
      createdAt: new Date().toISOString(),
    };

    agents.push(newAgent);
    (global as any).__agents__ = agents;

    return {
      success: true,
      content: `✅ **代理已创建**\n\n` +
               `🆔 **ID**: ${newAgent.id}\n` +
               `📝 **名称**: ${newAgent.name}\n` +
               `🎯 **角色**: ${newAgent.role}\n` +
               `📄 **描述**: ${newAgent.description}\n` +
               `📊 **状态**: 🟢 idle`,
      data: newAgent,
    };
  }

  /**
   * 分配任务
   */
  private assignTask(agents: any[], agentName?: string, task?: string): ToolResult {
    if (!agentName || !task) {
      return {
        success: false,
        content: `❌ 请提供代理名称和任务`,
        error: 'Agent name and task required',
      };
    }

    const agentIndex = agents.findIndex((a: any) => a.name === agentName);

    if (agentIndex === -1) {
      return {
        success: false,
        content: `❌ 未找到代理：${agentName}`,
        error: 'Agent not found',
      };
    }

    const agent = agents[agentIndex];

    if (agent.status === 'busy') {
      return {
        success: false,
        content: `⚠️ 代理正在忙碌中\n\n代理：${agentName}\n当前任务：${agent.currentTask}`,
        error: 'Agent is busy',
      };
    }

    agent.status = 'busy';
    agent.currentTask = task;
    agents[agentIndex] = agent;
    (global as any).__agents__ = agents;

    return {
      success: true,
      content: `✅ **任务已分配**\n\n` +
               `🤖 **代理**: ${agentName}\n` +
               `📋 **任务**: ${task}\n` +
               `📊 **状态**: 🔴 busy`,
      data: { agent, task },
    };
  }

  /**
   * 获取代理状态
   */
  private getAgentStatus(agents: any[], agentName?: string): ToolResult {
    if (!agentName) {
      return {
        success: false,
        content: `❌ 请提供代理名称`,
        error: 'Agent name required',
      };
    }

    const agent = agents.find((a: any) => a.name === agentName);

    if (!agent) {
      return {
        success: false,
        content: `❌ 未找到代理：${agentName}`,
        error: 'Agent not found',
      };
    }

    const statusEmoji = agent.status === 'busy' ? '🔴' : '🟢';

    return {
      success: true,
      content: `📊 **代理状态**\n\n` +
               `🆔 **ID**: ${agent.id}\n` +
               `📝 **名称**: ${agent.name}\n` +
               `🎯 **角色**: ${agent.role}\n` +
               `📊 **状态**: ${statusEmoji} ${agent.status}\n` +
               `${agent.currentTask ? `📋 **当前任务**: ${agent.currentTask}` : ''}`,
      data: agent,
    };
  }
}
