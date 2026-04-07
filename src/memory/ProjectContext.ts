import { writeFileSync, readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { debug, info, error } from '../utils/logger.js';

/**
 * 项目上下文 (Project Context)
 * 
 * 参考自 source/src/context.ts 和项目特定配置
 * 
 * 特点：
 * - 项目特定的配置和知识
 * - .claude/agents/ 目录中的 Agent 定义
 * - 项目架构和约定
 */

export interface ProjectContextData {
  // 项目基本信息
  name?: string;
  description?: string;
  version?: string;
  
  // 技术栈
  languages?: string[];
  frameworks?: string[];
  tools?: string[];
  
  // 项目结构
  srcDir?: string;
  testDir?: string;
  docsDir?: string;
  
  // 构建和运行
  buildCommand?: string;
  testCommand?: string;
  startCommand?: string;
  
  // 代码规范和约定
  conventions?: string[];
  
  // 重要文件和目录
  keyFiles?: string[];
  keyDirectories?: string[];
  
  // 依赖关系
  dependencies?: Record<string, string>;
  
  // 环境变量
  envVars?: string[];
  
  // 其他元数据
  metadata?: Record<string, unknown>;
}

export interface ProjectContextConfig {
  projectRoot: string;
  contextFile?: string; // 默认为 .source-deploy-context.json
}

/**
 * 项目上下文管理器
 * 
 * 管理项目特定的配置和知识，包括：
 * - 项目结构和架构
 * - 技术栈和工具
 * - 构建和测试命令
 * - 代码规范和约定
 */
export class ProjectContext {
  private config: ProjectContextConfig;
  private context: ProjectContextData = {};
  private initialized = false;

  constructor(config: ProjectContextConfig) {
    this.config = {
      ...config,
      contextFile: config.contextFile || '.source-deploy-context.json',
    };
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;

    const contextPath = join(this.config.projectRoot, this.config.contextFile!);

    if (existsSync(contextPath)) {
      try {
        const content = readFileSync(contextPath, 'utf-8');
        this.context = JSON.parse(content);
        info(`Loaded project context: ${this.context.name || 'unnamed'}`);
      } catch (err) {
        error('Failed to load project context:', err);
      }
    } else {
      // 尝试从 package.json 或其他配置文件自动发现
      await this.autoDiscover();
    }

    this.initialized = true;
  }

  /**
   * 自动发现项目信息
   */
  private async autoDiscover(): Promise<void> {
    const { projectRoot } = this.config;

    // 尝试读取 package.json
    try {
      const packageJsonPath = join(projectRoot, 'package.json');
      if (existsSync(packageJsonPath)) {
        const pkg = JSON.parse(readFileSync(packageJsonPath, 'utf-8'));
        
        this.context.name = pkg.name;
        this.context.description = pkg.description;
        this.context.version = pkg.version;
        
        if (pkg.scripts) {
          this.context.buildCommand = pkg.scripts.build;
          this.context.testCommand = pkg.scripts.test;
          this.context.startCommand = pkg.scripts.start;
        }

        if (pkg.dependencies) {
          this.context.dependencies = pkg.dependencies;
        }

        debug('Auto-discovered project info from package.json');
      }
    } catch (err) {
      debug('No package.json found or failed to parse');
    }

    // 检测语言
    this.context.languages = [];
    if (existsSync(join(projectRoot, 'tsconfig.json'))) {
      this.context.languages?.push('typescript');
    }
    if (existsSync(join(projectRoot, 'pyproject.toml')) || 
        existsSync(join(projectRoot, 'setup.py')) ||
        existsSync(join(projectRoot, 'requirements.txt'))) {
      this.context.languages?.push('python');
    }
    if (existsSync(join(projectRoot, 'Cargo.toml'))) {
      this.context.languages?.push('rust');
    }
    if (existsSync(join(projectRoot, 'go.mod'))) {
      this.context.languages?.push('go');
    }

    // 检测框架
    this.context.frameworks = [];
    if (this.context.dependencies) {
      const deps = this.context.dependencies;
      if (deps.react) this.context.frameworks?.push('react');
      if (deps.vue) this.context.frameworks?.push('vue');
      if (deps['next']) this.context.frameworks?.push('nextjs');
      if (deps.express) this.context.frameworks?.push('express');
    }

    // 设置默认目录
    this.context.srcDir = 'src';
    this.context.testDir = 'tests';
    this.context.docsDir = 'docs';
  }

  /**
   * 更新项目上下文
   */
  update(data: Partial<ProjectContextData>): void {
    this.context = { ...this.context, ...data };
    this.save();
    info('Updated project context');
  }

  /**
   * 保存项目上下文
   */
  save(): void {
    const contextPath = join(this.config.projectRoot, this.config.contextFile!);
    
    try {
      writeFileSync(contextPath, JSON.stringify(this.context, null, 2), 'utf-8');
    } catch (err) {
      error('Failed to save project context:', err);
    }
  }

  /**
   * 获取项目上下文
   */
  get(): ProjectContextData {
    return { ...this.context };
  }

  /**
   * 获取特定字段
   */
  getField<K extends keyof ProjectContextData>(field: K): ProjectContextData[K] {
    return this.context[field];
  }

  /**
   * 生成系统提示的项目上下文部分
   */
  toSystemPrompt(): string {
    const parts: string[] = [];

    if (this.context.name) {
      parts.push(`## Project: ${this.context.name}`);
      
      if (this.context.description) {
        parts.push(this.context.description);
      }
    }

    if (this.context.languages && this.context.languages.length > 0) {
      parts.push(`\n**Languages:** ${this.context.languages.join(', ')}`);
    }

    if (this.context.frameworks && this.context.frameworks.length > 0) {
      parts.push(`**Frameworks:** ${this.context.frameworks.join(', ')}`);
    }

    if (this.context.conventions && this.context.conventions.length > 0) {
      parts.push('\n**Conventions:**');
      for (const conv of this.context.conventions) {
        parts.push(`- ${conv}`);
      }
    }

    if (this.context.keyFiles && this.context.keyFiles.length > 0) {
      parts.push('\n**Key Files:**');
      for (const file of this.context.keyFiles) {
        parts.push(`- ${file}`);
      }
    }

    return parts.join('\n');
  }
}
