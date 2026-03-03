# Heartbeat 方案设计

> **版本**: v1.0
> **日期**: 2026-02-28
> **设计来源**: 
> - Nat/Felix 心跳模式（活跃项目追踪 + session 自动重启）
> - Erik "Git-as-State-Bus"（push history = 进度）
> - Spec-Driven Testing（规则覆盖率 = 进度度量）
> - Rule-Aware Git（结构化 commit = 可追踪状态）
> - OpenClaw 官方文档（heartbeat vs cron 最佳实践）

---

## 1. 设计原则

### 1.1 心跳 vs Cron 的分工

根据 OpenClaw 官方指南，两者有明确的分工边界：

| 维度 | 心跳 | Cron |
|------|------|------|
| 会话 | 主会话（有上下文） | 隔离会话（无上下文） |
| 定时 | 每 N 分钟漂移 | 精确 cron 表达式 |
| 适合 | 轻量检查、批量巡检、上下文感知 | 精确定时、重任务、需要不同模型 |
| 成本 | 低（一次轮次检查多项） | 高（每个 job 一次完整轮次） |

**当前问题**：我们有 10 个 cron job，但心跳完全空置。很多轻量检查（session 状态、项目健康）被打散在 cron 里或者根本没有。

### 1.2 Nat/Felix 的核心启发

Felix 的心跳模式极其高效：
1. Daily note 记录活跃项目 + 对应 session
2. 心跳读 daily note → 发现未完成项目 → 检查 session
3. Session 挂了 → 静默重启（不打扰人类）
4. Session 完成 → 通知人类

**关键洞见**：心跳不是"检查任务清单"，而是**"维护 Agent 的自主运转能力"**。

### 1.3 "去瓶颈"原则

每次心跳发现需要人类介入的事情 → 问自己：**能否自动化解决？**
- 能 → 自动处理 + 记录到 daily note
- 不能 → 通知人类 + 记录为瓶颈

---

## 2. 架构：三级心跳

```
┌─────────────────────────────────────────────────────────────┐
│  Level 1: 基础设施守护（每次心跳必跑）                        │
│  Gateway 健康 / Cron 异常检测 / 磁盘空间 / 进程存活           │
│  → 异常自动修复，修复失败才告警                               │
├─────────────────────────────────────────────────────────────┤
│  Level 2: 活跃任务追踪（有活跃任务时跑）                      │
│  子 Agent session 状态 / Code Fleet worker 状态              │
│  → 挂了自动重启，完成了通知夏总                               │
├─────────────────────────────────────────────────────────────┤
│  Level 3: 项目进度感知（工作时间跑）                          │
│  Git 规则覆盖率变化 / 待办项超时 / 阻塞项检测                 │
│  → 进度异常主动预警                                          │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 Level 1: 基础设施守护

**每次心跳必跑**，确保 Claw 自身运转正常。

| 检查项 | 怎么查 | 自动修复 | 告警条件 |
|--------|--------|---------|---------|
| Gateway 进程存活 | `openclaw health` | 无（不触碰 Gateway，Protocol C） | health 返回异常 |
| Cron 连续失败 | 读 `cron/jobs.json` 中 `consecutiveErrors` | 无 | 任何 job ≥ 3 次连续失败 |
| 磁盘空间 | `df -h /` | 无 | 可用 < 10GB |
| workspace git 状态 | `git status --short` | `git stash` 清理冲突 | 未提交变更 > 50 个文件 |

**处理逻辑**：
- 全部正常 → 不输出，进入 Level 2
- 有问题但能自修复 → 修复 + 记录到 daily note
- 有问题且不能自修复 → 告警文本（不含 HEARTBEAT_OK）

### 2.2 Level 2: 活跃任务追踪

**只有当 daily note 中存在活跃任务时才运行。**

这是 Nat/Felix 模式的核心，也是最大价值所在。

#### 状态文件：`memory/active-tasks.json`

```json
{
  "tasks": [
    {
      "id": "task-001",
      "description": "Code Fleet 试点: order 模块",
      "type": "code-fleet",
      "started_at": "2026-02-28T01:00:00+08:00",
      "sessions": [
        {"label": "worker-a", "sessionKey": "spawn:abc123", "status": "running"},
        {"label": "worker-b", "sessionKey": "spawn:def456", "status": "running"}
      ],
      "git_repo": "~/Documents/claw-outputs/projects/order-module",
      "rule_table": "docs/rule-table.md",
      "notify_on_complete": true,
      "auto_restart": true,
      "max_restarts": 3,
      "restart_count": 0
    }
  ]
}
```

**心跳检查逻辑**：

```
对每个活跃任务:
  ├── 检查关联 session 状态（sessions_list）
  │   ├── 仍在运行 → 跳过（一切正常）
  │   ├── 已完成 → 
  │   │   ├── 标记任务完成
  │   │   ├── 如果 notify_on_complete → 通知夏总
  │   │   └── 清理 active-tasks.json
  │   └── 已死亡/超时 → 
  │       ├── restart_count < max_restarts → 自动重启（不通知）
  │       ├── restart_count >= max_restarts → 标记失败 + 告警
  │       └── 记录到 daily note
  │
  ├── 检查 Git 进度（如果有 git_repo + rule_table）
  │   ├── 运行 rule-coverage → 获取规则覆盖率
  │   └── 与上次心跳对比：有进展 → 记录 / 无进展超 2h → 可能卡住
  │
  └── 检查超时
      └── 运行超过预期时间 → 记录 + 可能告警
