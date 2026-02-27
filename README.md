# OpenClaw Agent Platform — L2 Agent 部署文档

> **OpenClaw 多层隔离架构方案** — 在 macOS 上运行多个互相独立的 OpenClaw Agent

[![GitHub stars](https://img.shields.io/github/stars/xiafy/openclaw-agent-platform)](https://github.com/xiafy/openclaw-agent-platform/stargazers)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 快速开始

### 🚀 自动化部署 (推荐) ⭐

**L1 Profile 模式 (5 min)**:
```bash
./deploy/bin/deploy-agent --mode l1 --name researcher --role "商业研究员"
```

**L2 独立用户模式 (30 min)**:
```bash
./deploy/bin/deploy-agent --mode l2 --username wifey --role "夫人助理"
```

**预演模式**:
```bash
./deploy/bin/deploy-agent --mode l2 --username test --dry-run
```

**查看更多**: [部署使用指南](docs/deploy-automation-guide.md)

---

### 📖 手动部署 (参考)

**极简部署 (10 min)** - 已有 macOS 用户：
```bash
cat docs/sop-minimal-setup.md
```

**完整部署 (90 min)** - 从零开始：
```bash
cat docs/QUICKSTART-L2.md
```

---

## 📚 文档体系

```
docs/
├── 📘 架构与规划
│   └── spec.md                      # ⭐ 架构主文档 (v9)
│
├── 📗 部署 SOP (3 种模式)
│   ├── sop-minimal-setup.md         # ⭐ 极简配置 (10 min)
│   ├── QUICKSTART-L2.md             # ⭐ 快速部署 (90 min)
│   └── sop-l2-agent-deployment.md   # 完整 SOP (90 min + 踩坑)
│
├── 📙 复盘与总结
│   ├── SUMMARY-shuaishuai-l2.md     # ⭐ 最终总结
│   ├── retro-shuaishuai-l2.md       # 详细复盘
│   └── DOCUMENT-OPTIMIZATION-SUMMARY.md  # 优化总结
│
├── 📕 索引与导航
│   ├── README-deployment.md         # ⭐ 文档索引
│   ├── DOCUMENTATION-GUIDE.md       # ⭐ 维护指南
│   └── DOCUMENT-REVIEW-REPORT.md    # ⭐ 审查报告
│
└── 📁 archive/ (归档)
    ├── life-agent-plan.md           # 📜 shuaishuai 原始计划
    └── plan-sage.md                 # 📜 sage 计划 (过时)
```

---

## 🚀 部署模式

| 模式 | 适用场景 | 耗时 | 文档 |
|------|---------|------|------|
| **极简模式** ⭐ | 已有 macOS 用户，快速启动 | 10 min | `sop-minimal-setup.md` |
| **快速部署** | 从零开始，创建新用户 | 90 min | `QUICKSTART-L2.md` |
| **完整 SOP** | 深入学习，理解原理 | 90 min+ | `sop-l2-agent-deployment.md` |

---

## 🎯 核心特性

### L2 级别隔离

- ✅ 独立 macOS 用户
- ✅ OS 权限级文件隔离
- ✅ LaunchDaemon 开机自启
- ✅ 共享层 symlink

### 三种部署模式

- 极简模式 (10 min) — 快速启动
- 快速部署 (90 min) — 完整流程
- 完整 SOP — 深入学习

### 完整文档体系

- 9 篇核心文档 + 2 篇归档
- ~73K 字
- 场景化导航
- 踩坑记录 + 最佳实践

---

## 📊 当前部署状态

| Agent | 角色 | 级别 | 端口 | 状态 |
|-------|------|------|------|------|
| **claw** | 🦀 CEO 助手 | L1 | 18789 | ✅ |
| **sage** | 🧪 SAGE 项目 | L1 | 19001 | ✅ |
| **shuaishuai** | 🌟 生活助理 | L2 | 19002 | ✅ |

---

## 📖 使用指南

### 场景 1: 我要部署新 Agent

```
1. 阅读 sop-minimal-setup.md (极简) 或 QUICKSTART-L2.md (完整)
2. 准备 Telegram Bot Token
3. 按步骤执行
4. 验证测试
```

### 场景 2: 我要了解架构

```
1. 阅读 spec.md 第一、二章
2. 查看部署状态表格
3. 了解 L1 vs L2 区别
```

### 场景 3: 我要学习经验

```
1. 阅读 retro-shuaishuai-l2.md
2. 重点关注踩坑记录
3. 查看最佳实践
```

---

## ⚠️ 常见陷阱

| 问题 | 解决方案 |
|------|---------|
| brew 权限不足 | `sudo chown -R <user> /opt/homebrew` |
| LaunchAgent 失败 | 改用 LaunchDaemon |
| Auth 配置错误 | 复制 `auth-profiles.json` 而非 `auth.json` |
| Telegram 无响应 | 检查 Token、配对状态 |

详见：`docs/sop-l2-agent-deployment.md` 故障排查章节

---

## 🎓 最佳实践

1. **文档先行** — 执行前先写计划
2. **伴随更新** — 完成 Phase 立即更新文档
3. **极简启动** — 先 10 min 快速验证，再按需扩展
4. **共享层策略** — 通用知识单点维护，symlink 引用
5. **LaunchDaemon** — L2 用户无 GUI 会话，必须用 Daemon

---

## 📝 相关资源

| 资源 | 链接 |
|------|------|
| OpenClaw 官方 | https://github.com/openclaw/openclaw |
| OpenClaw 文档 | https://docs.openclaw.ai |
| 共享层注册表 | `/Users/Shared/openclaw-common/SHARED_REGISTRY.md` |

---

## 📄 许可证

MIT License

---

## 🦀 维护者

- **Claw** — CEO Assistant Bot
- **Mr. Xia** — Peblla CEO

---

*最后更新：2026-02-27*
*文档版本：v2.0*
