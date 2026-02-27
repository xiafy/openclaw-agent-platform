# 变更日志

所有重要变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [2.1.0] - 2026-02-27

### 新增
- ✨ 自动化部署工具 v1.0 (Phase 1 完成)
  - ✅ L1/L2 部署器
  - ✅ 验证系统
  - ✅ 回滚机制
  - ✅ 交互式 sudo 密码输入
  - ✅ 端口/UID 自动分配

### 修复
- 🔧 修复 list-agents 显示 N/A 问题 (兼容旧数据格式)
  - `deploy-agent` 主部署脚本
  - L1/L2 部署器
  - 验证系统
  - 回滚机制
- ✨ 交互式 sudo 密码输入 (安全)
- ✨ 端口/UID 自动分配
- ✨ 快捷脚本 (`deploy-l1-agent.sh`, `deploy-l2-agent.sh`)
- ✨ 部署使用指南 (`deploy-automation-guide.md`)

### 改进
- ✨ 极简配置模式 (10 min) — `sop-minimal-setup.md`
- ✨ 文档维护指南 — `DOCUMENTATION-GUIDE.md`
- ✨ 文档优化总结 — `DOCUMENT-OPTIMIZATION-SUMMARY.md`
- ✨ 文档审查报告 — `DOCUMENT-REVIEW-REPORT.md`

### 改进
- 🚀 重构文档索引 (README-deployment.md v2.0)
- 🚀 优化快速部署指南 (QUICKSTART-L2.md v2.0)
- 🚀 统一标记规范 (⭐ 核心文档，📜 历史文档)
- 🚀 场景化导航，按角色/需求查找文档

### 修复
- 🐛 更新 spec.md 部署状态日期 (2026-02-27)
- 🐛 更新 SUMMARY 中文档数量统计 (10 篇)
- 🐛 归档过时文档 (plan-sage.md, life-agent-plan.md)

### 文档
- 📚 新增 LICENSE (MIT)
- 📚 新增 CHANGELOG.md
- 📚 文档总数：11 篇 → 9 篇 (核心) + 2 篇 (归档)

---

## [1.0.0] - 2026-02-27

### 新增
- ✨ 初始版本 — shuaishuai L2 Agent 部署完成
- ✨ 架构主文档 — `spec.md` (v8)
- ✨ 完整部署 SOP — `sop-l2-agent-deployment.md`
- ✨ 快速部署指南 — `QUICKSTART-L2.md`
- ✨ 详细复盘报告 — `retro-shuaishuai-l2.md`
- ✨ 最终总结 — `SUMMARY-shuaishuai-l2.md`
- ✨ 文档索引 — `README-deployment.md`
- ✨ 原始计划 — `life-agent-plan.md`

### 部署成果
- 🦀 claw (L1, 18789) — CEO 助手
- 🧪 sage (L1, 19001) — SAGE 项目
- 🌟 shuaishuai (L2, 19002) — 个人生活助理

### 文档统计
- 文档总数：11 篇
- 总字数：~73K
- 核心文档：6 篇
- SOP 文档：3 篇
- 复盘文档：2 篇

---

## [0.1.0] - 2026-02-24

### 新增
- ✨ 项目初始化
- ✨ 架构设计 (L1/L2 隔离方案)
- ✨ 共享知识层设计

---

## 版本说明

### 语义化版本

- **主版本号 (Major)**: 不兼容的 API 变更
- **次版本号 (Minor)**: 向后兼容的功能新增
- **修订号 (Patch)**: 向后兼容的问题修正

### 文档版本策略

- **架构文档 (spec.md)**: 重大架构变更时升级主版本
- **SOP 文档**: 流程变更时升级次版本，文字优化升级修订号
- **复盘文档**: 一次性文档，不升级版本
- **索引文档**: 结构变更时升级次版本

---

*最后更新：2026-02-27 19:15*