```

#### 任务注册与清理

**注册**：当 Claw 启动子 Agent（`sessions_spawn`）或 Code Fleet worker 时，自动写入 `active-tasks.json`。

**清理**：任务完成/失败后从 `active-tasks.json` 移除，完整记录写入 daily note。

### 2.3 Level 3: 项目进度感知

**仅在工作时间运行（08:00-22:00）**，避免夜间无意义检查。

| 检查项 | 逻辑 | 产出 |
|--------|------|------|
| 规则覆盖率变化 | 对活跃项目运行 `rule-coverage` | 记录到 daily note |
| 待办项超时 | 扫描 daily note 中标记为 `[ ]` 的项，检查创建时间 | 超 48h 未完成 → 提醒 |
| 阻塞项 | 扫描 daily note 中含"等夏总"/"blocked"/"待确认"的项 | 聚合后提醒夏总 |
| 瓶颈识别 | 统计本周心跳中人类被打断的次数和原因 | 周报中输出瓶颈清单 |

---

## 3. 与现有 Cron 的关系

### 3.1 保持不变的 Cron

这些任务需要精确定时、隔离会话、重模型，不适合心跳：

| Job | 时间 | 理由 |
|-----|------|------|
| CEO 每日简报 | 09:00 | 精确定时 + Opus + 重任务 |
| 行业日报 | 11:00 | 精确定时 + 独立任务 |
| 会议纪要扫描 | 07:00 | 需要浏览器 + 独立任务 |
| 每日备份 | 02:00 | 独立 + 不需要上下文 |
| 深度研究 | 14:00 | Opus + 重任务 |
| 周度复盘 | 周日 20:00 | 精确定时 + 重任务 |
| 能力进化审计 | 21:00 | 独立审计 |
| 自我进化发现 | 07:00 | 独立学习任务 |
| Codex 对比测评 | 周日 10:00 | 重任务 |
| 实验观测上报 | 隔天 20:00 | 独立轻量 |

### 3.2 从 Cron 迁移到心跳的候选

| 当前 Cron | 迁移理由 | 心跳中怎么做 |
|-----------|---------|-------------|
| Daily Retro (12:00, 23:00) | 连续失败 3 次；本质是主会话上下文感知的检查 | Level 2 的任务完成检测 + Level 3 的进度感知可以覆盖其核心功能 |

**建议**：Daily Retro 保留 cron 但修复其连续失败的 bug，心跳不替代它，而是补充它缺失的**实时性**（cron 一天只跑 2 次，心跳每 30 分钟一次）。

---

## 4. 配置方案

### 4.1 OpenClaw 配置

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last",
        activeHours: { start: "08:00", end: "24:00" },
        // 夜间不跑心跳，节省成本
      }
    }
  }
}
```

### 4.2 HEARTBEAT.md

```markdown
# Heartbeat Checklist

## Level 1: 基础设施守护（每次必跑）
- 运行 `openclaw health`，异常则告警
- 读取 cron/jobs.json，检查 consecutiveErrors >= 3 的 job，列出名称和错误
- 检查磁盘空间 `df -h /`，可用 < 10GB 则告警

## Level 2: 活跃任务追踪（有任务时跑）
- 读取 `memory/active-tasks.json`，如果不存在或为空则跳过本级
- 对每个活跃任务：
  - 用 `sessions_list` 检查关联 session 是否存活
  - 已完成 → 通知夏总 + 从 active-tasks.json 移除 + 记录到 daily note
  - 已死亡 → 如果 restart_count < max_restarts，用 sessions_spawn 重启（相同参数），更新 restart_count，不通知
  - 已死亡且超过重启上限 → 告警
  - 仍在运行 → 如果有 git_repo，运行 `scripts/rule-coverage` 记录进度

## Level 3: 项目进度感知（08:00-22:00 跑）
- 如果当前时间在 22:00-08:00，跳过本级
- 扫描今日 daily note (memory/YYYY-MM-DD.md)：
  - 含 "blocked" / "等夏总" / "待确认" 的行 → 聚合为阻塞提醒
  - 超过 48h 未完成的 [ ] 待办 → 提醒
- 如无异常，不输出

## 全局规则
- 所有自动修复操作必须记录到 daily note
- 能自动处理的不通知夏总（去瓶颈原则）
- 如果所有级别都无异常 → 回复 HEARTBEAT_OK
```

