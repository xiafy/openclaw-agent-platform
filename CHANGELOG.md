# 变更日志

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)

---

## [3.0.0] - 2026-03-03

### 新增
- 🔥 Beacon 智库 Agent 上线 (L1, 端口 19003)
- 📄 L1 部署 SOP (`sop-l1-agent-deployment.md`)
- 🛡️ Claw 安全检查（禁止操作端口 18789 / LaunchAgent）
- 🌐 独立 browser profile 机制（防止 CDP 端口冲突）
- ✅ 部署验证步骤（HTTP probe）

### 改进
- 🔧 部署脚本 v2.0 — openclaw.json 模板对齐实际格式
- 🔧 L1 部署器增加 auth-profiles 复制、LaunchAgent 管理
- 🔧 L2 部署器同步更新
- 📁 文档结构整理：9 篇历史文档归档，根目录精简到 7 篇

### 删除
- 🗑️ `scripts/` 目录（功能已被 `deploy/bin/` 替代）
- 🗑️ `memory/` 目录（旧工作日志，不属于项目仓库）

## [2.2.0] - 2026-02-27

### 新增
- ✨ Phase 2 — 企业级部署增强
  - DeployLogger 详细日志
  - 异常类层次结构
  - Jinja2 配置模板
  - 部署记录自动生成

## [2.0.0] - 2026-02-27

### 新增
- 🌟 shuaishuai L2 Agent 部署完成
- 📄 完整 SOP 文档体系
- 🔗 共享知识层

## [1.0.0] - 2026-02-24

### 新增
- 🦀 Claw + Sage L1 部署
- 📐 两层隔离架构设计
