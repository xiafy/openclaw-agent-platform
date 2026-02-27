# L2 Agent 极简配置指南

> **版本**: v1.0
> **日期**: 2026-02-27
> **理念**: 只配置能力，不预加载记忆，在使用中建立

---

## 🎯 配置原则

### ✅ 配置什么

1. **工作方法** — AGENTS.md (六步法、纠错协议)
2. **工具说明** — TOOLS.md (工具使用指南)
3. **模型配置** — models.json (模型别名)
4. **能力目录** — sessions/ credentials/ browser/ logs/
5. **Skills** — summarize, domain-model-extract (symlink)

### ❌ 不配置什么

1. **MEMORY.md** — 不预加载记忆，对话中建立
2. **USER.md** — 用户画像在互动中形成
3. **定时任务** — cron/ 按需配置
4. **多设备** — devices/ 按需配置

---

## 🚀 5 步配置流程 (10 min)

### Step 1: 复制核心文档 (2 min)

```bash
sudo cp ~/.openclaw/workspace/AGENTS.md /Users/<username>/.openclaw/workspace/AGENTS.md
sudo cp ~/.openclaw/workspace/TOOLS.md /Users/<username>/.openclaw/workspace/TOOLS.md
echo "<sudo 密码>" | sudo -S /usr/sbin/chown <username>:staff /Users/<username>/.openclaw/workspace/{AGENTS,TOOLS}.md
```

### Step 2: 创建能力目录 (2 min)

```bash
echo "<sudo 密码>" | sudo -S mkdir -p /Users/<username>/.openclaw/{sessions,credentials,browser,logs}
echo "<sudo 密码>" | sudo -S /usr/sbin/chown -R <username>:staff /Users/<username>/.openclaw/{sessions,credentials,browser,logs}
```

### Step 3: 复制模型配置 (2 min)

```bash
echo "<sudo 密码>" | sudo -S cp ~/.openclaw/agents/main/agent/models.json /Users/<username>/.openclaw/agents/main/agent/models.json
echo "<sudo 密码>" | sudo -S /usr/sbin/chown <username>:staff /Users/<username>/.openclaw/agents/main/agent/models.json
```

### Step 4: 复制环境变量 (2 min)

```bash
sudo cp ~/.openclaw/workspace/.env /Users/<username>/.openclaw/workspace/.env
echo "<sudo 密码>" | sudo -S /usr/sbin/chown <username>:staff /Users/<username>/.openclaw/workspace/.env
```

### Step 5: 重启 Gateway (2 min)

```bash
echo "<sudo 密码>" | sudo -S launchctl kickstart -k system/ai.openclaw.<username>.gateway
```

---

## ✅ 验证测试

### 测试 1: 工作流程
```
发送：你的工作流程是什么？
预期：回答六步法 (需求对齐→需求文档→制定计划→执行→验证→复盘)
```

### 测试 2: 纠错协议
```
发送：如果你的回答错了怎么办？
预期：回答 STOP→VERIFY→COMPARE→CORRECT
```

### 测试 3: 模型切换
```
发送：用 opus 模型写一首诗
预期：使用 claude-opus-4-6 回答
```

### 测试 4: 搜索
```
发送：搜索一下 2026 AI Agent 趋势
预期：返回 web_search 结果
```

### 测试 5: Skills
```
发送：总结这个链接 <URL>
预期：使用 summarize skill
```

---

## 📁 配置后结构

```
/Users/<username>/.openclaw/
├── workspace/
│   ├── AGENTS.md              ← 工作原则 ✅
│   ├── TOOLS.md               ← 工具说明 ✅
│   ├── IDENTITY.md            ← Agent 人设 (独立)
│   ├── SOUL.md                ← Agent 灵魂 (独立)
│   ├── .env                   ← 环境变量 ✅
│   ├── skills/                ← symlink → 共享层
│   ├── protocols/             ← symlink → 共享层
│   └── knowledge/             ← symlink → 共享层
├── agents/main/agent/
│   ├── auth-profiles.json     ← API Keys ✅
│   └── models.json            ← 模型配置 ✅
├── sessions/                  ← 会话历史 (空，使用中建立)
├── credentials/               ← OAuth (空，按需使用)
├── browser/                   ← 浏览器数据 (空，使用中建立)
└── logs/                      ← 日志目录 ✅
```

---

## 🎓 与完整配置对比

| 配置项 | 极简模式 | 完整模式 | 说明 |
|-------|---------|---------|------|
| AGENTS.md | ✅ | ✅ | 工作原则 |
| TOOLS.md | ✅ | ✅ | 工具说明 |
| models.json | ✅ | ✅ | 模型配置 |
| auth-profiles.json | ✅ | ✅ | API Keys |
| MEMORY.md | ❌ | ✅ | 长期记忆 |
| USER.md | ❌ | ✅ | 用户画像 |
| sessions/ | ✅ (空) | ✅ (空) | 会话目录 |
| browser/ | ✅ (空) | ✅ (空) | 浏览器目录 |
| cron/ | ❌ | ✅ | 定时任务 |
| devices/ | ❌ | ✅ | 多设备 |
| canvas/ | ❌ | ✅ | UI 展示 |
| 配置耗时 | 10 min | 60 min | |
| 适用场景 | 快速启动 | 生产部署 | |

---

## 🔄 后续扩展

### 需要记忆时
```bash
# 复制 MEMORY.md
sudo cp ~/.openclaw/workspace/MEMORY.md /Users/<username>/.openclaw/workspace/
```

### 需要定时任务时
```bash
# 配置 cron 目录
echo "<sudo 密码>" | sudo -S mkdir -p /Users/<username>/.openclaw/cron
```

### 需要会议纪要时
```bash
# meeting-notes skill 已 symlink，直接使用
```

---

## 💡 最佳实践

1. **先极简启动** — 10 min 完成配置，快速验证
2. **使用中建立** — 记忆和偏好在对话中自然形成
3. **按需扩展** — 需要什么能力再加什么配置
4. **保持轻量** — 避免预加载不必要的记忆和配置

---

*文档路径：`~/Documents/claw-outputs/projects/agent-platform/docs/sop-minimal-setup.md`*
