#!/usr/bin/env bun

/**
 * Terminal Agent - 终端 AI 助手
 *
 * 简化自开源项目
 * 仅供学习研究使用
 *
 * 功能：
 * - 与多种 LLM Provider 对话（Qwen/Ollama/Anthropic 等）
 * - 执行 Bash 命令
 * - 读取和编辑文件
 * - Grep/Glob 搜索
 * - MCP 集成（可选）
 * - 记忆系统
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { QueryEngine } from './core/QueryEngine.js';
import { ToolRegistry } from './core/Tool.js';
import { renderMarkdownSimple, cleanMarkdownSimple, hasMarkdownSyntax, StreamingMarkdownProcessor } from './utils/markdown.js';
import { startLoading, stopLoading, showToolStatus } from './utils/loading.js';
import {
  BashTool,
  FileReadTool,
  FileEditTool,
  FileWriteTool,
  FileDeleteTool,
  DirectoryCreateTool,
  GrepTool,
  GlobTool,
  GitDiffTool,
  WorktreeTool,
  TodoWriteTool,
  WebSearchTool,
  AskUserTool,
  ProjectSummaryTool,
  ListMcpResourcesTool,
  MCPTool,
  WebFetchTool,
  TaskCreateTool,
  TaskUpdateTool,
  TaskGetTool,
  TaskListTool,
  TaskStopTool,
  TaskOutputTool,
  TaskCompleteTool,
  TaskDeleteTool,
  SendMessageTool,
  BriefTool,
  SkillTool,
  AgentTool,
  ReadMcpResourceTool,
  LSPTool,
} from './tools/index.js';
import { MemoryManager } from './memory/index.js';
import { McpClient } from './mcp/McpClient.js';
import { info, error, setLogLevel } from './utils/logger.js';

const version = '0.1.0';

/**
 * 清理临时文件（超过 24 小时）
 */
async function cleanupTempFiles() {
  try {
    const fs = await import('fs/promises');
    const path = await import('path');
    const tempDir = path.join(process.cwd(), '.source-deploy-temp');
    
    if (!existsSync(tempDir)) return;
    
    const now = Date.now();
    const TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000;
    
    const files = await fs.readdir(tempDir);
    for (const file of files) {
      const filePath = path.join(tempDir, file);
      const stats = await fs.stat(filePath);
      
      if (now - stats.mtimeMs > TWENTY_FOUR_HOURS) {
        await fs.unlink(filePath);
        console.log(`[Cleanup] 删除过期临时文件：${file}`);
      }
    }
  } catch (err) {
    // 清理失败不影响启动
  }
}

/**
 * 加载环境变量
 */
function loadEnv(): Record<string, string | undefined> {
  const envPath = join(process.cwd(), '.env');

  if (!existsSync(envPath)) {
    return {};
  }

  try {
    const content = readFileSync(envPath, 'utf-8');
    const env: Record<string, string> = {};

    for (const line of content.split('\n')) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const [key, ...valueParts] = trimmed.split('=');
        if (key && valueParts.length > 0) {
          env[key.trim()] = valueParts.join('=').trim();
        }
      }
    }

    return env;
  } catch {
    return {};
  }
}

/**
 * 初始化注册表
 */
function createToolRegistry(): ToolRegistry {
  const registry = new ToolRegistry();

  // 注册核心工具（5 个基础工具）
  registry.register(new BashTool());
  registry.register(new FileReadTool());
  registry.register(new FileEditTool());
  registry.register(new GrepTool());
  registry.register(new GlobTool());

  // 注册新增工具
  registry.register(new FileWriteTool());
  registry.register(new DirectoryCreateTool());
  registry.register(new ListMcpResourcesTool());
  registry.register(new MCPTool());
  registry.register(new WebFetchTool());
  registry.register(new TaskCreateTool());
  registry.register(new TaskUpdateTool());
  registry.register(new TaskGetTool());
  registry.register(new TaskListTool());
  registry.register(new TaskStopTool());
  registry.register(new TaskOutputTool());
  registry.register(new TaskCompleteTool());
  registry.register(new TaskDeleteTool());
  registry.register(new SendMessageTool());
  registry.register(new BriefTool());
  registry.register(new SkillTool());
  registry.register(new AgentTool());
  // AskUserTool 已在上面注册
  registry.register(new ReadMcpResourceTool());
  registry.register(new LSPTool());
  
  // 注册其他工具
  registry.register(new FileDeleteTool());
  registry.register(new GitDiffTool());
  registry.register(new WorktreeTool());
  registry.register(new TodoWriteTool());
  registry.register(new WebSearchTool());
  registry.register(new AskUserTool());
  registry.register(new ProjectSummaryTool());
  
  return registry;
}

