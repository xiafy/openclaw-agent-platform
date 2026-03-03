# L1 Agent 部署 SOP

> **版本**: v1.0
> **日期**: 2026-03-03
> **来源**: Beacon 部署实战 + 事故复盘
> **耗时**: 自动化 5 min / 手动 15 min

---

## 前置条件

- [ ] OpenClaw 已安装 (`which openclaw`)
- [ ] 共享层已就绪 (`/Users/Shared/openclaw-common/`)
- [ ] Telegram Bot Token 已从 @BotFather 获取
- [ ] Claw Gateway 正常运行 (`openclaw gateway status`)

---

## 方式一：自动化部署（推荐）

```bash
cd ~/Documents/claw-outputs/projects/agent-platform

# 预演（不实际执行，确认步骤）
python3 deploy/bin/deploy-agent --mode l1 --name <agent名> --role "<角色描述>" --dry-run

# 正式部署
python3 deploy/bin/deploy-agent --mode l1 --name <agent名> --role "<角色描述>" --bot-token "<token>"

# 验证
python3 deploy/bin/deploy-agent --verify --name <agent名>
```

**脚本自动完成的 9 个步骤**：
1. 检查前置条件（OpenClaw、共享层、Profile 不重复）
2. 分配端口（从 ports.yaml 读取 next_available）
3. 创建目录（`~/.openclaw-<name>/` + `~/.openclaw/workspace-<name>/`）
4. 生成 openclaw.json（从模板，含完整模型配置）
5. 复制 auth-profiles.json（从 Claw）
6. 配置共享层 symlink（skills + protocols + knowledge）
7. 创建独立 browser profile（`<name>-browser`，自动分配 CDP 端口）
8. 创建 LaunchAgent 并启动（`ai.openclaw.gateway.<name>.plist`）
9. 验证（HTTP probe 端口响应）

---

## 方式二：手动部署

当脚本不可用或需要自定义配置时使用。

### Step 1: 创建目录 (1 min)

```bash
AGENT=<agent名>
mkdir -p ~/.openclaw-${AGENT}/logs
mkdir -p ~/.openclaw/workspace-${AGENT}/{memory,docs,skills}
```

### Step 2: 生成 openclaw.json (3 min)

从现有 Agent（如 Sage）复制配置，修改以下字段：

```bash
cp ~/.openclaw-sage/openclaw.json ~/.openclaw-${AGENT}/openclaw.json
```

**必须修改的字段**：

| 字段 | 说明 |
|------|------|
| `agents.defaults.workspace` | → `~/.openclaw/workspace-${AGENT}` |
| `gateway.port` | → 新端口（查 ports.yaml 获取 next_available） |
| `gateway.auth.token` | → 新随机 token（`python3 -c "import secrets; print(secrets.token_hex(24))"`) |
| `channels.telegram.accounts.default.botToken` | → 新 Bot Token |
| `browser.defaultProfile` | → `${AGENT}-browser` |

**不要改的字段**：模型配置、API Key、别名——直接继承。

### Step 3: 复制 auth-profiles.json (1 min)

```bash
mkdir -p ~/.openclaw-${AGENT}/agents/main/agent/
cp ~/.openclaw/agents/main/agent/auth-profiles.json ~/.openclaw-${AGENT}/agents/main/agent/
```

### Step 4: 写入 Workspace 核心文件 (3 min)

必须创建：
- `SOUL.md` — Agent 人设和职责
- `IDENTITY.md` — 身份信息
- `AGENTS.md` — 工作原则和能力清单
- `USER.md` — 夏总画像（精简版）
- `MEMORY.md` — 空文件（使用中积累）

### Step 5: 配置共享层 symlink (1 min)

```bash
WS=~/.openclaw/workspace-${AGENT}
SHARED=/Users/Shared/openclaw-common

ln -sf $SHARED/skills/summarize $WS/skills/summarize
ln -sf $SHARED/skills/meeting-notes $WS/skills/meeting-notes
ln -sf $SHARED/skills/domain-model-extract $WS/skills/domain-model-extract
# protocols 和 knowledge 按需链接
```

