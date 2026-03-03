# Agent Platform — OpenClaw 多层隔离架构方案

> **文档状态**: v11 - Beacon 上线 + 部署脚本 v2.0
> **创建时间**: 2026-02-24
> **最后更新**: 2026-03-03
> **部署状态更新日期**: 2026-02-27
> **配套文档**: 
> - 文档索引：`README-deployment.md` ⭐
> - 极简 SOP: `sop-l2-minimal-setup.md` ⭐ (10 min)
> - 快速指南：`QUICKSTART-L2.md` ⭐ (90 min)
> - 完整 SOP: `sop-l2-agent-deployment.md` (90 min + 踩坑)
> - 复盘报告：`retro-shuaishuai-l2.md`
> - 最终总结：`SUMMARY-shuaishuai-l2.md` ⭐
> **目标**: 在一台 Mac mini 上运行多个互相独立的 OpenClaw Agent，支持按场景选择不同隔离级别

---

## 一、需求总结

| 需求 | 说明 |
|------|------|
| 角色独立 | 多个 Agent 扮演不同角色，处理不同类型工作 |
| 记忆隔离 | 各 Agent 的对话历史、记忆文件互不可见 |
| 文件隔离 | Agent 无法读写其他 Agent 的 workspace |
| 共享能力 | 可选共享 Skills、知识库、API Key |
| 项目协作 | 特定项目中多个 Agent 可以协作 |
| 灵活选择 | 不同场景可选择不同隔离级别 |

---

## 二、两层隔离方案

| 维度 | L1 多 Profile | L2 独立 macOS 用户 |
|------|--------------|-------------------|
| **Gateway 进程** | 各自独立 | 各自独立 |
| **Workspace / 记忆** | 目录隔离（可互访） | OS 权限隔离 |
| **文件系统隔离** | ⚠️ 目录级（可绕过） | ✅ OS 权限级 |
| **搭建复杂度** | 低 | 高 |

**一句话区别**：L1 = 君子协定，L2 = 物理隔墙。

---

## 三、实际部署状态（2026-02-27 更新）

### 已上线

| Agent | 角色 | 级别 | 端口 | 配置目录 | 渠道 | 状态 |
|-------|------|------|------|---------|------|------|
| **claw** | 🦀 CEO 助手 | L1 (默认 Profile) | 18789 | `~/.openclaw/` | 飞书 + Telegram | ✅ 运行中 |
| **sage** | 🧪 SAGE 项目 Owner | L1 (Profile: sage) | 19001 | `~/.openclaw-sage/` | Telegram | ✅ 运行中 |
| **beacon** | 🔥 智库 (研究+分析) | L1 (Profile: beacon) | 19003 | `~/.openclaw-beacon/` | Telegram | ✅ 运行中 |
| **shuaishuai** | 🌟 个人生活助理 | L2 (独立用户) | 19002 | `/Users/shuaishuai/.openclaw/` | Telegram | ✅ 运行中 (LaunchDaemon) |

### 模型配置（2026-03 统一策略）

| 别名 | 完整模型 | 定位 |
|------|----------|------|
| `opus` | `anthropic/claude-opus-4-6` | 旗舰，深度推理 |
| `sonnet` | `anthropic/claude-sonnet-4-6` | 默认模型，日常主力 |
| `glm-5` | `fireworks/glm-5` | 轻量便宜 |
| `kimi` | `fireworks/kimi-k2p5` | 轻量便宜 |
| `qwen` | `dashscope/qwen3.5-flash` | 轻量 |
| `qwen-plus` | `dashscope/qwen3.5-plus` | 中等 |

**已废弃**: Google Gemini 全系列 — 严重限速，不再使用。

两个 Gateway 已同步完整模型别名配置。

### 未完成

| 项目 | 状态 | 说明 |
|------|------|------|
| 跨 Agent 通信 | ❌ 未配置 | Telegram 互发方案未实施 |
| support Agent | ❌ 未创建 | 计划 L1 Profile |
| wifey Agent | ❌ 未创建 | 计划 L2 独立用户 |
| Sage AGENTS.md 消除重复 | P3 | 各 Agent 独立演进，不强制统一（2026-03-03 夏总定调）|

---

## 四、计划中的 Agent 阵容（完整版）