/**
 * 获取 LLM Provider API Key
 * 优先级：Qwen > Anthropic > Ollama
 */
function getApiKey(env: Record<string, string | undefined>): {
  apiKey: string;
  provider: 'qwen' | 'anthropic' | 'ollama';
  model?: string;
  baseUrl?: string;
} {
  // 优先使用 Qwen
  if (env.DASHSCOPE_API_KEY) {
    info('使用 Qwen (通义千问) 作为 LLM Provider');
    return {
      apiKey: env.DASHSCOPE_API_KEY,
      provider: 'qwen',
      model: env.QWEN_MODEL || 'qwen3.5-plus',
      baseUrl: env.QWEN_BASE_URL,
    };
  }

  // 其次使用 Anthropic
  if (env.ANTHROPIC_API_KEY) {
    info('使用 Anthropic 作为 LLM Provider');
    return {
      apiKey: env.ANTHROPIC_API_KEY,
      provider: 'anthropic',
      model: env.ANTHROPIC_MODEL || 'claude-sonnet-4-20250514',
    };
  }

  // 最后使用 Ollama
  if (env.OLLAMA_BASE_URL) {
    info('使用 Ollama 本地模型');
    return {
      apiKey: 'ollama', // Ollama 不需要 API Key
      provider: 'ollama',
      model: env.OLLAMA_MODEL || 'llama3.1:8b',
      baseUrl: env.OLLAMA_BASE_URL,
    };
  }

  throw new Error(
    '未配置 LLM Provider。请设置以下环境变量之一：\n' +
    '  - DASHSCOPE_API_KEY (Qwen/通义千问，推荐)\n' +
    '  - ANTHROPIC_API_KEY (Anthropic Claude)\n' +
    '  - OLLAMA_BASE_URL (Ollama 本地模型)'
  );
}

/**
 * 格式化参数（简洁样式）
 */
function formatToolArgs(args: Record<string, unknown> | undefined): string {
  if (!args || Object.keys(args).length === 0) return '';
  
  // 只显示关键参数
  const parts: string[] = [];
  
  // 优先显示这些参数
  const priorityKeys = ['subject', 'title', 'file_path', 'path', 'command', 'pattern'];
  
  for (const key of priorityKeys) {
    if (args[key] !== undefined) {
      const val = String(args[key]);
      
      // command 参数特殊处理（bash 命令要完整显示）
      if (key === 'command') {
        const displayVal = val.length > 100 ? val.slice(0, 100) + '...' : val;
        parts.push(`${key}=${displayVal}`);
      } else {
        const displayVal = val.length > 30 ? val.slice(0, 30) + '...' : val;
        parts.push(`${key}=${displayVal}`);
      }
    }
  }
  
  // 特殊处理 content 参数（可能很长）
  if (args.content !== undefined) {
    const content = String(args.content);
    const lines = content.split('\n');
    if (lines.length > 1) {
      // 多行内容，显示行数
      parts.push(`content=${lines.length} lines`);
    } else if (content.length > 50) {
      // 长文本，显示长度
      parts.push(`content=${content.length} chars`);
    } else {
      // 短文本，显示内容
      parts.push(`content=${content}`);
    }
  }
  
  // 显示其他参数
  const otherKeys = Object.keys(args).filter(k => !priorityKeys.includes(k) && k !== 'content');
  for (const key of otherKeys.slice(0, 3)) { // 最多显示 3 个其他参数
    const val = String(args[key]);
    const displayVal = val.length > 20 ? val.slice(0, 20) + '...' : val;
    parts.push(`${key}=${displayVal}`);
  }
  
  return parts.join(', ');
}

