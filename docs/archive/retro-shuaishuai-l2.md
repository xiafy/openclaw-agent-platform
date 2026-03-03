# Shuaishuai Agent (L2) 部署复盘报告

> **日期**: 2026-02-27
> **项目**: Agent Platform - L2 独立用户部署
> **目标**: 创建个人生活助理 Agent (shuaishuai)，L2 级别隔离
> **耗时**: 约 2.5 小时
> **状态**: ✅ 完成

---

## 一、执行摘要

### 成果
- ✅ 创建独立 macOS 用户 `shuaishuai` (UID 502)
- ✅ 部署 OpenClaw Gateway (端口 19002)
- ✅ 配置 Telegram Bot (@shuaishuai1989_bot)
- ✅ 共享层 symlink (skills + protocols + knowledge)
- ✅ LaunchDaemon 开机自启
- ✅ 模型配置同步 (DashScope + Anthropic + Fireworks)

### 核心挑战
1. **brew 权限问题** - 新用户无法使用 brew (需 chown /opt/homebrew)
2. **npm 全局安装权限** - 需给新用户 npm 目录权限
3. **LaunchAgent vs LaunchDaemon** - L2 用户无 GUI 会话，必须用 LaunchDaemon
4. **Auth 配置复制** - 需复制 `auth-profiles.json` 而非 `auth.json`

---

## 二、完整执行流程 (SOP v1.0)

### Phase 0: 前置准备 (10 min)

| 步骤 | 操作 | 负责人 | 备注 |
|------|------|--------|------|
| 0.1 | Telegram @BotFather 创建 Bot | 夏总 | 记录 Token |
| 0.2 | 确认共享层存在 | Claw | `/Users/Shared/openclaw-common/` |
| 0.3 | 检查 UID 占用 | Claw | `dscl . -list /Users UniqueID` |

### Phase 1: 创建 macOS 用户 (5 min)

```bash
# 创建用户 (UID 从 502 开始，501=xiafybot)
sudo dscl . -create /Users/shuaishuai
sudo dscl . -create /Users/shuaishuai UserShell /bin/zsh
sudo dscl . -create /Users/shuaishuai RealName "Shuaishuai Agent"
sudo dscl . -create /Users/shuaishuai UniqueID "502"
sudo dscl . -create /Users/shuaishuai PrimaryGroupID 20
sudo dscl . -create /Users/shuaishuai NFSHomeDirectory /Users/shuaishuai
sudo createhomedir -c -u shuaishuai

# 设置密码
sudo passwd shuaishuai
```

### Phase 2: 安装 NodeJS + OpenClaw (15 min)

```bash
# 给新用户 brew 权限
sudo chown -R shuaishuai /opt/homebrew

# 安装 NodeJS 和 OpenClaw
su - shuaishuai -c "brew install node@20"
su - shuaishuai -c "npm install -g openclaw --force"

# 创建目录结构
su - shuaishuai -c "mkdir -p ~/.openclaw/workspace"
```

**⚠️ 踩坑 #1**: npm 全局安装需要权限，`--force` 可绕过警告

### Phase 3: 配置 openclaw.json (10 min)

```bash
# 复制 claw 的配置作为模板
cp ~/.openclaw/openclaw.json /Users/shuaishuai/.openclaw/openclaw.json
chown shuaishuai:staff /Users/shuaishuai/.openclaw/openclaw.json

# 修改关键配置
# - gateway.port: 19002
# - channels.telegram.botToken: <新 Bot Token>
```

**配置模板** (关键部分):
```json
{
  "env": {
    "DASHSCOPE_API_KEY": "sk-xxx"
  },
  "gateway": {
    "port": 19002
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "8343182214:AAGEK-xxx"
    }
  }
}
```

### Phase 4: 配置共享层 symlink (10 min)

```bash
# 创建目录
su - shuaishuai -c "mkdir -p ~/.openclaw/workspace/{skills,protocols,knowledge,memory}"

# 创建 symlink
su - shuaishuai -c "ln -s /Users/Shared/openclaw-common/skills/summarize ~/.openclaw/workspace/skills/summarize"
su - shuaishuai -c "ln -s /Users/Shared/openclaw-common/skills/meeting-notes ~/.openclaw/workspace/skills/meeting-notes"
su - shuaishuai -c "ln -s /Users/Shared/openclaw-common/skills/domain-model-extract ~/.openclaw/workspace/skills/domain-model-extract"
su - shuaishuai -c "ln -s /Users/Shared/openclaw-common/protocols ~/.openclaw/workspace/protocols"
su - shuaishuai -c "ln -s /Users/Shared/openclaw-common/knowledge ~/.openclaw/workspace/knowledge"

# 设置共享层权限
sudo chmod -R 755 /Users/Shared/openclaw-common/
```