| Agent ID | 角色 | 级别 | 渠道 | 优先级 |
|----------|------|------|------|--------|
| **claw** | 🦀 CEO 助手 | L1 | 飞书 + TG | ✅ 已上线 |
| **sage** | 🧪 SAGE 项目 Owner | L1 | TG | ✅ 已上线 |
| **beacon** | 🔥 智库 (市场研究+数据分析) | L1 | TG | ✅ 已上线 |
| **researcher** | 🔍 商业研究员 | L1 | TG | P1 |
| **support** | 🎧 售后服务 Owner | L1 | TG | P2 |
| **life** | 🌴 个人生活助理 | L2 | TG | P3 |
| **wifey** | 💐 夫人助理 | L2 | 微信/TG | P3 |

---

## 五、共享知识层（已实施 ✅）

> **维护者**: Claw 🦀
> **清单**: `/Users/Shared/openclaw-common/SHARED_REGISTRY.md`
> **原则**: 通用知识单点维护，各 Agent 通过 symlink 引用；角色专属知识留各自 workspace。

### 已部署结构

```
/Users/Shared/openclaw-common/
├── SHARED_REGISTRY.md              ← 资产总清单（Claw 维护）
├── protocols/                      ← 通用工作协议
│   ├── execution-protocol.md       ← 标准执行流程（六步法）
│   ├── error-correction.md         ← 纠错验证协议
│   ├── browser-strategy.md         ← 浏览器分层策略 L0-L3
│   └── coding-conventions.md       ← 工程编码 & Git 规范
├── knowledge/                      ← 通用知识
│   ├── model-strategy.md           ← 模型分工策略
│   └── user-profile.md             ← 夏总画像 & 授权边界
└── skills/                         ← 通用技能
    ├── summarize/                  ← 内容总结与转写
    ├── meeting-notes/              ← 会议纪要整理
    └── domain-model-extract/       ← 领域模型提取
```

### 分类原则

| 共享（通用） | 不共享（角色专属） |
|---|---|
| 工程方法论、工具 SOP | IDENTITY.md / SOUL.md（人设不同） |
| 夏总偏好 & 授权边界 | HEARTBEAT.md（运行时状态） |
| 通用 Skills | ceo-daily-brief / industry-daily / work-journal（Claw 专属职责） |
| 行业知识、模型策略 | 各 Agent 的产品决策记忆 |

**判断标准**: 换一个全新 Agent 进来，它需不需要知道？需要 → 通用。不需要 → 专属。

### Beacon 同步状态