/**
 * REPL 交互模式
 */
async function runRepl(engine: QueryEngine): Promise<void> {
  console.log(chalk.green('\n╔═══════════════════════════════════════════════════════╗'));
  console.log(chalk.green('║     Source Deploy - Terminal Agent Local Version         ║'));
  console.log(chalk.green('║     Type "exit" or Ctrl+C to quit                     ║'));
  console.log(chalk.green('╚═══════════════════════════════════════════════════════╝\n'));

  const readline = await import('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const prompt = () => {
    rl.question(chalk.blue('\n❯ '), async (input) => {
      const trimmed = input.trim();

      if (!trimmed) {
        prompt();
        return;
      }

      if (trimmed === 'exit' || trimmed === 'quit') {
        rl.close();
        process.exit(0);
      }

      if (trimmed === 'clear') {
        engine.clearHistory();
        console.log(chalk.gray('History cleared.\n'));
        prompt();
        return;
      }

      try {
        console.log();

        // 开始加载动画
        startLoading('思考中');

        // 流式显示 AI 回复（使用 Markdown 处理器）
        const mdProcessor = new StreamingMarkdownProcessor();
        let fullContent = '';
        let firstChunk = true;
        
        for await (const chunk of engine.submitMessage(trimmed)) {
          switch (chunk.type) {
            case 'text':
              // 收到第一个 text 时停止加载
              if (firstChunk) {
                stopLoading(true);
                firstChunk = false;
              }
              
              // 使用 Markdown 处理器处理流式输出
              const cleaned = mdProcessor.process(chunk.content);
              fullContent += chunk.content;
              
              // 打字机效果流式输出
              for (const char of cleaned) {
                process.stdout.write(char);
                await new Promise(r => setTimeout(r, 15)); // 打字速度
              }
              break;
            case 'tool_use':
              // 工具调用时，确保 loading 还在运行
              // loading 会在收到第一个 text chunk 时停止
            case 'tool_call':
            case 'tool': // 兼容更多类型名称
              // 参考 Claude 官方样式显示工具调用（带闪烁动画）
              const toolName = chunk.toolName || '工具';
              const toolDisplayName = toolName.replace(/_/g, ' ');
              const args = formatToolArgs(chunk.toolInput);
              
              // 使用 终端风格的圆圈动画
              const spinnerFrames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
              let spinnerIndex = 0;
              
              // 立即显示第一帧
              const displayArgs = toolName === 'bash' ? `command=${chunk.toolInput?.command || args}` : args;
              process.stdout.write(`${spinnerFrames[0]} ${toolDisplayName}(${displayArgs})`);
              
              const spinnerInterval = setInterval(() => {
                spinnerIndex = (spinnerIndex + 1) % spinnerFrames.length;
                process.stdout.write(`\r\x1b[K${spinnerFrames[spinnerIndex]} ${toolDisplayName}(${displayArgs})`);
              }, 80);
              
              // 存储 interval ID 以便在工具完成时清除
              (global as any).__toolSpinner__ = spinnerInterval;
              break;
            case 'tool_result':
            case 'tool_output': // 兼容更多类型名称
              // 参考 Claude 官方样式显示执行结果
              const resultToolName = chunk.toolName || '工具';
              const resultToolDisplayName = resultToolName.replace(/_/g, ' ');
              const content = chunk.content;
              
              // 清除工具调用时的闪烁动画
              if ((global as any).__toolSpinner__) {
                clearInterval((global as any).__toolSpinner__);
                delete (global as any).__toolSpinner__;
              }
              // 清除动画行并显示工具名
              process.stdout.write('\r\x1b[K');
              
              // 简洁显示工具结果（显示前 10 行）
              const resultLines = content.split('\n').slice(0, 10);
              const hasMore = content.split('\n').length > 10;
              
              console.log(chalk.green(`✅ ${resultToolDisplayName}`));
              resultLines.forEach(line => {
                const cleanLine = line.replace(/[#*_`]/g, '').trim();
                if (cleanLine && !cleanLine.startsWith('**')) {
                  console.log(chalk.gray(`   ${cleanLine}`));
                }
              });
              
              if (hasMore) {
                console.log(chalk.gray(`   ... (+${content.split('\n').length - 10} more lines)`));
              }
              console.log();
              break;
            case 'error':
              // 清除工具调用时的闪烁动画 - 清除整行
              if ((global as any).__toolSpinner__) {
                clearInterval((global as any).__toolSpinner__);
                delete (global as any).__toolSpinner__;
                process.stdout.write('\r\u001b[K');
              }
              showToolStatus(chunk.toolName || '系统', 'error');
              console.log(chalk.red(`${chunk.content}\n`));
              break;
            default:
              // 如果 chunk 有 toolName 字段，当作工具调用处理
              if ('toolName' in chunk && chunk.toolName) {
                const toolName = String(chunk.toolName);
                const toolDisplayName = toolName.replace(/_/g, ' ');
                
                // 显示工具调用动画
                const spinnerFrames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
                let spinnerIndex = 0;
                const spinnerInterval = setInterval(() => {
                  spinnerIndex = (spinnerIndex + 1) % spinnerFrames.length;
                  process.stdout.write(`\r\x1b[K${chalk.cyan(`${spinnerFrames[spinnerIndex]} ${toolDisplayName}`)}`);
                }, 80);
                
                (global as any).__toolSpinner__ = spinnerInterval;
              }
              break;
          }
        }

        // 确保加载动画和工具动画都已停止
        stopLoading(true);
        
        // 清除任何残留的工具动画
        if ((global as any).__toolSpinner__) {
          clearInterval((global as any).__toolSpinner__);
          delete (global as any).__toolSpinner__;
          process.stdout.write('\r\x1b[K');
        }

        console.log();
      } catch (err) {
        console.error(chalk.red('Error:', err instanceof Error ? err.message : String(err)));
      }

      prompt();
    });
  };

  prompt();
}

/**
 * 主函数
 */
async function main() {
  const program = new Command();

  program
    .name('source-deploy')
    .description('Terminal Agent CLI 本地部署版本 (支持 Qwen/Anthropic/Ollama)')
    .version(version)
    .option('-k, --api-key <key>', 'API Key (Qwen DASHSCOPE_API_KEY or Anthropic API Key)')
    .option('-m, --model <model>', '模型名称', '')
    .option('-p, --prompt <prompt>', '直接执行提示并退出')
    .option('--qwen', '使用 Qwen (通义千问) 模型')
    .option('--qwen-url <url>', 'Qwen Base URL', 'https://coding.dashscope.aliyuncs.com/v1')
    .option('--qwen-model <model>', 'Qwen 模型名称', 'qwen3.5-plus')
    .option('--ollama', '使用 Ollama 本地模型')
    .option('--ollama-url <url>', 'Ollama URL', 'http://localhost:11434')
    .option('--ollama-model <model>', 'Ollama 模型名称', 'llama3.1:8b')
    .option('-v, --verbose', '详细日志输出')
    .option('--no-memory', '禁用记忆系统');

  program.parse();

  // 启动时清理临时文件目录（超过 24 小时的文件）
  cleanupTempFiles();
  const options = program.opts();

  // 设置日志级别
  if (options.verbose) {
    setLogLevel('debug');
  }

  // 加载环境变量
  const env = loadEnv();

  // 使用统一的 Provider 配置
  const providerConfig = getApiKey(env);

  // 命令行选项覆盖环境变量
  let finalApiKey = providerConfig.apiKey;
  let finalModel = providerConfig.model;
  let finalBaseUrl = providerConfig.baseUrl;

  if (options.apiKey) {
    finalApiKey = options.apiKey;
  }
  if (options.model) {
    finalModel = options.model;
  }
  if (options.qwen) {
    finalApiKey = env.DASHSCOPE_API_KEY || finalApiKey;
    finalModel = options.qwenModel || 'qwen3.5-plus';
    finalBaseUrl = options.qwenUrl;
  }
  if (options.ollama) {
    finalApiKey = 'ollama';
    finalModel = options.ollamaModel;
    finalBaseUrl = options.ollamaUrl;
  }

  if (!finalApiKey && providerConfig.provider !== 'ollama') {
    console.error(chalk.red('Error: API Key not configured.'));
    console.error('Please set one of:');
    console.error('  - DASHSCOPE_API_KEY (Qwen/通义千问，推荐)');
    console.error('  - ANTHROPIC_API_KEY (Anthropic Claude)');
    console.error('  - Or use --ollama for local models');
    console.error('\nOr use --api-key flag to specify key directly.');
    process.exit(1);
  }

  // 创建工具注册表
  const registry = createToolRegistry();
  info(`Registered ${registry.list().length} tools`);

  // 初始化记忆系统
  let memoryManager: MemoryManager | null = null;
  if (options.memory !== false) {
    const memoryDir = join(process.cwd(), '.source-deploy-memory');
    if (!existsSync(memoryDir)) {
      mkdirSync(memoryDir, { recursive: true });
    }

    memoryManager = new MemoryManager({ memoryDir });
    await memoryManager.initialize();
    info('Memory system initialized');
  }

  // 构建系统提示（包含所有工具 + 强制使用工具规则）
  const systemPrompt = `You are a helpful AI coding assistant.

🚨 CRITICAL RULES:
1. MUST use tools - DO NOT just describe
2. After tool succeeds, CHECK if task complete → if YES, STOP and summarize
3. NEVER repeat same tool call >2 times  
4. AFTER reading file, PROCESS it - do NOT read again
5. If tool fails, TRY DIFFERENT APPROACH
6. **LIMIT FILE READS**: Read max 3-5 files, then STOP and summarize what you learned
7. **NO ENDLESS READING**: After reading files, MUST provide analysis/summary, not read more

📋 WORKFLOW:
1. **PLAN**: Outline 2-3 steps
2. **EXECUTE**: Call tools ONE BY ONE (max 3-5 file reads)
3. **SUMMARIZE**: After reading, summarize what you learned
4. **OPTIMIZE**: Suggest 2-3 improvements

🛠️ TOOL SELECTION GUIDE:
- Read files: file_read (single), file_read with file_paths (batch), project_summary (entire project)
- Write files: file_write (create), file_edit (modify)
- Search: grep (text search), glob (file search)
- Run commands: bash (shell commands, scripts)
- Git: git_diff (changes), worktree (branches)
- Tasks: task_create, task_list, task_update, task_complete
- Project analysis: project_summary (recommended for new projects)
- Web: web_search (search), web_fetch (fetch URL)
- MCP: list_mcp_resources, read_mcp_resource, mcp

📝 EXAMPLES:
【示例 1】文件创建
用户：创建文件 test.txt
助手：⏺ file_write(file_path=test.txt)
 ⎿ ✅ 执行成功

【示例 2】项目总结（正确示范）
用户：检查 pet-system 项目
助手：
**📋 计划：** 1.查看结构 2.读取 2-3 个核心文件 3.总结
**🔧 执行：** 
1. ⏺ glob(pattern=*.py) → 找到 5 个文件
2. ⏺ file_read(file_paths=[pet.py, main.py]) → 读取 2 个核心文件
**📊 总结：** ✅ pet-system 是宠物养成系统，包含 Pet 类、主程序、存储模块
**💡 建议：** 1.拆分大文件 2.增加单元测试 3.添加 GUI

❌ 错误示范（不要这样做）：
助手：⏺ file_read(pet.py) → ⏺ file_read(main.py) → ⏺ file_read(storage.py) → ⏺ file_read(pet.py) → ...（无限读取）
`;

  // 创建查询引擎
  const engine = new QueryEngine({
    apiKey: finalApiKey || 'dummy-key-for-ollama',
    model: finalModel,
    systemPrompt,
    toolRegistry: registry,
    cwd: process.cwd(),
  });

  // 如果有直接提示，执行后退出
  if (options.prompt) {
    console.log(chalk.blue(`Processing: ${options.prompt}\n`));

    for await (const chunk of engine.submitMessage(options.prompt)) {
      if (chunk.type === 'text') {
        process.stdout.write(chunk.content);
      }
    }

    console.log();
    process.exit(0);
  }

  // 启动 REPL
  await runRepl(engine);
}

// 运行主函数
main().catch(err => {
  console.error(chalk.red('Fatal error:'), err);
  process.exit(1);
});