### Step 6: 创建 Browser Profile (1 min)

```bash
openclaw --profile ${AGENT} browser create-profile --name ${AGENT}-browser
```

记录输出中的 CDP 端口号。

### Step 7: 创建 LaunchAgent 并启动 (2 min)

```bash
# 创建 plist（参照 ai.openclaw.gateway.sage.plist 模板）
cat > ~/Library/LaunchAgents/ai.openclaw.gateway.${AGENT}.plist << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Comment</key>
	<string>OpenClaw Gateway - ${AGENT} profile</string>
	<key>EnvironmentVariables</key>
	<dict>
		<key>HOME</key>
		<string>$(echo $HOME)</string>
		<key>PATH</key>
		<string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
	</dict>
	<key>KeepAlive</key>
	<true/>
	<key>Label</key>
	<string>ai.openclaw.gateway.${AGENT}</string>
	<key>ProgramArguments</key>
	<array>
		<string>/opt/homebrew/bin/openclaw</string>
		<string>--profile</string>
		<string>${AGENT}</string>
		<string>gateway</string>
		<string>run</string>
		<string>--port</string>
		<string><端口号></string>
	</array>
	<key>RunAtLoad</key>
	<true/>
	<key>StandardErrorPath</key>
	<string>$(echo $HOME)/.openclaw-${AGENT}/logs/gateway.err.log</string>
	<key>StandardOutPath</key>
	<string>$(echo $HOME)/.openclaw-${AGENT}/logs/gateway.log</string>
</dict>
</plist>
PLIST

# 启动
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.${AGENT}.plist
```

### Step 8: 验证 (1 min)

```bash
# 检查 LaunchAgent 状态（退出码应为 0）
launchctl list | grep ${AGENT}

# 检查端口响应
curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:<端口>/

# Telegram 测试
# 给 Bot 发 /start，完成配对
```

### Step 9: 更新 ports.yaml (1 min)

```bash
# 编辑 deploy/config/ports.yaml，添加新 Agent 记录
# 更新 next_available
```

---

## ⛔ 安全红线

1. **禁止操作 Claw 的 Gateway**：任何 `gateway stop/start/restart` 前，必须确认 Service file 和端口不是 18789
2. **禁止共用 browser profile**：每个 Agent 必须有独立的 browser profile，否则 CDP 端口冲突
3. **LaunchAgent unload/load 必须成对**：unload 后必须立即 load 并验证
4. **先 dry-run 后执行**：手动部署也要先列步骤确认

---

## 🔄 回滚

```bash
# 自动回滚
python3 deploy/bin/deploy-agent --rollback --name <agent名> --mode l1

# 手动回滚
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.${AGENT}.plist
rm ~/Library/LaunchAgents/ai.openclaw.gateway.${AGENT}.plist
rm -rf ~/.openclaw-${AGENT}
rm -rf ~/.openclaw/workspace-${AGENT}
# 更新 ports.yaml 移除记录
```

---

## 📋 部署检查清单

| # | 检查项 | 通过 |
|---|--------|------|
| 1 | `launchctl list \| grep <agent>` 退出码 0 | ☐ |
| 2 | `curl http://127.0.0.1:<端口>/` 返回 200 | ☐ |
| 3 | Telegram Bot 发 /start 能配对 | ☐ |
| 4 | 发消息能正常回复 | ☐ |
| 5 | browser profile 独立（`openclaw --profile <agent> browser profiles`） | ☐ |
| 6 | ports.yaml 已更新 | ☐ |
| 7 | spec.md 已更新部署状态 | ☐ |

---

## 已部署 L1 Agent

| Agent | 端口 | Browser Profile | CDP 端口 | 部署日期 |
|-------|------|----------------|----------|----------|
| claw | 18789 | openclaw | 18800 | - |
| sage | 19001 | sage-browser | 18801 | 2026-02-25 |
| beacon | 19003 | beacon-browser | 18802 | 2026-03-03 |
