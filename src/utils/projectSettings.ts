/**
 * 项目设置管理
 * 
 * 参考 claude-code-learning/src/utils/settings/settings.ts
 * 支持多层级设置：全局 → 项目 → 会话
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { getProjectRoot, getSessionStorageDir } from '../bootstrap/state.js';
import { debug, warn } from './logger.js';

/**
 * 设置接口
 */
export interface Settings {
  /** 模型名称 */
  model?: string;
  
  /** 最大 token 数 */
  maxTokens?: number;
  
  /** 温度参数 */
  temperature?: number;
  
  /** 思考模式 */
  thinking?: 'on' | 'off' | 'auto';
  
  /** 快速模式 */
  fastMode?: boolean;
  
  /** 详细模式 */
  verbose?: boolean;
  
  /** 自动保存会话 */
  autoSaveSession?: boolean;
  
  /** MCP 服务器配置 */
  mcpServers?: Record<string, McpServerConfig>;
  
  /** 工具权限 */
  toolPermissions?: ToolPermissions;
}

/**
 * MCP 服务器配置
 */
export interface McpServerConfig {
  command: string;
  args?: string[];
  env?: Record<string, string>;
}

/**
 * 工具权限
 */
export interface ToolPermissions {
  /** 始终允许的工具 */
  allowAlways?: string[];
  
  /** 需要确认的工具 */
  requireConfirm?: string[];
  
  /** 禁止的工具 */
  deny?: string[];
}

/**
 * 设置文件路径
 */
const SETTINGS_FILES = {
  /** 全局设置 */
  global: () => join(process.env.HOME || process.env.USERPROFILE || '', '.source-deploy', 'settings.json'),
  
  /** 项目设置 */
  project: () => join(getProjectRoot(), '.source-deploy', 'settings.json'),
  
  /** 会话设置 */
  session: () => join(getSessionStorageDir(), '.source-deploy', 'session-settings.json'),
};

/**
 * 读取设置文件
 */
function readSettingsFile(path: string): Settings {
  try {
    if (!existsSync(path)) {
      return {};
    }
    const content = readFileSync(path, 'utf-8');
    return JSON.parse(content) as Settings;
  } catch (error) {
    warn(`Failed to read settings from ${path}: ${error}`);
    return {};
  }
}

/**
 * 写入设置文件
 */
function writeSettingsFile(path: string, settings: Settings): void {
  try {
    const dir = dirname(path);
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
    writeFileSync(path, JSON.stringify(settings, null, 2), 'utf-8');
    debug(`Saved settings to ${path}`);
  } catch (error) {
    warn(`Failed to write settings to ${path}: ${error}`);
  }
}

/**
 * 合并设置（后者覆盖前者）
 */
function mergeSettings(...settings: Settings[]): Settings {
  const result: Settings = {};
  for (const settings of settings) {
    Object.assign(result, settings);
  }
  return result;
}

/**
 * 获取合并后的设置
 * 优先级：会话 > 项目 > 全局
 */
export function getSettings(): Settings {
  const global = readSettingsFile(SETTINGS_FILES.global());
  const project = readSettingsFile(SETTINGS_FILES.project());
  const session = readSettingsFile(SETTINGS_FILES.session());
  
  return mergeSettings(global, project, session);
}

/**
 * 获取全局设置
 */
export function getGlobalSettings(): Settings {
  return readSettingsFile(SETTINGS_FILES.global());
}

/**
 * 获取项目设置
 */
export function getProjectSettings(): Settings {
  return readSettingsFile(SETTINGS_FILES.project());
}

/**
 * 获取会话设置
 */
export function getSessionSettings(): Settings {
  return readSettingsFile(SETTINGS_FILES.session());
}

/**
 * 更新全局设置
 */
export function updateGlobalSettings(changes: Partial<Settings>): void {
  const current = getGlobalSettings();
  const updated = { ...current, ...changes };
  writeSettingsFile(SETTINGS_FILES.global(), updated);
}

/**
 * 更新项目设置
 */
export function updateProjectSettings(changes: Partial<Settings>): void {
  const current = getProjectSettings();
  const updated = { ...current, ...changes };
  writeSettingsFile(SETTINGS_FILES.project(), updated);
}

/**
 * 更新会话设置
 */
export function updateSessionSettings(changes: Partial<Settings>): void {
  const current = getSessionSettings();
  const updated = { ...current, ...changes };
  writeSettingsFile(SETTINGS_FILES.session(), updated);
}

/**
 * 重置项目设置
 */
export function resetProjectSettings(): void {
  const path = SETTINGS_FILES.project();
  if (existsSync(path)) {
    const { unlinkSync } = require('fs');
    unlinkSync(path);
    debug('Reset project settings');
  }
}

/**
 * 获取特定设置值
 */
export function getSetting<K extends keyof Settings>(key: K): Settings[K] | undefined {
  const settings = getSettings();
  return settings[key];
}

/**
 * 设置特定设置值（保存到会话级别）
 */
export function setSetting<K extends keyof Settings>(key: K, value: Settings[K]): void {
  const current = getSessionSettings();
  const updated = { ...current, [key]: value };
  writeSettingsFile(SETTINGS_FILES.session(), updated);
}

/**
 * 初始化默认项目设置
 */
export function initProjectSettings(): void {
  const path = SETTINGS_FILES.project();
  if (!existsSync(path)) {
    const defaultSettings: Settings = {
      model: 'qwen3.5-plus',
      maxTokens: 4096,
      temperature: 0.7,
      thinking: 'auto',
      fastMode: false,
      verbose: false,
      autoSaveSession: true,
    };
    writeSettingsFile(path, defaultSettings);
    debug('Initialized project settings with defaults');
  }
}
