# Agent Platform — 文档中心

> **版本**: v3.0
> **更新日期**: 2026-03-03
> **维护者**: Claw 🦀
> **用途**: 统一文档入口，快速找到所需资料

---

## 📚 文档地图

```
docs/
├── 📘 架构与规划
│   └── spec.md                      # ⭐ 架构主文档 (v11)
│
├── 📗 部署 SOP (3 种模式)
│   ├── sop-minimal-setup.md         # ⭐ 极简配置 (10 min)
│   ├── QUICKSTART-L2.md             # ⭐ 快速部署 (90 min)
│   └── sop-l2-agent-deployment.md   # 完整 SOP (90 min+)
│
├── 📙 复盘与总结 (3 篇)
│   ├── SUMMARY-shuaishuai-l2.md     # ⭐ 最终总结
│   ├── retro-shuaishuai-l2.md       # 详细复盘
│   └── DOCUMENT-OPTIMIZATION-SUMMARY.md  # 优化总结
│
├── 📕 索引与导航 (3 篇)
│   ├── README-deployment.md         # ⭐ 文档索引
│   ├── DOCUMENTATION-GUIDE.md       # ⭐ 维护指南
│   └── DOCUMENT-REVIEW-REPORT.md    # ⭐ 审查报告
│
└── 📁 archive/ (归档)
    ├── life-agent-plan.md           # 📜 shuaishuai 原始计划
    └── plan-sage.md                 # 📜 sage 计划
```

---

## 🎯 按场景查找文档

### 场景 1: 我要部署新 Agent

**推荐路径**:

| 需求 | 文档/工具 | 耗时 |
|------|----------|------|
| L1 自动部署 (推荐) | `deploy-agent --mode l1` | 5 min |
| L2 自动部署 (推荐) | `deploy-agent --mode l2` | 30 min |
| L2 手动部署 | `QUICKSTART-L2.md` | 90 min |
| 深入学习 | `sop-l2-agent-deployment.md` | 120 min |

**执行流程**:
```
1. 阅读对应 SOP
2. 准备 Telegram Bot Token
3. 按步骤执行
4. 验证测试
5. 更新 spec.md 和 SHARED_REGISTRY.md
```

---

### 场景 2: 我要了解架构

**推荐路径**:

| 主题 | 文档 | 章节 |
|------|------|------|
| 整体架构 | `spec.md` | 第一、二章 |
| 部署状态 | `spec.md` | 第三章 |
| L1 vs L2 | `spec.md` | 第二章 |
| Agent 阵容 | `spec.md` | 第四章 |

**预计耗时**: 15 min

---

### 场景 3: 我要学习经验

**推荐路径**:

| 内容 | 文档 | 章节 |
|------|------|------|
| 踩坑记录 | `retro-shuaishuai-l2.md` | 第三章 |
| 最佳实践 | `SUMMARY-shuaishuai-l2.md` | 核心最佳实践 |
| 时间分配 | `retro-shuaishuai-l2.md` | 时间分配回顾 |
| 配置方案 | `sop-minimal-setup.md` | 配置原则 |

**预计耗时**: 30 min

---

### 场景 4: 我要排查问题

**推荐路径**:

| 问题类型 | 文档 | 章节 |
|---------|------|------|
| brew/npm 权限 | `QUICKSTART-L2.md` | 踩坑 #1 #2 |
| LaunchAgent 失败 | `retro-shuaishuai-l2.md` | 踩坑 #3 |
| Auth 配置错误 | `retro-shuaishuai-l2.md` | 踩坑 #4 |
| Telegram 无响应 | `sop-l2-agent-deployment.md` | 故障排查 |

**预计耗时**: 10 min

---

### 场景 5: 我要配置共享层

**推荐路径**:

| 内容 | 文档 |
|------|------|
| 共享资产清单 | `/Users/Shared/openclaw-common/SHARED_REGISTRY.md` |
| 分类原则 | `spec.md` | 第五章 |
| 维护规则 | `SHARED_REGISTRY.md` | 维护规则 |

**预计耗时**: 10 min

---

## 📊 当前部署状态

| Agent | 角色 | 级别 | 端口 | 配置模式 | 状态 | 文档 |
|-------|------|------|------|---------|------|------|
| **claw** | 🦀 CEO 助手 | L1 | 18789 | Profile | ✅ | spec.md |
| **sage** | 🧪 SAGE 项目 | L1 | 19001 | Profile | ✅ | spec.md |
| **beacon** | 🔥 智库 | L1 | 19003 | Profile | ✅ | spec.md |
| **shuaishuai** | 🌟 生活助理 | L2 | 19002 | 极简 | ✅ | SUMMARY-shuaishuai-l2.md |

---

## 🎓 文档版本历史

| 日期 | 版本 | 变更 | 文档数 |
|------|------|------|--------|
| 2026-02-27 | v1.0 | 初始版本 (shuaishuai 部署完成) | 6 |
| 2026-02-27 | v2.0 | 优化结构，新增极简模式 | 7 |
| 2026-03-03 | v3.0 | Beacon 上线，部署脚本 v2.0，浏览器隔离 | 7 |

---

## 📁 完整文档清单

## 📊 完整文档清单

### 核心文档 (9 篇)

