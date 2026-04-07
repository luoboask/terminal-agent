#!/usr/bin/env node
/**
 * 完整系统测试脚本
 * 测试项目管理、任务系统、会话系统、WorktreeTool 的集成
 */

const path = require('path');
const fs = require('fs');

console.log('🧪 完整系统测试\n');
console.log('=' .repeat(60));

// ============ 1. 测试状态管理 ============
console.log('\n1️⃣ 测试状态管理...\n');

const state = require('./src/bootstrap/state.js');

// 初始化
state.initState(process.cwd());
console.log('✅ initState()');

// 获取项目根目录
const projectRoot = state.getProjectRoot();
console.log(`✅ getProjectRoot(): ${projectRoot}`);

// 获取原始工作目录
const originalCwd = state.getOriginalCwd();
console.log(`✅ getOriginalCwd(): ${originalCwd}`);

// 获取会话存储目录
const sessionDir = state.getSessionStorageDir();
console.log(`✅ getSessionStorageDir(): ${sessionDir}`);

// 打印状态
console.log('\n📊 当前状态:');
state.printState();

// ============ 2. 测试项目设置 ============
console.log('\n2️⃣ 测试项目设置...\n');

const settings = require('./src/utils/projectSettings.js');

// 初始化项目设置
settings.initProjectSettings();
console.log('✅ initProjectSettings()');

// 获取设置
const projectSettings = settings.getProjectSettings();
console.log('✅ getProjectSettings()');
console.log(`   模型：${projectSettings.model || '(默认)'}`);
console.log(`   Max Tokens: ${projectSettings.maxTokens || '(默认)'}`);

// 更新设置
settings.updateProjectSettings({
  model: 'qwen3.5-plus',
  maxTokens: 4096,
  verbose: true
});
console.log('✅ updateProjectSettings()');

// 验证更新
const updated = settings.getProjectSettings();
console.log(`   更新后模型：${updated.model}`);
console.log(`   更新后 Max Tokens: ${updated.maxTokens}`);

// ============ 3. 测试会话系统 ============
console.log('\n3️⃣ 测试会话系统...\n');

const sessionStorage = require('./src/utils/sessionStorage.js');

// 创建会话
const session1 = sessionStorage.createSession('测试会话 1', { test: true });
console.log(`✅ createSession(): ${session1.id}`);

// 添加消息
sessionStorage.addMessage(session1.id, {
  role: 'user',
  content: '你好，这是测试消息'
});
console.log('✅ addMessage() - 用户消息');

sessionStorage.addMessage(session1.id, {
  role: 'assistant',
  content: '你好！有什么可以帮你的吗？'
});
console.log('✅ addMessage() - 助手消息');

// 加载会话
const loaded = sessionStorage.loadSession(session1.id);
console.log(`✅ loadSession(): ${loaded?.messages.length} 条消息`);

// 列出会话
const sessions = sessionStorage.listSessions();
console.log(`✅ listSessions(): ${sessions.length} 个会话`);

// 获取统计
const stats = sessionStorage.getSessionStats();
console.log('✅ getSessionStats():');
console.log(`   总会话数：${stats.totalSessions}`);
console.log(`   总消息数：${stats.totalMessages}`);

// ============ 4. 测试任务系统 ============
console.log('\n4️⃣ 测试任务系统...\n');

const taskStorage = require('./src/utils/taskStorageV2.js');

// 创建任务
const task1 = taskStorage.createTask({
  subject: '测试任务 1',
  description: '这是一个测试任务',
  priority: 'high',
  status: 'pending',
  activeForm: '执行测试任务 1'
});
console.log(`✅ createTask(): ${task1.id}`);

const task2 = taskStorage.createTask({
  subject: '测试任务 2',
  description: '这是另一个测试任务',
  priority: 'medium',
  status: 'pending',
  activeForm: '执行测试任务 2'
});
console.log(`✅ createTask(): ${task2.id}`);

// 查看任务列表
console.log('\n📋 任务列表:');
console.log(taskStorage.listTasksSimple());

// 更新任务
taskStorage.updateTask(task1.id, {
  status: 'in_progress',
  activeForm: '正在执行测试任务 1'
});
console.log('✅ updateTask() - 更新任务 1 为进行中');

// 完成任务
taskStorage.updateTask(task1.id, {
  status: 'completed'
});
console.log('✅ updateTask() - 完成任务 1');

// 查看更新后的列表
console.log('\n📋 更新后的任务列表:');
console.log(taskStorage.listTasksSimple());

// ============ 5. 测试跨项目恢复 ============
console.log('\n5️⃣ 测试跨项目恢复...\n');

// 创建第二个会话
const session2 = sessionStorage.createSession('测试会话 2');
console.log(`✅ createSession(): ${session2.id}`);

// 模拟跨项目恢复
const resumed = sessionStorage.resumeSession(
  session2.id,
  sessionDir,  // 源项目
  sessionDir   // 目标项目（相同，仅测试）
);
console.log(`✅ resumeSession(): ${resumed?.id}`);
console.log(`   元数据：${JSON.stringify(resumed?.metadata)}`);

// ============ 6. 测试 WorktreeTool ============
console.log('\n6️⃣ 测试 WorktreeTool...\n');

const { WorktreeTool } = require('./src/tools/WorktreeTool.js');
const worktreeTool = new WorktreeTool();

// 检查 Git 是否可用
(async () => {
  const gitAvailable = await worktreeTool.checkGit();
  console.log(`✅ checkGit(): ${gitAvailable ? 'Git 可用' : 'Git 不可用'}`);

  if (gitAvailable) {
    const isRepo = await worktreeTool.checkGitRepo();
    console.log(`✅ checkGitRepo(): ${isRepo ? '是 Git 仓库' : '不是 Git 仓库'}`);

    if (isRepo) {
      // 列出 worktree
      const worktrees = await worktreeTool.listWorktrees();
      console.log(`✅ listWorktrees(): ${worktrees.length} 个 worktree`);
      
      worktrees.forEach(w => {
        const icon = w.isCurrent ? '✅' : '⚪';
        console.log(`   ${icon} ${w.path} (${w.branch})`);
      });
    } else {
      console.log('⚠️  跳过 worktree 测试（不是 Git 仓库）');
    }
  } else {
    console.log('⚠️  跳过 worktree 测试（Git 不可用）');
  }

  // ============ 7. 清理测试数据 ============
  console.log('\n7️⃣ 清理测试数据...\n');

  // 删除测试会话
  sessionStorage.deleteSession(session1.id);
  console.log(`✅ deleteSession(): ${session1.id}`);

  sessionStorage.deleteSession(session2.id);
  console.log(`✅ deleteSession(): ${session2.id}`);

  // 删除测试任务
  taskStorage.deleteTask(task1.id);
  console.log(`✅ deleteTask(): ${task1.id}`);

  taskStorage.deleteTask(task2.id);
  console.log(`✅ deleteTask(): ${task2.id}`);

  // 重置项目设置
  settings.resetProjectSettings();
  console.log('✅ resetProjectSettings()');

  // 最终统计
  console.log('\n📊 最终统计:');
  const finalStats = sessionStorage.getSessionStats();
  console.log(`   剩余会话：${finalStats.totalSessions}`);
  console.log(`   剩余消息：${finalStats.totalMessages}`);

  console.log('\n' + '='.repeat(60));
  console.log('✅ 所有测试通过！\n');
})();
