# SAGE Agent 搭建详细方案

> **文档状态**: ✅ 已执行完成
> **创建时间**: 2026-02-24
> **执行完成**: 2026-02-25
> **实际耗时**: ~1.5 小时（分两天完成）

---

## 执行结果总览

| Step | 描述 | 状态 | 备注 |
|------|------|------|------|
| 1 | 创建 Profile | ✅ | `~/.openclaw-sage/` |
| 2 | 配置模型认证 | ✅ | Anthropic + Fireworks + DashScope |
| 3 | 配置 Telegram 渠道 | ✅ | @sage1989_bot |
| 4 | 配置模型 | ✅ | 默认 sonnet，Gemini 已废弃 |
| 5 | 创建 Workspace 文件 | ✅ | IDENTITY/SOUL/AGENTS/USER/MEMORY/TOOLS |
| 6 | 设置共享目录 | ❌ | 未执行，待后续统一规划 |
| 7 | Gateway 端口 19001 | ✅ | |
| 8 | launchd 自启动 | ✅ | `ai.openclaw.gateway.sage.plist` |
| 9 | 启动验证 | ✅ | Gateway running, Telegram 连通 |
| 10 | 迁移 SAGE 记忆 | ⚠️ 部分 | 基础记忆已写入，完整迁移待补 |

## 与原计划的偏差

| 偏差项 | 原计划 | 实际 | 原因 |
|--------|--------|------|------|
| 默认模型 | `google/gemini-3-flash-preview` | `anthropic/claude-sonnet-4-6` | Gemini 全系列因限速废弃 |
| 共享目录 | 创建 + symlink | 未执行 | 优先级降低，单 Agent 阶段暂不需要 |
| Bot Token 轮换 | 建议 revoke 换新 | 未处理 | 待夏总操作 |
| Sage 接入飞书 | 未在原计划中 | 实际已接入飞书 | 夏总后续配置 |

## 待办

- [ ] 共享目录方案（等更多 Agent 上线后统一规划）
- [ ] Telegram Bot Token 轮换
- [ ] 完整 SAGE 记忆迁移（从 claw 的 MEMORY.md 提取）

---

*文档路径: `~/Documents/claw-outputs/projects/multi-agent-architecture/docs/plan-sage.md`*
