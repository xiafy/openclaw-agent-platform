# OpenClaw Agent Platform

> 在一台 Mac mini 上运行多个互相独立的 OpenClaw Agent

---

## 架构

两层隔离方案：
- **L1 (Profile)**: 目录隔离，同一 macOS 用户下多个 Gateway 实例
- **L2 (独立用户)**: OS 权限隔离，独立 macOS 用户

## 当前部署

| Agent | 角色 | 级别 | 端口 | 状态 |
|-------|------|------|------|------|
| claw | 🦀 CEO 助手 | L1 | 18789 | ✅ |
| sage | 🧪 SAGE 项目 | L1 | 19001 | ✅ |
| beacon | 🔥 智库 | L1 | 19010 | ✅ |
| shuaishuai | 🌟 生活助理 | L2 | 19002 | ✅ |

## 部署新 Agent

```bash
# L1 自动部署（推荐）
python3 deploy/bin/deploy-agent --mode l1 --name <名称> --role "<角色>" --bot-token "<token>"

# L2 自动部署
python3 deploy/bin/deploy-agent --mode l2 --username <用户名> --role "<角色>"

# 预演（不实际执行）
python3 deploy/bin/deploy-agent --mode l1 --name <名称> --dry-run

# 查看已部署 Agent
python3 deploy/bin/deploy-agent --list
```

## 文档

| 文档 | 说明 |
|------|------|
| [spec.md](docs/spec.md) | 架构主文档 |
| [L1 部署 SOP](docs/sop-l1-agent-deployment.md) | L1 部署步骤 (5-15 min) |
| [L2 极简 SOP](docs/sop-l2-minimal-setup.md) | L2 快速配置 (10 min) |
| [L2 完整 SOP](docs/sop-l2-agent-deployment.md) | L2 详细步骤 (90 min) |
| [自动化工具](docs/deploy-automation-guide.md) | deploy-agent 使用指南 |

## License

MIT