| 文档 | 路径 | 字数 | 用途 | 状态 |
|------|------|------|------|------|
| **spec.md** | `spec.md` | ~8K | 架构主文档 | ✅ v11 |
| **sop-minimal-setup.md** | `sop-minimal-setup.md` | ~5K | ⭐ 极简配置 SOP | ✅ v1.0 |
| **QUICKSTART-L2.md** | `QUICKSTART-L2.md` | ~8K | ⭐ 快速部署指南 | ✅ v2.0 |
| **sop-l2-agent-deployment.md** | `sop-l2-agent-deployment.md` | ~9K | 完整部署 SOP | ✅ v1.0 |
| **SUMMARY-shuaishuai-l2.md** | `SUMMARY-shuaishuai-l2.md` | ~6K | ⭐ 最终总结 | ✅ v1.1 |
| **retro-shuaishuai-l2.md** | `retro-shuaishuai-l2.md` | ~11K | 详细复盘 | ✅ v1.0 |
| **README-deployment.md** | `README-deployment.md` | ~7K | ⭐ 文档索引 | ✅ v2.0 |
| **DOCUMENTATION-GUIDE.md** | `DOCUMENTATION-GUIDE.md` | ~5K | ⭐ 维护指南 | ✅ v1.0 |
| **DOCUMENT-OPTIMIZATION-SUMMARY.md** | `DOCUMENT-OPTIMIZATION-SUMMARY.md` | ~7K | 优化总结 | ✅ v1.0 |

### 归档文档 (2 篇)

| 文档 | 路径 | 字数 | 用途 | 状态 |
|------|------|------|------|------|
| **life-agent-plan.md** | `archive/life-agent-plan.md` | ~8K | shuaishuai 原始计划 | 📜 历史 |
| **plan-sage.md** | `archive/plan-sage.md` | ~2K | sage 计划 | 📜 过时 |

**总计**: 11 篇文档，~73K 字 (核心 9 篇 ~65K)

---

## 🔗 外部文档

| 文档 | 路径 | 用途 |
|------|------|------|
| **共享资产注册表** | `/Users/Shared/openclaw-common/SHARED_REGISTRY.md` | 共享层清单 |
| **执行流程** | `/Users/Shared/openclaw-common/protocols/execution-protocol.md` | 六步法 |
| **纠错协议** | `/Users/Shared/openclaw-common/protocols/error-correction.md` | STOP 协议 |
| **浏览器策略** | `/Users/Shared/openclaw-common/protocols/browser-strategy.md` | L0-L3 |
| **编码规范** | `/Users/Shared/openclaw-common/protocols/coding-conventions.md` | 工程规范 |
| **模型策略** | `/Users/Shared/openclaw-common/knowledge/model-strategy.md` | 模型分工 |
| **用户画像** | `/Users/Shared/openclaw-common/knowledge/user-profile.md` | 夏总偏好 |

---

## 💡 使用建议

### 新手 (第一次部署)
```
1. 阅读 QUICKSTART-L2.md (了解全貌)
2. 执行 sop-minimal-setup.md (快速启动)
3. 遇到问题查阅 retro-shuaishuai-l2.md (踩坑记录)
```

### 老手 (第二次及以后)
```
1. 直接执行 sop-minimal-setup.md (10 min 完成)
2. 按需扩展配置
```

### 学习者 (理解原理)
```
1. 阅读 spec.md (架构设计)
2. 阅读 retro-shuaishuai-l2.md (实战复盘)
3. 阅读 sop-l2-agent-deployment.md (详细步骤)
```

### 管理者 (了解状态)
```
1. 阅读 SUMMARY-shuaishuai-l2.md (成果总结)
2. 查看 spec.md 第三章 (部署状态)
```

---

## 📞 获取帮助

### 自助排查
```bash
# 1. 检查进程
ps aux | grep "openclaw.*<端口>"

# 2. 查看日志
tail -50 /tmp/openclaw-<username>/openclaw.log

# 3. 验证配置
openclaw doctor

# 4. 检查配对
openclaw pairing list
```

### 文档查找
- 找流程 → 看 SOP
- 找问题 → 看复盘
- 找状态 → 看 spec.md
- 找入口 → 看本文档

---

## 📝 维护责任

| 文档类型 | 维护者 | 更新时机 |
|---------|--------|---------|
| 架构文档 (spec.md) | Claw | 每次部署后 |
| SOP | Claw | 每次复盘后优化 |
| 复盘报告 | Claw | 每次部署后 24h 内 |
| 索引文档 | Claw | 新增文档时 |
| 共享层注册表 | Claw | 新增共享资产时 |

---

## 🎯 下一步行动

| 优先级 | 行动 | 说明 |
|-------|------|------|
| P2 | 跨 Agent 通信 | Telegram 互发方案 |
| P2 | support Agent | L1 Profile 售后服务 |
| P3 | wifey Agent | L2 夫人助理 |
| ✅ | ~~部署脚本 v2.0~~ | 2026-03-03 完成，L1/L2 均已对齐实际配置 |
| ✅ | ~~Beacon 智库 Agent~~ | 2026-03-03 上线 (合并 researcher + analyst) |

---

*文档路径：`~/Documents/claw-outputs/projects/agent-platform/docs/README-deployment.md`*
*最后更新：2026-02-27 18:50*
