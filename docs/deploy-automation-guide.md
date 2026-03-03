# 部署自动化使用指南

> **版本**: v2.0
> **日期**: 2026-03-03
> **用途**: Agent 自动化部署工具使用指南

---

## 🚀 快速开始

### L1 部署 (Profile 模式，5 min)

```bash
# 交互式部署
cd ~/Documents/claw-outputs/projects/agent-platform
./deploy/bin/deploy-agent --mode l1 --name researcher --role "商业研究员"

# 全自动部署
./deploy/bin/deploy-agent --mode l1 --name researcher \
  --role "商业研究员" \
  --bot-token "123456:ABCdef..." \
  --no-verify
```

### L2 部署 (独立用户，30 min)

```bash
# 交互式部署
./deploy/bin/deploy-agent --mode l2 --username wifey --role "夫人助理"

# 全自动部署
./deploy/bin/deploy-agent --mode l2 --username wifey \
  --role "夫人助理" \
  --bot-token "123456:ABCdef..." \
  --no-verify
```


---

## ⚡ v2.0 变更 (2026-03-03)

- **openclaw.json 模板重写**: 对齐实际运行格式（嵌套 channels/agents/models 结构）
- **新增 auth-profiles 复制**: 自动从 Claw 复制 API Key
- **新增 browser profile 创建**: 每个 Agent 独立浏览器，避免端口冲突
- **新增 LaunchAgent (L1)**: 替代 Popen，支持开机自启和 launchd 管理
- **新增 Claw 安全检查**: 禁止操作 Claw 端口 18789 和 LaunchAgent
- **新增部署验证**: HTTP probe 检查 Gateway 是否响应
- **L2 同步更新**: 复用 v2 模板，增加 browser profile 和验证步骤

---

## 📖 命令参考

### 主命令

```bash
./deploy/bin/deploy-agent [选项]
```

### 选项

| 选项 | 说明 | 必需 |
|------|------|------|
| `--mode l1/l2` | 部署模式 | ✅ |
| `--name <名称>` | Agent 名称 (L1) | L1 必需 |
| `--username <用户名>` | macOS 用户名 (L2) | L2 必需 |
| `--role <描述>` | 角色描述 | 推荐 |
| `--bot-token <Token>` | Telegram Bot Token | 可选 |
| `--port <端口>` | 指定端口 | 可选 |
| `--uid <UID>` | 指定 UID (L2) | 可选 |
| `--dry-run` | 预演模式 | - |
| `--no-verify` | 跳过验证 | - |
| `--verbose, -v` | 详细输出 | - |
| `--list` | 列出已部署 Agent | - |
| `--verify` | 验证模式 | - |

---

## 📋 使用示例

### 示例 1: 部署 L1 Agent

```bash
# 1. 运行部署命令
./deploy/bin/deploy-agent --mode l1 --name researcher --role "商业研究员"

# 2. 输入 sudo 密码
🔐 需要 sudo 权限来配置系统
请输入 sudo 密码：********

# 3. 等待部署完成
[1/9] 检查前置条件... ✅
[2/9] 分配端口... ✅
[3/9] 创建目录结构... ✅
...
✅ 部署完成！

# 4. 验证部署
./deploy/bin/deploy-agent --verify --name researcher
```

### 示例 2: 部署 L2 Agent

```bash
# 1. 运行部署命令
./deploy/bin/deploy-agent --mode l2 --username wifey --role "夫人助理"

# 2. 输入 sudo 密码
🔐 需要 sudo 权限来配置系统
请输入 sudo 密码：********

# 3. 设置用户密码
请设置用户密码：
New password: ********
Retype new password: ********

# 4. 等待部署完成
[1/8] 检查前置条件... ✅
[2/8] 分配端口... ✅
[3/8] 创建 macOS 用户... ✅
...
✅ 部署完成！
```

### 示例 3: 预演模式

