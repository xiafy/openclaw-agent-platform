# L2 Agent 部署指南

> **版本**: v2.0
> **更新日期**: 2026-02-27
> **两种模式**: 极简 (10 min) / 完整 (90 min)

---

## 🎯 选择部署模式

| 模式 | 适用场景 | 耗时 | 文档 |
|------|---------|------|------|
| **极简模式** ⭐ | 已有 macOS 用户，快速启动 | 10 min | `sop-l2-minimal-setup.md` |
| **完整模式** | 从零开始，创建新用户 | 90 min | 本文档 |

---

## 📦 完整模式 - 前置条件

- [ ] macOS 管理员 sudo 权限
- [ ] Telegram Bot Token (@BotFather)
- [ ] 共享层已存在 (`/Users/Shared/openclaw-common/`)
- [ ] 主用户 OpenClaw 正常运行

---

## 🚀 9 步部署流程 (完整模式)

### 1️⃣ 创建用户 (5 min)

```bash
# 检查 UID 是否被占用
dscl . -list /Users UniqueID | grep <目标 UID>

# 创建用户 (UID 从 502 开始，501=xiafybot)
sudo dscl . -create /Users/<username>
sudo dscl . -create /Users/<username> UserShell /bin/zsh
sudo dscl . -create /Users/<username> RealName "<显示名称>"
sudo dscl . -create /Users/<username> UniqueID "<UID>"
sudo dscl . -create /Users/<username> PrimaryGroupID 20
sudo dscl . -create /Users/<username> NFSHomeDirectory /Users/<username>
sudo createhomedir -c -u <username>

# 设置密码
sudo passwd <username>
```

**✅ 验证**:
```bash
dscl . -read /Users/<username> UniqueID NFSHomeDirectory
```

---

### 2️⃣ 安装 NodeJS + OpenClaw (15 min)

```bash
# 给新用户 brew 权限
sudo chown -R <username> /opt/homebrew

# 安装 NodeJS
su - <username> -c "brew install node@20"

# 安装 OpenClaw (加 --force 避免权限警告)
su - <username> -c "npm install -g openclaw --force"

# 创建基础目录
su - <username> -c "mkdir -p ~/.openclaw/workspace"
```

**✅ 验证**:
```bash
su - <username> -c "node --version"
su - <username> -c "openclaw --version"
```

---

### 3️⃣ 配置 openclaw.json (10 min)

```bash
# 复制模板
cp ~/.openclaw/openclaw.json /Users/<username>/.openclaw/openclaw.json
chown <username>:staff /Users/<username>/.openclaw/openclaw.json

# 编辑配置 (用 nano 或手动)
# 修改以下字段:
# - gateway.port: <目标端口>
# - channels.telegram.botToken: <Bot Token>
```

**配置检查点**:
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

---

### 4️⃣ 配置共享层 symlink (10 min)

```bash
# 创建目录结构
su - <username> -c "mkdir -p ~/.openclaw/workspace/{skills,protocols,knowledge,memory}"

# 创建 symlink
su - <username> -c "ln -s /Users/Shared/openclaw-common/skills/summarize ~/.openclaw/workspace/skills/summarize"
su - <username> -c "ln -s /Users/Shared/openclaw-common/skills/meeting-notes ~/.openclaw/workspace/skills/meeting-notes"
su - <username> -c "ln -s /Users/Shared/openclaw-common/skills/domain-model-extract ~/.openclaw/workspace/skills/domain-model-extract"
su - <username> -c "ln -s /Users/Shared/openclaw-common/protocols ~/.openclaw/workspace/protocols"
su - <username> -c "ln -s /Users/Shared/openclaw-common/knowledge ~/.openclaw/workspace/knowledge"

# 设置共享层权限
sudo chmod -R 755 /Users/Shared/openclaw-common/
```

**✅ 验证**:
```bash
su - <username> -c "ls -la ~/.openclaw/workspace/"
```

---

### 5️⃣ 创建人设文件 (5 min)

```bash
# IDENTITY.md
su - <username> -c "cat > ~/.openclaw/workspace/IDENTITY.md << 'EOF'
# IDENTITY.md - Who Am I?
- **Name:** <显示名称>
- **Creature:** AI assistant — <角色描述>
- **Vibe:** <性格特点>
- **Emoji:** <emoji>
EOF"

# SOUL.md (使用通用模板)
su - <username> -c "cat > ~/.openclaw/workspace/SOUL.md << 'EOF'
# SOUL.md - Who You Are
_You're not a chatbot. You're becoming someone._
## Core Truths
Be genuinely helpful, not performatively helpful.
Have opinions.
Be resourceful before asking.
EOF"
```

---

### 6️⃣ 复制 Auth 配置 ⭐ 关键 (5 min)