### 4.3 active-tasks.json 初始状态

```json
{
  "version": 1,
  "tasks": []
}
```

---

## 5. 任务注册流程（关键集成点）

当 Claw 启动长时间运行的工作时，必须注册到 active-tasks.json：

### 5.1 触发时机

| 场景 | 注册方式 |
|------|---------|
| `sessions_spawn` 启动子 Agent | 写入 task + session 信息 |
| Code Fleet 启动 worker | 写入 task + session + git_repo + rule_table |
| 手动标记 | 夏总说"跟踪这个任务"→ Claw 手动注册 |

### 5.2 注册示例

```python
# Claw 在 spawn 子 Agent 后自动执行：
task = {
    "id": f"task-{timestamp}",
    "description": "实现 order 模块满减逻辑",
    "type": "spawn",
    "started_at": now_iso(),
    "sessions": [{"label": label, "sessionKey": key, "status": "running"}],
    "notify_on_complete": True,
    "auto_restart": True,
    "max_restarts": 3,
    "restart_count": 0
}
# 追加到 active-tasks.json
```

### 5.3 与 Rule-Aware Git 的集成

如果任务关联了 `git_repo` 和 `rule_table`，心跳会自动运行 `rule-coverage`，获取规则覆盖率作为进度度量。

```
心跳 → 发现活跃 Code Fleet 任务
  → cd git_repo && scripts/rule-coverage -r rule_table
  → 输出: "order 模块: 3/6 规则已实现 (50%), +1 since last check"
  → 写入 daily note
```

**人类不需要主动问进度——心跳自动追踪并记录。**

---

## 6. 通知策略

| 事件 | 通知？ | 渠道 | 说明 |
|------|:---:|------|------|
| 基础设施异常（自修复成功）| ❌ | — | 记录到 daily note |
| 基础设施异常（自修复失败）| ✅ | 飞书 | 立即告警 |
| Cron 连续失败 ≥ 3 | ✅ | 飞书 | 告警 + 失败原因 |
| 子 Agent 完成 | ✅ | 飞书 | 通知 + 成果摘要 |
| 子 Agent 死亡（自动重启）| ❌ | — | 记录到 daily note |
| 子 Agent 死亡（超过重启上限）| ✅ | 飞书 | 告警 |
| 规则覆盖率有进展 | ❌ | — | 记录到 daily note |
| 规则覆盖率 2h 无进展 | ❌ | — | 记录到 daily note（不打扰） |
| 阻塞项聚合提醒 | ✅ | 飞书 | 每天最多 1 次（聚合） |
| 全部正常 | ❌ | — | HEARTBEAT_OK |

**核心原则**：**能自己处理的绝不通知，必须通知的绝不遗漏。**

---

## 7. 成本估算

| 组件 | 频率 | 模型 | 预估 token/次 |
|------|------|------|-------------|
| 心跳（无活跃任务）| 30min | Sonnet | ~500（读 HEARTBEAT.md + 几个命令 + HEARTBEAT_OK） |
| 心跳（有活跃任务）| 30min | Sonnet | ~2000（额外的 session 检查 + rule-coverage） |
| 心跳（有阻塞提醒）| 30min | Sonnet | ~1500（扫描 daily note + 生成提醒） |

**日成本估算**（08:00-24:00 = 32 次心跳）：
- 无活跃任务：~16K tokens/天 ≈ $0.05
- 有活跃任务：~64K tokens/天 ≈ $0.20

**远低于当前 cron 成本**（10 个 cron job/天，每个几十万 token）。

---

## 8. 落地步骤

| Step | 做什么 | 产出 |
|------|--------|------|
| 1 | 创建 `memory/active-tasks.json`（空） | 状态文件 |
| 2 | 写入 HEARTBEAT.md | 心跳检查清单 |
| 3 | 配置 openclaw.json 启用心跳 | 30m + activeHours |
| 4 | 测试一轮心跳（手动触发） | 验证 Level 1 正常工作 |
| 5 | 在下次 spawn 子 Agent 时注册 active-tasks | 验证 Level 2 |
| 6 | Code Fleet 试点时验证 rule-coverage 集成 | 验证 Level 3 |

---

## 9. 风险与缓解

| 风险 | 缓解 |
|------|------|
| 心跳 prompt 过长导致 token 浪费 | HEARTBEAT.md 保持精简，用"跳过本级"逻辑减少无效检查 |
| 自动重启 loop（session 反复崩溃）| max_restarts = 3 硬限 |
| 心跳干扰主会话上下文 | 心跳输出尽量短，HEARTBEAT_OK 自动丢弃 |
| active-tasks.json 状态不一致 | 心跳每次都从 sessions_list 获取真实状态，不信任本地缓存 |
| Protocol C 冲突（远程时不碰 Gateway）| Level 1 只读检查 health，不做 restart/重启 |

---

*本文档定义 Claw 的心跳方案。随实践迭代更新。*