| 资产 | 同步方式 | 状态 |
|------|----------|------|
| skills/summarize | symlink | ✅ |
| skills/meeting-notes | symlink | ✅ |
| skills/domain-model-extract | symlink | ✅ |
| protocols/* | 未配置 | ❌ 待配 |
| knowledge/* | 未配置 | ❌ 待配 |

### Sage 同步状态

| 资产 | 同步方式 | 状态 |
|------|----------|------|
| skills/summarize | symlink | ✅ |
| skills/meeting-notes | symlink | ✅ |
| skills/domain-model-extract | symlink | ✅ |
| protocols/* | Sage AGENTS.md 中有手动复制的旧版 | ⚠️ 待改为引用共享层 |
| knowledge/* | Sage MEMORY.md 中有手动复制的旧版 | ⚠️ 待改为引用共享层 |

### 维护规则

1. **Claw 负责维护共享层所有内容**
2. 新增/修改共享资产后，必须更新 `SHARED_REGISTRY.md` 的版本和日期
3. 新 Agent 上线时，Claw 负责配置 symlink 并更新同步状态
4. 每周 review：是否有角色专属知识应升级为通用知识
5. 共享层文件是**只读引用**，各 Agent 不应直接修改

### 多 Agent 知识治理原则（2026-03-03 夏总定调）⭐

1. **独立演进**：每个 Agent 独自发展符合其工作场景的能力和经验，不强制同步
2. **提取与分发**：Claw 负责从各 Agent 实践中提炼可共用的方法论/经验/Skill，推荐（非强制）给其他 Agent
3. **自主吸收**：接收方自主判断如何吸收，避免新技能与原有技能冲突导致降智或失能

**共享层定位**：可选参考库，不是强制同步源。Claw 的职责是"提炼+推荐"，不是"覆盖+替换"。

---

## 六、待实施

| 项目 | 优先级 | 说明 |
|------|--------|------|
| 跨 Agent 通信 | P2 | Telegram 互发方案 |
| industry-insights.md | P2 | 从 Claw knowledge-base.md 提取通用行业知识到共享层 |
| support Agent | P2 | L1 Profile |
| wifey Agent | P3 | L2 独立用户 |
| ~~Sage AGENTS.md 消除重复~~ | P3 | 各 Agent 独立演进，不强制统一（2026-03-03 夏总定调）|
| ~~Claw 迁移到 L2~~ | 取消 | Claw 是夏总个人助理，应在 xiafybot 用户下运行 |
| ~~researcher Agent~~ | 完成 | 合并为 Beacon 智库 Agent（2026-03-03）|

---

## 八、浏览器隔离策略（2026-03-03 补充）⭐

### 事故：浏览器端口冲突导致 Claw 无头浏览器不可用

**时间**：2026-03-03 07:00 ~ 14:00（约 7 小时）
**影响**：07:00 会议纪要扫描 cron 无法使用浏览器，3/2 管理例会纪要未自动归档

**根因**：
1. Claw 和 Sage 的 `browser.cdpPort` 均未显式配置，依赖自动计算
2. 某次 gateway 重启后，Chrome 实例使用了 Claw 的 user-data 但绑定 Sage 端口（19012）
3. Claw gateway 连接默认 18800 → 超时 → 所有浏览器操作失败

**修复（三轮迭代）**：
1. 应急：杀掉冲突 Chrome 进程 → Claw 恢复
2. 误修：写入 `browser.cdpPort`（无效 key）→ Sage crash → 移除
3. 正解：给 Sage 创建独立 browser profile `sage-browser`（端口 18801 自动分配），设置 `defaultProfile`

### 多 Agent 浏览器隔离规则

| Agent | Browser Profile | CDP 端口 | User-Data 目录 | 状态 |
|-------|----------------|----------|----------------|------|
| Claw | openclaw | 18800 | `~/.openclaw/browser/openclaw/user-data` | ✅ |
| Sage | sage-browser | 18801 | `~/.openclaw/browser/sage-browser/user-data` | ✅ |
| Beacon | beacon-browser | 18802 | `~/.openclaw/browser/beacon-browser/user-data` | ✅ |

Sage 配置：`~/.openclaw-sage/openclaw.json` → `"browser": {"defaultProfile": "sage-browser"}`

**⚠️ 重要**：CDP 端口由 OpenClaw 创建 browser profile 时自动分配，**不能通过 openclaw.json 手动配置**（`browser.cdpPort` 是无效 key，会导致 gateway 启动失败！2026-03-03 实锤）。

**规则**：
1. CDP 端口由 OpenClaw 自动管理，不要手动修改
2. User-data 目录天然隔离（跟随 configDir）
3. 同一 user-data 只能有一个 Chrome 实例
4. 如遇端口冲突，杀掉错误进程让 OpenClaw 自动重新分配

### 诊断 SOP

```bash
# 1. 查运行中的 Chrome 及端口
ps aux | grep "remote-debugging-port" | grep -v grep
# 2. 确认端口可达
curl -s http://127.0.0.1:18800/json/version
# 3. 冲突时 kill 错误进程，OpenClaw 会自动重启
```


## 九、变更日志

| 日期 | 变更 | 操作人 |
|------|------|--------|
| 2026-02-24 | spec v1 创建 | Claw |
| 2026-02-25 | v6 — Claw + Sage 上线，模型配置同步 | Claw |
| 2026-02-26 | 共享知识层建立（protocols + knowledge + skills），Sage symlink 配置完成 | Claw |
| 2026-02-27 | v7 — shuaishuai (life Agent) L2 部署完成，共享层 symlink 配置，LaunchDaemon 开机自启 | Claw |
| 2026-02-27 | v8 — 复盘完成，发布 SOP v1.0，文档结构化 | Claw |
| 2026-03-03 | v11 — 多 Agent 知识治理原则（独立演进+提取分发+自主吸收），Sage 消除重复降 P3 | Claw |
| 2026-03-03 | v10 — 浏览器端口冲突事故（三轮修复），新增浏览器隔离策略，Sage 独立 profile sage-browser | Claw |

---

*文档路径: `~/Documents/claw-outputs/projects/agent-platform/docs/spec.md`*
