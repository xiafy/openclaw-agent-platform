# L2 Agent 部署标准作业程序 (SOP)

> **版本**: v1.0
> **创建日期**: 2026-02-27
> **适用范围**: 在 macOS 上创建新的 L2 级别隔离 Agent (独立用户)
> **预计耗时**: 90 分钟 (首次), 60 分钟 (熟练后)

---

## 📋 部署前检查清单

### 前置条件
- [ ] macOS 管理员 sudo 权限可用
- [ ] Telegram Bot Token 已创建 (@BotFather)
- [ ] 共享层 `/Users/Shared/openclaw-common/` 已存在
- [ ] 主用户 (xiafybot) 的 OpenClaw 正常运行
- [ ] 目标端口未被占用 (默认 19002, 19003...)

### 信息记录表
| 项目 | 值 | 备注 |
|------|-----|------|
| Agent 名称 | | 如：shuaishuai, wifey, researcher |
| 角色描述 | | 如：个人生活助理 |
| Telegram Bot Token | | 从 @BotFather 获取 |
| Bot Username | | 如：@shuaishuai1989_bot |
| 分配端口 | | 从 19002 开始递增 |
| 分配 UID | | 从 502 开始递增 |
| 创建日期 | | |

---

## 🚀 部署流程

### Step 1: 创建 macOS 用户 (5 min)

```bash
# 检查 UID 是否被占用
dscl . -list /Users UniqueID | grep <目标 UID>

# 创建用户
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

### Step 2: 安装 NodeJS + OpenClaw (15 min)

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

### Step 3: 配置 openclaw.json (10 min)

```bash
# 复制模板
cp ~/.openclaw/openclaw.json /Users/<username>/.openclaw/openclaw.json
sudo chown <username>:staff /Users/<username>/.openclaw/openclaw.json

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

### Step 4: 配置共享层 symlink (10 min)

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

### Step 5: 创建人设文件 (5 min)

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

### Step 6: 复制 Auth 配置 ⭐ 关键 (5 min)

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

### Step 7: 配置 LaunchDaemon (10 min)

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

### Step 8: Telegram 配对 (5 min)

```bash
# 等待系统消息显示配对码
# 或在日志中查找
tail -20 /tmp/openclaw-<username>/openclaw.log

# 执行批准命令
openclaw pairing approve telegram <CODE>
```

---

### Step 9: 最终验证 (5 min)

| 检查项 | 命令 | 预期结果 |
|-------|------|---------|
| 进程运行 | `ps aux \| grep "openclaw.*<端口>"` | 有进程 |
| 端口监听 | `lsof -i :<端口>` | LISTEN 状态 |
| 日志正常 | `tail -20 /tmp/openclaw-<username>/openclaw.log` | 无 ERROR |
| Telegram 响应 | 向 Bot 发送 `/start` | Bot 回复 |
| 模型可用 | 发送测试问题 | 正常回答 |

---

## 🔧 故障排查

### 问题 1: brew 权限不足
**症状**: `brew install` 报错 "not writable"
**解决**: `sudo chown -R <username> /opt/homebrew`

### 问题 2: npm 安装失败
**症状**: `npm install -g` 报错 EACCES
**解决**: `sudo chown -R <username> /opt/homebrew/lib/node_modules` 或加 `--force`

### 问题 3: LaunchDaemon 启动失败
**症状**: `launchctl bootstrap` 报错
**解决**: 
1. 检查 plist 语法：`plutil -lint /Library/LaunchDaemons/ai.openclaw.<username>.gateway.plist`
2. 查看系统日志：`log show --predicate 'process == "launchd"' --last 5m`

### 问题 4: 模型不可用
**症状**: "No API key found for provider"
**解决**: 确认已复制 `auth-profiles.json`

### 问题 5: Telegram 无响应
**症状**: Bot 不回复
**解决**: 
1. 检查 Bot Token 是否正确
2. 检查是否已配对：`openclaw pairing list`
3. 查看日志中的 telegram 相关错误

---

## 📁 交付清单

部署完成后，确认以下项目：

- [ ] macOS 用户已创建 (UID 正确)
- [ ] NodeJS + OpenClaw 已安装
- [ ] openclaw.json 配置正确 (端口、Token)
- [ ] 共享层 symlink 已配置
- [ ] IDENTITY.md / SOUL.md 已创建
- [ ] auth-profiles.json 已复制
- [ ] LaunchDaemon 已加载
- [ ] Gateway 进程运行中
- [ ] Telegram Bot 可对话
- [ ] 模型测试通过
- [ ] 文档已更新 (spec.md + SHARED_REGISTRY.md)

---

## 📚 参考文档

- 主架构文档：`~/Documents/claw-outputs/projects/agent-platform/docs/spec.md`
- 复盘报告：`~/Documents/claw-outputs/projects/agent-platform/docs/retro-shuaishuai-l2.md`
- 共享层注册表：`/Users/Shared/openclaw-common/SHARED_REGISTRY.md`

---

*文档路径：`~/Documents/claw-outputs/projects/agent-platform/docs/sop-l2-agent-deployment.md`*
