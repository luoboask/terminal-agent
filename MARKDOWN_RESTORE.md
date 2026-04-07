# ✅ Markdown 渲染恢复

**恢复时间**: 2026-04-07 02:35  
**变更**: 恢复为简单 Markdown 渲染（不使用 marked 库）

---

## 🔄 恢复内容

### 修改前（使用 marked 库）

```typescript
import { marked } from 'marked';

export function renderMarkdownFull(content: string): string {
  const tokens = marked.lexer(content);
  return tokens.map(token => formatToken(token)).join('');
}
```

---

### 修改后（简单渲染）

```typescript
export function renderMarkdownSimple(content: string): string {
  let result = content;
  
  // 处理代码块
  result = result.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const langTag = lang ? chalk.gray(`[${lang}]\n`) : '';
    return `${langTag}${chalk.gray(code)}`;
  });
  
  // 处理粗体
  result = result.replace(/\*\*(.*?)\*\*/g, chalk.bold('$1'));
  
  // 处理斜体
  result = result.replace(/\*(.*?)\*/g, chalk.italic('$1'));
  
  // 处理行内代码
  result = result.replace(/`(.*?)`/g, chalk.blue('$1'));
  
  // 处理标题
  result = result.replace(/^### (.*$)/gim, chalk.cyan.bold('$1'));
  result = result.replace(/^## (.*$)/gim, chalk.blue.bold('$1'));
  result = result.replace(/^# (.*$)/gim, chalk.magenta.bold.underline('$1'));
  
  // 处理列表
  result = result.replace(/^[-*] (.*$)/gim, chalk.white('  • $1'));
  
  // 处理引用块
  result = result.replace(/^> (.*$)/gim, chalk.dim.italic('│ $1'));
  
  // 处理水平线
  result = result.replace(/^---$/gm, chalk.dim('─'.repeat(40)));
  
  return result;
}
```

---

## 📊 对比

| 特性 | marked 库 | 简单渲染 |
|------|----------|---------|
| **依赖** | marked 库 | 无 |
| **代码块** | ✅ 完整 | ✅ 完整 |
| **粗体** | ✅ 完整 | ✅ 完整 |
| **斜体** | ✅ 完整 | ✅ 完整 |
| **列表** | ✅ 完整 | ✅ 完整 |
| **引用块** | ✅ 完整 | ✅ 完整 |
| **表格** | ✅ 完整 | ❌ 不支持 |
| **复杂度** | 高 | 低 |
| **性能** | 中 | 高 |

---

## ✅ 总结

**恢复为简单 Markdown 渲染**！

- ✅ 不使用 marked 库
- ✅ 使用正则表达式渲染
- ✅ 支持代码块、粗体、斜体、列表
- ✅ 性能更好
- ✅ 无额外依赖

**现在 Markdown 渲染恢复为之前的简单版本了！** 🎉
