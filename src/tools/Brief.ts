/**
 * Brief Tool - 简报生成
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';

const BriefInputSchema = z.object({
  topic: z.string().describe('简报主题'),
  points: z.array(z.string()).optional().describe('要点列表'),
  length: z.enum(['short', 'medium', 'long']).optional().describe('简报长度'),
});

type Input = z.infer<typeof BriefInputSchema>;

export class BriefTool extends BaseTool<typeof BriefInputSchema> {
  readonly name = 'brief';
  readonly description = '生成主题简报或摘要';
  readonly inputSchema = BriefInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { topic, points = [], length = 'medium' } = input;

    const lengthLimits = {
      short: 3,
      medium: 5,
      long: 10,
    };

    const maxPoints = lengthLimits[length];
    const briefPoints = points.slice(0, maxPoints);

    let output = `📋 **${topic} 简报**\n\n`;

    if (briefPoints.length === 0) {
      output += `⚠️ 请提供要点内容以生成简报。\n\n`;
      output += `**示例**:\n`;
      output += `\`\`\`\n主题：项目进度\n要点：\n1. 完成首页开发\n2. 开始后端开发\n3. 预计下周测试\n\`\`\`\n`;
    } else {
      output += `📊 **要点概览** (${briefPoints.length}/${points.length})\n\n`;
      
      briefPoints.forEach((point, index) => {
        output += `${index + 1}. ${point}\n`;
      });

      output += `\n---\n\n`;
      output += `📝 **总结**\n\n`;
      output += `以上 ${briefPoints.length} 个要点涵盖了 ${topic} 的主要内容。\n\n`;
      
      if (points.length > maxPoints) {
        output += `⚠️ 还有 ${points.length - maxPoints} 个要点未显示（${length} 模式限制）。\n`;
      }
    }

    return {
      success: true,
      content: output,
      data: { topic, points: briefPoints, length, totalPoints: points.length },
    };
  }
}
