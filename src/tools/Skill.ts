/**
 * Skill Tool - 技能系统
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';

const SkillInputSchema = z.object({
  action: z.enum(['list', 'get', 'use', 'create']).describe('操作类型'),
  skillName: z.string().optional().describe('技能名称'),
  parameters: z.record(z.any()).optional().describe('技能参数'),
  description: z.string().optional().describe('技能描述（创建时使用）'),
});

type Input = z.infer<typeof SkillInputSchema>;

export class SkillTool extends BaseTool<typeof SkillInputSchema> {
  readonly name = 'skill';
  readonly description = '管理技能：列出、获取、使用或创建技能';
  readonly inputSchema = SkillInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { action, skillName, parameters = {}, description } = input;

    try {
      // 获取所有技能
      const globalSkills = (global as any).__skills__ || this.getDefaultSkills();

      switch (action) {
        case 'list':
          return this.listSkills(globalSkills);
        
        case 'get':
          return this.getSkill(globalSkills, skillName);
        
        case 'use':
          return this.useSkill(globalSkills, skillName, parameters);
        
        case 'create':
          return this.createSkill(globalSkills, skillName, description);
        
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
        content: `❌ 技能操作失败\n❌ 错误：${error.message}`,
        error: error.message,
      };
    }
  }

  /**
   * 获取默认技能
   */
  private getDefaultSkills(): any[] {
    return [
      {
        id: 'skill_code_review',
        name: '代码审查',
        description: '审查代码质量和安全性',
        usage: 'skill use 代码审查 { code: "代码内容" }',
      },
      {
        id: 'skill_write_test',
        name: '编写测试',
        description: '为代码生成测试用例',
        usage: 'skill use 编写测试 { file: "文件路径" }',
      },
      {
        id: 'skill_optimize',
        name: '性能优化',
        description: '优化代码性能',
        usage: 'skill use 性能优化 { code: "代码内容" }',
      },
    ];
  }

  /**
   * 列出所有技能
   */
  private listSkills(skills: any[]): ToolResult {
    if (skills.length === 0) {
      return {
        success: true,
        content: `📋 技能列表\n\n暂无技能。\n\n使用 \`skill create\` 创建新技能。`,
        data: { skills: [], count: 0 },
      };
    }

    let output = `📋 **技能列表** (${skills.length} 个)\n\n`;

    skills.forEach((skill: any, index: number) => {
      output += `${index + 1}. **${skill.name}**\n`;
      output += `   ${skill.description}\n`;
      output += `   用法：\`${skill.usage}\`\n\n`;
    });

    return {
      success: true,
      content: output,
      data: { skills, count: skills.length },
    };
  }

  /**
   * 获取技能详情
   */
  private getSkill(skills: any[], skillName?: string): ToolResult {
    if (!skillName) {
      return {
        success: false,
        content: `❌ 请提供技能名称`,
        error: 'Skill name required',
      };
    }

    const skill = skills.find((s: any) => s.name === skillName);

    if (!skill) {
      return {
        success: false,
        content: `❌ 未找到技能：${skillName}`,
        error: 'Skill not found',
      };
    }

    return {
      success: true,
      content: `📋 **技能详情**\n\n` +
               `🆔 **ID**: ${skill.id}\n` +
               `📝 **名称**: ${skill.name}\n` +
               `📄 **描述**: ${skill.description}\n` +
               `💡 **用法**: \`${skill.usage}\``,
      data: skill,
    };
  }

  /**
   * 使用技能
   */
  private useSkill(skills: any[], skillName?: string, parameters?: any): ToolResult {
    if (!skillName) {
      return {
        success: false,
        content: `❌ 请提供技能名称`,
        error: 'Skill name required',
      };
    }

    const skill = skills.find((s: any) => s.name === skillName);

    if (!skill) {
      return {
        success: false,
        content: `❌ 未找到技能：${skillName}`,
        error: 'Skill not found',
      };
    }

    return {
      success: true,
      content: `🔧 **使用技能**: ${skill.name}\n\n` +
               `📝 **描述**: ${skill.description}\n` +
               `📊 **参数**: ${JSON.stringify(parameters, null, 2)}\n\n` +
               `⚠️ **注意**: 这是简化版实现，实际技能执行需要完整实现。`,
      data: { skill, parameters },
    };
  }

  /**
   * 创建技能
   */
  private createSkill(skills: any[], skillName?: string, description?: string): ToolResult {
    if (!skillName || !description) {
      return {
        success: false,
        content: `❌ 请提供技能名称和描述`,
        error: 'Skill name and description required',
      };
    }

    const newSkill = {
      id: `skill_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      name: skillName,
      description: description,
      usage: `skill use ${skillName} { parameters }`,
      createdAt: new Date().toISOString(),
    };

    skills.push(newSkill);
    (global as any).__skills__ = skills;

    return {
      success: true,
      content: `✅ **技能已创建**\n\n` +
               `🆔 **ID**: ${newSkill.id}\n` +
               `📝 **名称**: ${newSkill.name}\n` +
               `📄 **描述**: ${newSkill.description}\n` +
               `💡 **用法**: \`${newSkill.usage}\``,
      data: newSkill,
    };
  }
}
