# Agent 自动化部署方案设计

> **版本**: v1.0
> **日期**: 2026-02-27
> **目标**: L1/L2 部署完全自动化 (一键部署)
> **预期耗时**: L1 (5 min) / L2 (30 min)

---

## 🎯 设计目标

### 当前状态 (手动)

| 部署类型 | 当前耗时 | 手动步骤 | 痛点 |
|---------|---------|---------|------|
| **L1 (Profile)** | 30 min | 8 步 | 配置重复、易出错 |
| **L2 (完整)** | 90 min | 9 步 | 权限问题、步骤繁琐 |
| **L2 (极简)** | 10 min | 5 步 | 需手动执行命令 |

### 自动化目标

| 部署类型 | 目标耗时 | 自动化率 | 用户交互 |
|---------|---------|---------|---------|
| **L1 (Profile)** | 5 min | 95% | 仅确认 |
| **L2 (完整)** | 30 min | 90% | 密码输入 |
| **L2 (极简)** | 3 min | 95% | 仅确认 |

---

## 🏗️ 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                   部署自动化系统                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │  配置管理   │    │  部署引擎   │    │  验证系统   │ │
│  │  Config     │    │  Deploy     │    │  Verify     │ │
│  │  Manager    │    │  Engine     │    │  System     │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │  配置模板   │    │  L1/L2      │    │  健康检查   │ │
│  │  Templates  │    │  Scripts    │    │  Checks     │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                    用户界面层                            │
├─────────────────────────────────────────────────────────┤
│  CLI (命令行)  │  Web UI (可选)  │  API (可选)         │
└─────────────────────────────────────────────────────────┘
```

### 核心组件

| 组件 | 职责 | 实现方式 |
|------|------|---------|
| **配置管理** | 配置生成、验证、模板化 | Python + Jinja2 |
| **部署引擎** | 执行部署流程、错误处理 | Shell + Python |
| **验证系统** | 部署后验证、健康检查 | Shell + HTTP 请求 |
| **回滚机制** | 失败回滚、状态恢复 | Shell 脚本 |

---

## 📁 目录结构

```
~/Documents/claw-outputs/projects/agent-platform/
├── deploy/                          # 部署自动化目录
│   ├── bin/                         # 可执行脚本
│   │   ├── deploy-agent             # 主部署脚本 (Python)
│   │   ├── verify-agent             # 验证脚本
│   │   ├── rollback-agent           # 回滚脚本
│   │   └── list-agents              # 列出已部署 Agent
│   │
│   ├── lib/                         # 库函数
│   │   ├── config.py                # 配置管理
│   │   ├── deploy_l1.py             # L1 部署逻辑
│   │   ├── deploy_l2.py             # L2 部署逻辑
│   │   ├── verify.py                # 验证逻辑
│   │   └── utils.py                 # 工具函数
│   │
│   ├── templates/                   # 配置模板
│   │   ├── openclaw.json.j2         # openclaw 配置模板
│   │   ├── launchdaemon.plist.j2    # LaunchDaemon 模板
│   │   ├── IDENTITY.md.j2           # 人设模板
│   │   └── .env.j2                  # 环境变量模板
│   │
│   ├── config/                      # 配置文件
│   │   ├── agents.yaml              # Agent 配置清单
│   │   ├── ports.yaml               # 端口分配表
│   │   └── defaults.yaml            # 默认配置
│   │
│   └── logs/                        # 部署日志
│       └── deploy-YYYY-MM-DD.log
│
├── docs/
│   ├── deploy-automation-design.md  # 本文件
│   ├── deploy-automation-guide.md   # 使用指南
│   └── deploy-automation-api.md     # API 文档
│
└── scripts/                         # 快捷脚本 (兼容旧版)
    ├── deploy-l1-agent.sh           # L1 快速部署
    └── deploy-l2-agent.sh           # L2 快速部署
```

---

## 🚀 部署流程设计

### L1 部署流程 (Profile 模式)

```
用户输入
    │
    ▼