```bash
# 创建目录
sudo mkdir -p /Users/<username>/.openclaw/agents/main/agent

# 复制 auth-profiles.json (包含 API Keys 和 OAuth)
sudo cp ~/.openclaw/agents/main/agent/auth-profiles.json \
  /Users/<username>/.openclaw/agents/main/agent/auth-profiles.json
sudo chown <username>:staff \
  /Users/<username>/.openclaw/agents/main/agent/auth-profiles.json
```

**⚠️ 注意**: 必须复制 `auth-profiles.json`，不是 `auth.json`！

---

### 7️⃣ 配置 LaunchDaemon (10 min)

```bash
# 创建 LaunchDaemon 配置
sudo cat > /Library/LaunchDaemons/ai.openclaw.<username>.gateway.plist << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.<username>.gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/openclaw</string>
        <string>gateway</string>
        <string>--port</string>
        <string><端口号></string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/<username></string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/openclaw-<username>/openclaw.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/openclaw-<username>/openclaw.err</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>DASHSCOPE_API_KEY</key>
        <string>sk-d78d39b07b46464c82f0ac50904239e1</string>
    </dict>
    <key>UserName</key>
    <string><username></string>
</dict>
</plist>
PLIST

# 设置权限
sudo chown root:wheel /Library/LaunchDaemons/ai.openclaw.<username>.gateway.plist
sudo chmod 644 /Library/LaunchDaemons/ai.openclaw.<username>.gateway.plist

# 加载并启动
sudo launchctl bootstrap system /Library/LaunchDaemons/ai.openclaw.<username>.gateway.plist
```

**✅ 验证**:
```bash
sudo launchctl list | grep <username>
ps aux | grep "openclaw.*<端口>" | grep -v grep
```

---

### 8️⃣ Telegram 配对 (5 min)

```bash
# 等待系统消息显示配对码
# 或在日志中查找
tail -20 /tmp/openclaw-<username>/openclaw.log

# 执行批准命令
openclaw pairing approve telegram <CODE>
```

---

### 9️⃣ 最终验证 (5 min)

| 检查项 | 命令 | 预期结果 |
|-------|------|---------|
| 进程运行 | `ps aux \| grep "openclaw.*<端口>"` | 有进程 |
| 端口监听 | `lsof -i :<端口>` | LISTEN 状态 |
| 日志正常 | `tail -20 /tmp/openclaw-<username>/openclaw.log` | 无 ERROR |
| Telegram 响应 | 向 Bot 发送 `/start` | Bot 回复 |
| 模型可用 | 发送测试问题 | 正常回答 |

---

## ⚠️ 常见陷阱

| 问题 | 症状 | 解决方案 |
|------|------|---------|
| brew 权限 | "not writable" | `sudo chown -R <user> /opt/homebrew` |
| npm 权限 | EACCES 错误 | `sudo chown -R <user> /opt/homebrew/lib/node_modules` |
| LaunchAgent 失败 | "Domain does not support" | 改用 LaunchDaemon |
| Auth 配置错误 | "No API key found" | 复制 `auth-profiles.json` |
| Telegram 无响应 | Bot 不回复 | 检查 Token、配对状态 |

---

## 📁 极简模式 (已有用户)

如果 macOS 用户已存在，只需 10 min 完成基础配置：

```bash
# 阅读并执行极简 SOP
cat docs/sop-l2-minimal-setup.md
```

**极简模式配置内容**:
- ✅ AGENTS.md (工作原则)
- ✅ TOOLS.md (工具说明)
- ✅ models.json (模型配置)
- ✅ .env (环境变量)
- ✅ sessions/ credentials/ browser/ logs/ (能力目录)

**不配置**:
- ❌ MEMORY.md (在使用中建立)
- ❌ USER.md (在互动中形成)
- ❌ cron/ devices/ (按需扩展)

---

## 📚 相关文档

| 文档 | 用途 |
|------|------|
| `sop-l2-minimal-setup.md` | 极简配置 SOP (10 min) |
| `sop-l2-agent-deployment.md` | 详细步骤 + 踩坑记录 |
| `retro-shuaishuai-l2.md` | 实战复盘报告 |
| `SUMMARY-shuaishuai-l2.md` | 成果总结 |
| `README-deployment.md` | 文档索引 |

---

## ✅ 交付清单

部署完成后确认：

- [ ] 用户创建成功 (UID 正确)
- [ ] Gateway 运行中 (端口监听)
- [ ] Telegram Bot 可对话
- [ ] 模型测试通过
- [ ] LaunchDaemon 已加载
- [ ] 文档已更新 (spec.md + SHARED_REGISTRY.md)

---

*文档路径：`~/Documents/claw-outputs/projects/agent-platform/docs/QUICKSTART-L2.md`*
*最后更新：2026-02-27 18:50*
