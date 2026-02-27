# Shuaishuai Agent (L2) 搭建计划

> **版本**: v1.1 - 已审核
> **创建时间**: 2026-02-27
> **更新时间**: 2026-02-27
> **目标**: 在 macOS 上创建独立用户 `shuaishuai`，部署 L2 级别隔离的个人生活助理 Agent

---

## 一、前置条件

| 项目 | 状态 | 负责人 |
|------|------|--------|
| Telegram Bot Token | ✅ 已提供 | 夏总 |
| macOS 管理员 sudo 权限 | ✅ 可用 | 夏总 |
| 共享层 `/Users/Shared/openclaw-common/` | ✅ 已存在 | Claw |

---

## 二、整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     macOS (xiafybot 用户)                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Claw Gateway (L1) - 端口 18789                      │    │
│  │  Config: ~/.openclaw/                                │    │
│  │  Workspace: ~/.openclaw/workspace/                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ OS 权限隔离
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     macOS (life 用户 - 新建)                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Life Gateway (L2) - 端口 19002                      │    │
│  │  Config: ~/.openclaw/                                │    │
│  │  Workspace: ~/.openclaw/workspace/                   │    │
│  │  Skills → symlink → /Users/Shared/openclaw-common/   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、执行步骤

### Phase 1: 准备工作（夏总）

