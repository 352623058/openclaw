# 🧠 Agent-Driven Obsidian Vault

这是一个由本地大语言模型（OpenClaw）通过 `knowledge-pipeline` 技能全自动管理的 Obsidian 知识库。

## 🤖 自动化工作流声明
- **触发机制**：通过聊天发送 `Memo: ` 前缀，或通过每日晚间 21:00 定时整理触发。
- **Git 策略**：全自动化。脚本执行完毕后自动触发 `git add .` -> `commit` -> `push`。

## 📁 目录架构与物理路由规则
本知识库通过文件所在的【父文件夹名称】直接决定读写权限，实现严格的物理隔离：

### 🔴 30-Dynamic/ (全局覆写区 — Overwrite Only)
- **包含文件**：`考研进度总览.md`、`考研计划表.md` 等需要长期维护的汇总/计划表。
- **操作规则**：Agent 拥有覆写权限。必须先读取旧内容，与新输入逻辑合并后，完整覆写。

### 🟢 00-Inbox/、10-Projects/、20-Areas/ (全局追加区 — Append Only)
- **包含文件**：`20-Areas/考研记录.md`、`20-Areas/股票投资.md`、`00-Inbox/YYYY-MM-DD.md` 等日常流水。
- **操作规则**：【绝对禁止覆盖原文件】。一律使用追加（Append）模式写入末尾。