```bash
# 查看部署步骤但不实际执行
./deploy/bin/deploy-agent --mode l2 --username test --dry-run

# 输出:
预演部署步骤:
  1. 检查前置条件
  2. 分配端口 (预计：19004)
  3. 分配 UID (预计：503)
  4. 创建用户：test
  5. 安装 NodeJS + OpenClaw
  6. 配置环境
  7. 配置 LaunchDaemon
  8. 启动 Gateway
  9. Telegram 配对

✅ 预演完成
```

### 示例 4: 列出已部署 Agent

```bash
./deploy/bin/deploy-agent --list

# 输出:
📊 已部署的 Agent

名称                 模式     端口     用户                 UID     
----------------------------------------------------------------------
claw                 L1       18789    -                    -       
sage                 L1       19001    -                    -       
shuaishuai           L2       19002    shuaishuai           502     
----------------------------------------------------------------------
总计：3 个 Agent
```

### 示例 5: 验证部署

```bash
./deploy/bin/deploy-agent --verify --name shuaishuai

# 输出:
开始验证...

  ✅ 进程检查：Gateway 运行中
  ✅ 端口检查：端口 19002 监听中
  ✅ WebSocket 检查：WebSocket 可连接
  ⚠️  工作流程：跳过 (需手动验证)

验证结果：3/4 通过
```

### 示例 6: 回滚部署

```bash
# L1 回滚
./deploy/bin/deploy-agent --rollback --name test --mode l1

# L2 回滚
./deploy/bin/deploy-agent --rollback --name test --mode l2
```

---

## 🔧 快捷脚本

### L1 快速部署

```bash
# 使用快捷脚本
./scripts/deploy-l1-agent.sh --name researcher --role "商业研究员"
```

### L2 快速部署

```bash
# 使用快捷脚本
./scripts/deploy-l2-agent.sh --username wifey --role "夫人助理"
```

---

## ⚠️ 常见问题

### Q1: sudo 密码错误

```
❌ 部署失败：sudo: 1 incorrect password attempt
```

**解决**: 确认输入的是当前用户的 sudo 密码

### Q2: 端口已被占用

```
❌ 部署失败：Port 19003 is already in use
```

**解决**: 使用 `--port` 指定其他端口

### Q3: 用户已存在 (L2)

```
❌ 部署失败：用户已存在：wifey
```

**解决**: 使用不同的用户名，或删除现有用户

### Q4: 共享层不存在

```
❌ 部署失败：共享层不存在：/Users/Shared/openclaw-common
```

**解决**: 先创建共享层或检查路径

---

## 📊 部署后验证

### 手动验证

```bash
# 1. 检查进程
ps aux | grep openclaw | grep <端口>

# 2. 检查端口
lsof -i :<端口>

# 3. Telegram 测试
# 向 Bot 发送 /start

# 4. 工作流程测试
# 发送："你的工作流程是什么？"
```

### 自动验证

```bash
./deploy/bin/deploy-agent --verify --name <Agent 名称>
```

---

## 📁 目录结构

```
deploy/
├── bin/
│   ├── deploy-agent         # 主部署脚本 ⭐
│   ├── verify-agent         # 验证脚本
│   └── rollback-agent       # 回滚脚本
├── lib/
│   ├── config.py            # 配置管理
│   ├── deploy_l1.py         # L1 部署器
│   ├── deploy_l2.py         # L2 部署器
│   ├── verify.py            # 验证器
│   └── utils.py             # 工具函数
├── config/
│   ├── ports.yaml           # 端口分配
│   └── defaults.yaml        # 默认配置
├── templates/               # Jinja2 模板
└── logs/                    # 部署日志
```

---

## 🎯 最佳实践

1. **先用 --dry-run 预演** - 确认步骤无误
2. **L2 部署前备份** - 防止误操作
3. **验证部署结果** - 使用 --verify
4. **记录部署日志** - 便于排查问题
5. **定期更新工具** - 获取最新功能

---

*文档路径：`~/Documents/claw-outputs/projects/agent-platform/docs/deploy-automation-guide.md`*
*最后更新：2026-02-27 19:45*