| 步骤 | 操作 | 预计时间 |
|------|------|----------|
| 1.1 | Telegram @BotFather 创建新 Bot | 5 min |
| 1.2 | 记录 Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`） | - |
| 1.3 | 将 Token 通过安全渠道发给 Claw | - |

**Bot 信息**：
- Bot Token: `8343182214:AAGEK-hZ7-0aBDfd9sCJkhJaBh1tjKc4Fr4`
- Bot Username: 待确认（@BotFather 创建时设置）

---

### Phase 2: 创建 macOS 用户（Claw 执行，需 sudo）

| 步骤 | 命令/操作 | 说明 |
|------|-----------|------|
| 2.1 | `sudo dscl . -create /Users/life` | 创建用户 |
| 2.2 | `sudo dscl . -create /Users/life UserShell /bin/zsh` | 设置 Shell |
| 2.3 | `sudo dscl . -create /Users/life RealName "Life Agent"` | 全名 |
| 2.4 | `sudo dscl . -create /Users/shuaishuai UniqueID "502"` | UID（501=xiafybot，502=shuaishuai） |
| 2.5 | `sudo dscl . -create /Users/life PrimaryGroupID 20` | 设置组 |
| 2.6 | `sudo dscl . -create /Users/life NFSHomeDirectory /Users/life` | 家目录 |
| 2.7 | `sudo createhomedir -c -u life` | 创建家目录 |
| 2.8 | `sudo dscl . -append /Groups/com.apple.access_ssh GroupMembership life` | 可选：允许 SSH |

**风险说明**：
- UID 冲突风险：需确保 503 未被占用
- 创建后需验证用户可登录

---

### Phase 3: 配置 life 用户的 OpenClaw 环境（Claw 执行）

| 步骤 | 操作 | 说明 |
|------|------|------|
| 3.1 | `sudo su - life` 切换到 life 用户 | - |
| 3.2 | 安装 NodeJS（如未安装） | `brew install node@20` |
| 3.3 | 安装 OpenClaw | `npm install -g openclaw` |
| 3.4 | 初始化配置 | `openclaw init` |
| 3.5 | 配置 Telegram Bot Token | 编辑 `~/.openclaw/openclaw.json` |
| 3.6 | 配置端口 19002 | 避免与 claw(18789)/sage(19001) 冲突 |
| 3.7 | 配置模型别名 | 同步 claw 的模型配置 |
| 3.8 | 配置 IDENTITY.md / SOUL.md | 定义 life Agent 人设 |

---

### Phase 4: 配置共享层 symlink（Claw 执行）

| 步骤 | 操作 | 说明 |
|------|------|------|
| 4.1 | `sudo su - life` | 切换到 life 用户 |
| 4.2 | `ln -s /Users/Shared/openclaw-common/skills/summarize ~/.openclaw/workspace/skills/summarize` | Skills |
| 4.3 | `ln -s /Users/Shared/openclaw-common/skills/meeting-notes ~/.openclaw/workspace/skills/meeting-notes` | - |
| 4.4 | `ln -s /Users/Shared/openclaw-common/skills/domain-model-extract ~/.openclaw/workspace/skills/domain-model-extract` | - |
| 4.5 | `ln -s /Users/Shared/openclaw-common/protocols ~/.openclaw/workspace/protocols` | 协议 |
| 4.6 | `ln -s /Users/Shared/openclaw-common/knowledge ~/.openclaw/workspace/knowledge` | 知识 |
| 4.7 | 更新 `SHARED_REGISTRY.md` | 记录 life Agent 同步状态 |

**权限问题**：
- 需确保 life 用户对 `/Users/Shared/openclaw-common/` 有读权限
- `sudo chmod -R 755 /Users/Shared/openclaw-common/`

---

### Phase 5: 启动 Gateway（Claw 执行）

| 步骤 | 操作 | 说明 |
|------|------|------|
| 5.1 | `sudo su - life -c "openclaw gateway start"` | 以 life 用户启动 |
| 5.2 | 验证端口 19002 监听 | `lsof -i :19002` |
| 5.3 | 验证 Telegram 连接 | 发送 `/start` 测试 |

---

### Phase 6: 验证与交付（Claw + 夏总）

| 步骤 | 操作 | 验收标准 |
|------|------|----------|
| 6.1 | 向 life Bot 发送 `/start` | Bot 回复正常 |
| 6.2 | 发送测试问题 | 能正常回答 |
| 6.3 | 验证文件隔离 | life 用户无法访问 xiafybot 的 `~` 目录 |
| 6.4 | 验证共享层 | life 能读取 `/Users/Shared/openclaw-common/` |
| 6.5 | 验证记忆隔离 | life 的 MEMORY.md 独立 |

---

## 四、风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| UID 冲突 | 低 | 中 | 先检查 `dscl . -list /Users UniqueID` |
| 共享层权限不足 | 中 | 高 | 提前设置 `chmod 755` |
| Bot Token 泄露 | 低 | 高 | 仅通过加密渠道传输，不存聊天记录 |
| Gateway 端口冲突 | 低 | 中 | 启动前检查 `lsof -i :19002` |
| NodeJS 版本不一致 | 中 | 低 | 统一使用 Node 20+ |
| life 用户无法启动 GUI 应用 | - | - | L2 用户本就不需要 GUI，正常 |

---

## 五、预计时间

| Phase | 预计时间 |
|-------|----------|
| Phase 1: 准备工作 | 10 min（夏总） |
| Phase 2: 创建用户 | 5 min |
| Phase 3: 配置环境 | 15 min |
| Phase 4: 共享层 | 10 min |
| Phase 5: 启动 | 5 min |
| Phase 6: 验证 | 10 min |
| **总计** | **约 55 min** |

---

## 六、交付物

1. ✅ 独立 macOS 用户 `life`（UID 503）
2. ✅ Life Gateway 运行在端口 19002
3. ✅ Telegram Bot 可对话
4. ✅ 共享层 symlink 配置完成
5. ✅ `SHARED_REGISTRY.md` 更新
6. ✅ Life Agent 专属 IDENTITY.md / SOUL.md

---

## 七、后续待办（不在此次范围内）

| 项目 | 说明 |
|------|------|
| Life Agent 人设细化 | 定义 life Agent 的具体职责边界 |
| 跨 Agent 通信 | life ↔ claw 的协作机制 |
| wifey Agent | 类似的 L2 搭建 |
| Claw 迁移到 L2 | 将 claw 也迁移到独立用户（P3） |

---

*文档路径：`~/Documents/claw-outputs/projects/agent-platform/docs/life-agent-plan.md`*
