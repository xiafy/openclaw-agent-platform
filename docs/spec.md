# Agent Platform — OpenClaw 多层隔离架构方案

> **文档状态**: v14 - 职责分离重构
> **创建时间**: 2026-02-24
> **最后更新**: 2026-03-13
> **运维数据**: 端口/阵容/事故/检查清单 → `claw-memory/memory/kb/multi-agent-ops.md`（唯一真相）
> **配套文档**:
> - L1 部署 SOP: `sop-l1-agent-deployment.md` (5-15 min)
> - L2 极简 SOP: `sop-l2-minimal-setup.md` (10 min)
> - L2 完整 SOP: `sop-l2-agent-deployment.md` (90 min)
> - 自动化工具: `deploy-automation-guide.md`

---

## 一、需求总结

| 需求 | 说明 |
|------|------|
| 角色独立 | 多个 Agent 扮演不同角色，处理不同类型工作 |
| 记忆隔离 | 各 Agent 的对话历史、记忆文件互不可见 |
| 文件隔离 | Agent 无法读写其他 Agent 的 workspace |
| 共享能力 | 可选共享 Skills、知识库、API Key |
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

## 三、当前部署状态

> 最新阵容、端口、浏览器隔离详情见 `multi-agent-ops.md`。以下仅列概要。

| Agent | 角色 | 级别 | 状态 |
|-------|------|------|------|
| claw | 🦀 CEO 助手 | L1 | ✅ |
| sage | 🧪 SAGE 项目 | L1 | ✅ |
| beacon | 🔥 智库 | L1 | ✅ |
| shuaishuai | 🌟 生活助理 | L2 | ✅ |

### 模型配置（统一策略）

| 别名 | 完整模型 | 定位 |
|------|----------|------|
| `opus` | `anthropic/claude-opus-4-6` | 旗舰，深度推理 |
| `sonnet` | `anthropic/claude-sonnet-4-6` | 默认模型，日常主力 |
| `glm-5` | `fireworks/glm-5` | 轻量便宜 |
| `kimi` | `fireworks/kimi-k2p5` | 轻量便宜 |
| `qwen` | `dashscope/qwen3.5-flash` | 轻量 |
| `qwen-plus` | `dashscope/qwen3.5-plus` | 中等 |

**已废弃**: Google Gemini 全系列 — 严重限速。

---

## 四、共享知识层

> **维护者**: Claw 🦀
> **清单**: `/Users/Shared/openclaw-common/SHARED_REGISTRY.md`

### 结构

```
/Users/Shared/openclaw-common/
├── SHARED_REGISTRY.md              ← 资产总清单
├── protocols/                      ← 通用工作协议
│   ├── execution-protocol.md
│   ├── error-correction.md
│   ├── browser-strategy.md
│   └── coding-conventions.md
├── knowledge/                      ← 通用知识
│   ├── model-strategy.md
│   └── user-profile.md
└── skills/                         ← 通用技能
    ├── summarize/
    ├── meeting-notes/
    └── domain-model-extract/
```

### 分类原则

| 共享（通用） | 不共享（角色专属） |
|---|---|
| 工程方法论、工具 SOP | IDENTITY.md / SOUL.md（人设不同） |
| 夏总偏好 & 授权边界 | HEARTBEAT.md（运行时状态） |
| 通用 Skills | ceo-daily-brief / industry-daily（Claw 专属职责） |
| 行业知识、模型策略 | 各 Agent 的产品决策记忆 |

**判断标准**: 换一个全新 Agent 进来，它需不需要知道？需要 → 通用。不需要 → 专属。

### 知识治理原则（2026-03-03 夏总定调）

1. **独立演进**：每个 Agent 独自发展符合其工作场景的能力和经验
2. **提取与分发**：Claw 负责从各 Agent 实践中提炼可共用的方法论/经验/Skill，推荐（非强制）给其他 Agent
3. **自主吸收**：接收方自主判断如何吸收

**共享层定位**：可选参考库，不是强制同步源。

---

## 五、待实施

| 项目 | 优先级 | 说明 |
|------|--------|------|
| 跨 Agent 通信 | P2 | Telegram 互发方案 |
| support Agent | P2 | L1 Profile，售后服务 |
| wifey Agent | P3 | L2 独立用户 |

---

## 六、变更日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-02-24 | v1 | 初始架构设计 |
| 2026-02-25 | v6 | Claw + Sage 上线 |
| 2026-02-27 | v7-v8 | shuaishuai L2 部署，SOP v1.0 |
| 2026-03-03 | v9-v13 | Beacon 上线，知识治理原则，浏览器隔离，端口冲突修复，检查清单 |
| 2026-03-13 | v14 | **职责分离重构**：运维数据（端口/阵容/事故/检查清单）统一到 `multi-agent-ops.md`，spec.md 瘦身为架构设计文档 |

---

*文档路径: `~/Documents/claw-outputs/projects/agent-platform/docs/spec.md`*