┌─────────────────┐
│ 1. 输入 Agent 信息 │
│    - 名称        │
│    - 角色        │
│    - Bot Token   │
│    - 端口 (自动)  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 2. 检查前置条件   │
│    - OpenClaw   │
│    - 端口占用    │
│    - Bot Token  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 3. 创建 Profile   │
│    - 目录结构    │
│    - symlink    │
│    - 配置文件    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 4. 启动 Gateway   │
│    - openclaw   │
│    - 验证端口    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 5. Telegram 配对  │
│    - 获取配对码  │
│    - 自动批准    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 6. 验证测试      │
│    - 工作流程    │
│    - 模型测试    │
│    - 功能测试    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 7. 生成报告      │
│    - 部署状态    │
│    - Bot 信息    │
│    - 访问方式    │
└─────────────────┘
    │
    ▼
✅ 部署完成 (5 min)
```

### L2 部署流程 (完整模式)

```
用户输入
    │
    ▼
┌─────────────────┐
│ 1. 输入 Agent 信息 │
│    - 用户名      │
│    - 显示名称    │
│    - Bot Token   │
│    - UID (自动)  │
│    - 密码        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 2. 创建 macOS 用户  │
│    - dscl 命令   │
│    - 设置密码    │
│    - 创建家目录  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 3. 安装依赖      │
│    - brew 权限   │
│    - NodeJS     │
│    - OpenClaw   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 4. 配置环境      │
│    - openclaw   │
│    - 共享层     │
│    - Auth       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 5. 配置 LaunchDaemon│
│    - plist 生成  │
│    - 权限设置    │
│    - 加载启动    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 6. Telegram 配对  │
│    - 自动批准    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 7. 验证测试      │
│    - 进程检查    │
│    - 端口检查    │
│    - 功能测试    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 8. 生成报告      │
│    - 用户信息    │
│    - Gateway 状态│
│    - Bot 信息    │
└─────────────────┘
    │
    ▼
✅ 部署完成 (30 min)
```

---

## 💻 脚本设计

### 主部署脚本 (deploy-agent)

```python
#!/usr/bin/env python3
"""
Agent 自动化部署工具
支持 L1 (Profile) 和 L2 (独立用户) 两种模式
"""

import argparse
import sys
from lib.config import ConfigManager
from lib.deploy_l1 import L1Deployer
from lib.deploy_l2 import L2Deployer
from lib.verify import Verifier