### Phase 5: 创建人设文件 (5 min)

```bash
# IDENTITY.md
su - shuaishuai -c "cat > ~/.openclaw/workspace/IDENTITY.md << 'EOF'
# IDENTITY.md - Who Am I?
- **Name:** Shuaishuai
- **Creature:** AI assistant — 生活管家
- **Vibe:** 温暖、贴心、实用、不啰嗦
- **Emoji:** 🌟
EOF"

# SOUL.md
su - shuaishuai -c "cat > ~/.openclaw/workspace/SOUL.md << 'EOF'
# SOUL.md - Who You Are
_You're not a chatbot. You're becoming someone._
## Core Truths
Be genuinely helpful, not performatively helpful.
Have opinions.
Be resourceful before asking.
EOF"
```

### Phase 6: 复制 Auth 配置 (5 min) ⭐ 关键

```bash
# 复制 auth-profiles.json (包含 OAuth token 和 API Keys)
sudo cp ~/.openclaw/agents/main/agent/auth-profiles.json \
  /Users/shuaishuai/.openclaw/agents/main/agent/auth-profiles.json
sudo chown shuaishuai:staff \
  /Users/shuaishuai/.openclaw/agents/main/agent/auth-profiles.json
```

**⚠️ 踩坑 #2**: 必须复制 `auth-profiles.json`，不是 `auth.json`！

### Phase 7: 配置 LaunchDaemon (10 min)

```bash
# 创建 LaunchDaemon 配置文件 (系统级，不需要 GUI 会话)
sudo cat > /Library/LaunchDaemons/ai.openclaw.shuaishuai.gateway.plist << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.shuaishuai.gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/openclaw</string>
        <string>gateway</string>
        <string>--port</string>
        <string>19002</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/shuaishuai</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/openclaw-shuaishuai/openclaw.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/openclaw-shuaishuai/openclaw.err</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>DASHSCOPE_API_KEY</key>
        <string>sk-d78d39b07b46464c82f0ac50904239e1</string>
    </dict>
    <key>UserName</key>
    <string>shuaishuai</string>
</dict>
</plist>
PLIST

# 设置权限
sudo chown root:wheel /Library/LaunchDaemons/ai.openclaw.shuaishuai.gateway.plist
sudo chmod 644 /Library/LaunchDaemons/ai.openclaw.shuaishuai.gateway.plist

# 加载并启动
sudo launchctl bootstrap system /Library/LaunchDaemons/ai.openclaw.shuaishuai.gateway.plist
```

**⚠️ 踩坑 #3**: L2 用户没有 GUI 会话，LaunchAgent 会失败，必须用 LaunchDaemon！

### Phase 8: Telegram 配对 (2 min)

```bash
# 获取配对码 (从错误日志或系统消息)
# 执行批准命令
openclaw pairing approve telegram <CODE>
```

### Phase 9: 验证 (5 min)

```bash
# 检查进程
ps aux | grep "openclaw.*19002" | grep -v grep

# 检查日志
tail -20 /tmp/openclaw-shuaishuai/openclaw.log

# Telegram 测试
# 向 @shuaishuai1989_bot 发送 /start
```

---

## 三、踩坑记录与解决方案

### 踩坑 #1: brew 权限问题
**现象**: `su - shuaishuai -c "brew install node"` 报错 "not writable"
**原因**: brew 目录属于 xiafybot 用户
**解决**: `sudo chown -R shuaishuai /opt/homebrew`

### 踩坑 #2: npm 全局安装权限
**现象**: `npm install -g openclaw` 报错 EACCES
**原因**: npm 全局目录权限不足
**解决**: `sudo chown -R shuaishuai /opt/homebrew/lib/node_modules` 或加 `--force`

### 踩坑 #3: LaunchAgent 失败
**现象**: `launchctl bootstrap gui/502 ...` 报错 "Domain does not support specified action"
**原因**: shuaishuai 用户从未登录 GUI，没有 gui/502 session
**解决**: 改用 LaunchDaemon (系统级)，放在 `/Library/LaunchDaemons/`

### 踩坑 #4: Auth 配置复制错误
**现象**: "No API key found for provider anthropic"
**原因**: 复制了 `auth.json` 而非 `auth-profiles.json`
**解决**: 复制 `~/.openclaw/agents/main/agent/auth-profiles.json`

### 踩坑 #5: su 切换用户需要密码
**现象**: `su - shuaishuai` 需要输入 shuaishuai 密码
**原因**: macOS 安全机制
**解决**: 提前设置密码，或用 `sudo -u shuaishuai` (部分命令有效)

---

## 四、最佳实践总结

### 1. 用户命名规范
- 使用有意义的名称 (如 `shuaishuai` 而非 `user2`)
- UID 从 502 开始递增 (501=第一个用户)
- 记录在文档中

### 2. 配置管理
- openclaw.json 从主用户复制模板，修改端口和 Bot Token
- auth-profiles.json 必须复制 (包含 OAuth 和 API Keys)
- 敏感信息不存聊天记录，用安全渠道传输

### 3. 启动方式选择
| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| 有 GUI 会话的用户 | LaunchAgent | 用户级，易管理 |
| 无 GUI 会话的用户 | LaunchDaemon | 系统级，开机自启 |
| 测试/临时 | `openclaw gateway &` | 快速验证 |

### 4. 共享层策略
- 通用知识：`/Users/Shared/openclaw-common/` (只读 symlink)
- 角色专属：各用户 `~/.openclaw/workspace/` 独立目录
- 权限：`chmod -R 755` 确保可读

### 5. 日志管理
- 日志路径：`/tmp/openclaw-<UID>/openclaw.log`
- 定期清理：`find /tmp -name "openclaw*.log" -mtime +7 -delete`

---

## 五、下次部署优化 (v2.0 计划)

### 自动化脚本
```bash
#!/bin/bash
# deploy-l2-agent.sh <username> <port> <bot-token>
# 一键部署 L2 Agent
```

### 配置模板化
- 创建 `l2-agent-config-template.json`
- 用 sed 替换变量 (端口、Token、用户名)

### 验证自动化
- 创建 `verify-l2-agent.sh` 脚本
- 自动检查进程、端口、日志、symlink

### 文档改进
- 创建检查清单 (Checklist)
- 每个 Phase 完成后打勾

---

## 六、时间分配回顾

| Phase | 计划时间 | 实际时间 | 偏差原因 |
|-------|---------|---------|---------|
| Phase 0: 准备 | 10 min | 10 min | - |
| Phase 1: 用户 | 5 min | 10 min | 密码设置沟通 |
| Phase 2: 安装 | 15 min | 30 min | brew/npm 权限问题 |
| Phase 3: 配置 | 10 min | 15 min | 手动编辑 JSON |
| Phase 4: symlink | 10 min | 10 min | - |
| Phase 5: 人设 | 5 min | 5 min | - |
| Phase 6: Auth | 5 min | 10 min | 踩坑 #4 重试 |
| Phase 7: Daemon | 10 min | 20 min | 踩坑 #3 切换方案 |
| Phase 8: 配对 | 2 min | 5 min | 等待系统消息 |
| Phase 9: 验证 | 5 min | 10 min | 日志检查 |
| **总计** | **77 min** | **125 min** | **+62%** |

**主要偏差来源**: 权限问题 (30 min) + LaunchDaemon 切换 (20 min) + Auth 配置 (10 min)

---

## 七、关键文件清单

| 文件 | 路径 | 用途 |
|------|------|------|
| LaunchDaemon | `/Library/LaunchDaemons/ai.openclaw.shuaishuai.gateway.plist` | 开机自启 |
| 主配置 | `/Users/shuaishuai/.openclaw/openclaw.json` | Gateway 配置 |
| Auth 配置 | `/Users/shuaishuai/.openclaw/agents/main/agent/auth-profiles.json` | API Keys + OAuth |
| 人设文件 | `/Users/shuaishuai/.openclaw/workspace/{IDENTITY,SOUL}.md` | Agent 人格 |
| 日志 | `/tmp/openclaw-shuaishuai/openclaw.log` | 运行日志 |
| 项目文档 | `~/Documents/claw-outputs/projects/agent-platform/docs/` | 架构说明 |

---

*文档路径：`~/Documents/claw-outputs/projects/agent-platform/docs/retro-shuaishuai-l2.md`*