def main():
    parser = argparse.ArgumentParser(description='OpenClaw Agent 自动化部署工具')
    
    # 部署模式
    parser.add_argument('--mode', choices=['l1', 'l2'], required=True,
                       help='部署模式：l1=Profile, l2=独立用户')
    
    # Agent 信息
    parser.add_argument('--name', required=True, help='Agent 名称')
    parser.add_argument('--role', help='Agent 角色描述')
    parser.add_argument('--bot-token', help='Telegram Bot Token')
    
    # L2 特有
    parser.add_argument('--username', help='macOS 用户名 (L2 模式)')
    parser.add_argument('--uid', type=int, help='用户 ID (L2 模式, 自动分配)')
    parser.add_argument('--password', help='用户密码 (L2 模式)')
    
    # 高级选项
    parser.add_argument('--port', type=int, help='端口号 (自动分配)')
    parser.add_argument('--dry-run', action='store_true', help='预演模式')
    parser.add_argument('--no-verify', action='store_true', help='跳过验证')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 配置管理
    config = ConfigManager()
    
    # 选择部署器
    if args.mode == 'l1':
        deployer = L1Deployer(config, args)
    else:  # l2
        deployer = L2Deployer(config, args)
    
    # 执行部署
    try:
        result = deployer.run()
        
        # 验证
        if result.success and not args.no_verify:
            verifier = Verifier(result)
            verifier.run()
        
        # 输出报告
        print_report(result)
        
    except Exception as e:
        # 回滚
        deployer.rollback()
        print(f"❌ 部署失败：{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### L1 部署器 (deploy_l1.py)

```python
class L1Deployer:
    """L1 Profile 模式部署器"""
    
    def __init__(self, config, args):
        self.config = config
        self.args = args
        self.profile_name = args.name
        
    def run(self):
        """执行部署"""
        steps = [
            self.check_prerequisites,
            self.create_profile_dir,
            self.generate_config,
            self.setup_symlinks,
            self.start_gateway,
            self.pair_telegram,
        ]
        
        for step in steps:
            step()
            
        return DeployResult(success=True, mode='l1', profile=self.profile_name)
    
    def check_prerequisites(self):
        """检查前置条件"""
        # 检查 OpenClaw 是否安装
        # 检查端口是否占用
        # 检查 Bot Token 是否有效
        
    def create_profile_dir(self):
        """创建 Profile 目录"""
        # ~/.openclaw-<profile>/
        
    def generate_config(self):
        """生成配置文件"""
        # 使用 Jinja2 模板
        
    def setup_symlinks(self):
        """配置共享层 symlink"""
        # skills, protocols, knowledge
        
    def start_gateway(self):
        """启动 Gateway"""
        # openclaw gateway
        
    def pair_telegram(self):
        """Telegram 配对"""
        # 自动获取配对码并批准
```

### L2 部署器 (deploy_l2.py)

```python
class L2Deployer:
    """L2 独立用户模式部署器"""
    
    def __init__(self, config, args):
        self.config = config
        self.args = args
        self.username = args.username
        
    def run(self):
        """执行部署"""
        steps = [
            self.check_prerequisites,
            self.create_user,
            self.install_dependencies,
            self.configure_environment,
            self.setup_launchdaemon,
            self.start_gateway,
            self.pair_telegram,
        ]
        
        for step in steps:
            step()
            
        return DeployResult(success=True, mode='l2', username=self.username)
    
    def create_user(self):
        """创建 macOS 用户"""
        # dscl 命令
        
    def install_dependencies(self):
        """安装依赖"""
        # brew, node, openclaw
        
    def configure_environment(self):
        """配置环境"""
        # openclaw.json, symlink, auth
        
    def setup_launchdaemon(self):
        """配置 LaunchDaemon"""
        # plist 生成和加载
```

---

## 🔧 配置模板

### openclaw.json.j2

```jinja2
{
  "meta": {
    "lastTouchedVersion": "2026.2.26",
    "agent": "{{ agent_name }}"
  },
  "env": {
    "DASHSCOPE_API_KEY": "{{ dashscope_key }}"
  },
  "gateway": {
    "port": {{ port }}
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "{{ bot_token }}"
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "{{ default_model }}"
      }
    }
  }
}
```

### launchdaemon.plist.j2

```jinja2
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.{{ username }}.gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/openclaw</string>
        <string>gateway</string>
        <string>--port</string>
        <string>{{ port }}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/{{ username }}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>UserName</key>
    <string>{{ username }}</string>
</dict>
</plist>
```

---

## 📊 端口和 UID 分配

### ports.yaml

```yaml
# 端口分配表
allocated:
  - port: 18789
    agent: claw
    mode: l1
  - port: 19001
    agent: sage
    mode: l1
  - port: 19002
    agent: shuaishuai
    mode: l2

next_available:
  l1: 19003
  l2: 19004

reserved:
  - 18788  # 保留
  - 19000  # 保留
```

### UID 分配

```yaml
# UID 分配表
allocated:
  - uid: 501
    username: xiafybot
  - uid: 502
    username: shuaishuai

next_available: 503

reserved:
  - 0-100    # 系统
  - 200-300  # 保留
```

---

## ✅ 验证系统

### 验证项目

| 检查项 | 方法 | 预期 |
|-------|------|------|
| 进程运行 | `ps aux \| grep openclaw` | 有进程 |
| 端口监听 | `lsof -i :<port>` | LISTEN |
| WebSocket | `ws://localhost:<port>` | 可连接 |
| Telegram | 发送 `/start` | Bot 回复 |
| 模型 | 发送测试问题 | 正常回答 |
| 工作流程 | "你的工作流程" | 回答六步法 |

### verify.py

```python
class Verifier:
    """部署验证器"""
    
    def __init__(self, deploy_result):
        self.result = deploy_result
        
    def run(self):
        """执行验证"""
        checks = [
            self.check_process,
            self.check_port,
            self.check_websocket,
            self.check_telegram,
            self.check_workflow,
        ]
        
        results = []
        for check in checks:
            result = check()
            results.append(result)
            
        return VerifyReport(results)
    
    def check_process(self):
        """检查进程"""
        # ps aux | grep openclaw
        
    def check_port(self):
        """检查端口"""
        # lsof -i :<port>
        
    def check_telegram(self):
        """检查 Telegram"""
        # 发送 /start
```

---

## 🔄 回滚机制

### rollback-agent

```bash
#!/bin/bash
# 部署回滚脚本

set -e

AGENT_NAME=$1
MODE=$2

echo "🔄 开始回滚 $AGENT_NAME ($MODE)..."

if [ "$MODE" = "l2" ]; then
    # L2 回滚
    echo "1. 停止 Gateway"
    launchctl bootout system/ai.openclaw.$AGENT_NAME.gateway
    
    echo "2. 删除 LaunchDaemon"
    rm -f /Library/LaunchDaemons/ai.openclaw.$AGENT_NAME.gateway.plist
    
    echo "3. 删除用户 (可选)"
    read -p "是否删除用户 $AGENT_NAME? [y/N] " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo dscl . -delete /Users/$AGENT_NAME
    fi
else
    # L1 回滚
    echo "1. 停止 Gateway"
    # kill 进程
    
    echo "2. 删除 Profile 目录"
    rm -rf ~/.openclaw-$AGENT_NAME
fi

echo "✅ 回滚完成"
```

---

## 📱 用户界面

### CLI 使用示例

```bash
# L1 部署 (交互式)
./deploy-agent --mode l1 --name researcher --role "商业研究员"

# L1 部署 (全自动)
./deploy-agent --mode l1 --name researcher --role "商业研究员" \
  --bot-token "123456:ABCdef..." --no-verify

# L2 部署 (交互式)
./deploy-agent --mode l2 --username wifey --role "夫人助理"

# L2 部署 (全自动)
./deploy-agent --mode l2 --username wifey --role "夫人助理" \
  --bot-token "123456:ABCdef..." --password "wifey.2026"

# 预演模式
./deploy-agent --mode l2 --username test --dry-run

# 列出已部署 Agent
./list-agents

# 验证部署
./verify-agent --name shuaishuai

# 回滚
./rollback-agent --name test --mode l2
```

### 交互式界面 (可选)

```
🦀 OpenClaw Agent 部署工具 v1.0

部署模式:
  1) L1 - Profile (快速，5 min)
  2) L2 - 独立用户 (完整，30 min)
  
选择 [1-2]: 1

Agent 名称：researcher
角色描述：商业研究员
Telegram Bot Token: 123456:ABCdef...

前置条件检查...
✅ OpenClaw 已安装
✅ 端口 19003 可用
✅ Bot Token 有效

开始部署...
[1/6] 创建 Profile 目录... ✅
[2/6] 生成配置文件... ✅
[3/6] 配置共享层... ✅
[4/6] 启动 Gateway... ✅
[5/6] Telegram 配对... ✅
[6/6] 验证测试... ✅

✅ 部署完成！

Bot: @researcher_bot
端口：19003
访问：https://t.me/researcher_bot
```

---

## 📈 实施计划

### Phase 1: 核心功能 (本周)

- [ ] 创建目录结构
- [ ] 实现 L1 部署器
- [ ] 实现 L2 部署器
- [ ] 配置模板 (Jinja2)
- [ ] 基础验证系统

**预计**: 8-10 小时

### Phase 2: 完善功能 (下周)

- [ ] 回滚机制
- [ ] 端口/UID 自动分配
- [ ] 详细日志
- [ ] 错误处理
- [ ] 文档编写

**预计**: 6-8 小时

### Phase 3: 优化体验 (可选)

- [ ] 交互式界面
- [ ] Web UI (可选)
- [ ] API 接口 (可选)
- [ ] 批量部署

**预计**: 10-15 小时

---

## 🎯 成功标准

| 指标 | 目标 | 测量方法 |
|------|------|---------|
| 部署时间 (L1) | < 5 min | 计时测试 |
| 部署时间 (L2) | < 30 min | 计时测试 |
| 自动化率 | > 90% | 手动步骤计数 |
| 成功率 | > 95% | 部署测试 |
| 回滚成功率 | 100% | 回滚测试 |
| 用户满意度 | > 4.5/5 | 用户反馈 |

---

## ⚠️ 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| sudo 密码输入 | 高 | 中 | 交互式提示 |
| brew 权限问题 | 中 | 高 | 自动修复 |
| 端口冲突 | 低 | 中 | 自动检测 |
| Bot Token 无效 | 中 | 高 | 预验证 |
| LaunchDaemon 失败 | 低 | 高 | 回滚机制 |

---

## 📚 相关文档

- `deploy-automation-guide.md` — 使用指南
- `deploy-automation-api.md` — API 文档
- `CHANGELOG.md` — 变更日志

---

*文档路径：`~/Documents/claw-outputs/projects/agent-platform/docs/deploy-automation-design.md`*
*最后更新：2026-02-27 19:30*
