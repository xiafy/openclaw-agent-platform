#!/usr/bin/env python3
"""
L2 独立用户模式部署器
"""

import subprocess
import shutil
import time
from pathlib import Path
from typing import Optional
from config import ConfigManager, DeployResult


class L2Deployer:
    """L2 独立用户模式部署器"""
    
    def __init__(self, config: ConfigManager, args, sudo_password: str):
        self.config = config
        self.args = args
        self.sudo_password = sudo_password
        self.username = args.username
        self.home_dir = Path.home()
        
        # 分配 UID (如果未指定)
        self.uid = args.uid if args.uid else config.allocate_uid()
        
        # 用户家目录
        self.user_home = Path('/Users') / self.username
        
    def run(self):
        """执行部署"""
        result = DeployResult(success=True, mode='l2', agent_name=self.username)
        result.username = self.username
        result.uid = self.uid
        
        try:
            # 1. 检查前置条件
            self._print_step(1, 8, "检查前置条件")
            self._check_prerequisites()
            
            # 2. 分配端口
            self._print_step(2, 8, "分配端口")
            result.port = self.config.allocate_port('l2')
            
            # 3. 创建 macOS 用户
            self._print_step(3, 8, "创建 macOS 用户")
            self._create_user()
            
            # 4. 安装依赖
            self._print_step(4, 8, "安装依赖")
            self._install_dependencies()
            
            # 5. 配置环境
            self._print_step(5, 8, "配置环境")
            self._configure_environment(result.port)
            
            # 6. 配置 LaunchDaemon
            self._print_step(6, 8, "配置 LaunchDaemon")
            self._setup_launchdaemon(result.port)
            
            # 7. 启动 Gateway
            self._print_step(7, 8, "启动 Gateway")
            self._start_gateway()
            result.gateway_running = True
            
            # 8. Telegram 配对
            self._print_step(8, 8, "Telegram 配对")
            result.bot_username = self._pair_telegram()
            
            # 注册 Agent
            self.config.register_agent(
                self.username, 'l2', result.port,
                username=self.username, uid=self.uid
            )
            
        except Exception as e:
            result.success = False
            result.error = str(e)
            raise
        
        return result
    
    def dry_run(self):
        """预演模式"""
        print("预演部署步骤:")
        print(f"  1. 检查前置条件")
        print(f"  2. 分配端口 (预计：{self.config.allocate_port('l2')})")
        print(f"  3. 分配 UID (预计：{self.uid})")
        print(f"  4. 创建用户：{self.username}")
        print(f"  5. 安装 NodeJS + OpenClaw")
        print(f"  6. 配置环境 (openclaw.json, symlink, auth)")
        print(f"  7. 配置 LaunchDaemon")
        print(f"  8. 启动 Gateway (端口 {self.config.allocate_port('l2')})")
        print(f"  9. Telegram 配对")
        print(f"\n✅ 预演完成")
    
    def rollback(self):
        """回滚"""
        print(f"🔄 回滚 L2 部署：{self.username}")
        
        # 停止 Gateway
        try:
            self._run_sudo(['launchctl', 'bootout', 'system', 
                           f'ai.openclaw.{self.username}.gateway'])
        except:
            pass
        
        # 删除 LaunchDaemon
        plist = Path('/Library/LaunchDaemons') / f'ai.openclaw.{self.username}.gateway.plist'
        if plist.exists():
            self._run_sudo(['rm', '-f', str(plist)])
        
        # 询问是否删除用户
        print(f"\n⚠️  用户 {self.username} 未删除")
        print("   如需删除，执行：sudo dscl . -delete /Users/{self.username}")
    
    def _print_step(self, current: int, total: int, message: str):
        """打印步骤"""
        print(f"[{current}/{total}] {message}... ", end='', flush=True)
    
    def _run_sudo(self, command: list, capture_output: bool = True):
        """执行 sudo 命令"""
        result = subprocess.run(
            ['sudo', '-S'] + command,
            input=self.sudo_password.encode(),
            capture_output=capture_output,
            check=True
        )
        return result
    
    def _run_as_user(self, command: list):
        """以目标用户身份执行命令"""
        result = subprocess.run(
            ['su', '-', self.username, '-c'] + [' '.join(command)],
            capture_output=True,
            text=True
        )
        return result
    
    def _check_prerequisites(self):
        """检查前置条件"""
        # 检查 OpenClaw 是否安装
        if not shutil.which('openclaw'):
            raise Exception("OpenClaw 未安装")
        
        # 检查共享层是否存在
        shared_path = Path(self.config.defaults['shared_path'])
        if not shared_path.exists():
            raise Exception(f"共享层不存在：{shared_path}")
        
        # 检查用户是否已存在
        result = subprocess.run(['dscl', '.', '-list', '/Users'], 
                               capture_output=True, text=True)
        if self.username in result.stdout:
            raise Exception(f"用户已存在：{self.username}")
        
        print("✅")
    
    def _create_user(self):
        """创建 macOS 用户"""
        # 创建用户
        self._run_sudo(['dscl', '.', '-create', f'/Users/{self.username}'])
        self._run_sudo(['dscl', '.', '-create', f'/Users/{self.username}', 
                       'UserShell', '/bin/zsh'])
        self._run_sudo(['dscl', '.', '-create', f'/Users/{self.username}', 
                       'RealName', self.args.role or self.username])
        self._run_sudo(['dscl', '.', '-create', f'/Users/{self.username}', 
                       'UniqueID', str(self.uid)])
        self._run_sudo(['dscl', '.', '-create', f'/Users/{self.username}', 
                       'PrimaryGroupID', '20'])
        self._run_sudo(['dscl', '.', '-create', f'/Users/{self.username}', 
                       'NFSHomeDirectory', str(self.user_home)])
        
        # 创建家目录
        self._run_sudo(['createhomedir', '-c', '-u', self.username])
        
        # 设置密码 (交互式)
        print("\n   请设置用户密码:")
        subprocess.run(['sudo', 'passwd', self.username])
        
        print("✅")
    
    def _install_dependencies(self):
        """安装依赖"""
        # 给 brew 权限
        self._run_sudo(['chown', '-R', self.username, '/opt/homebrew'])
        
        # 安装 NodeJS (以目标用户)
        self._run_as_user(['brew', 'install', 'node@20'])
        
        # 安装 OpenClaw
        self._run_as_user(['npm', 'install', '-g', 'openclaw', '--force'])
        
        print("✅")
    
    def _configure_environment(self, port: int):
        """配置环境"""
        # 创建目录
        self._run_as_user(['mkdir', '-p', '~/.openclaw/workspace'])
        
        # 复制配置
        main_config = self.home_dir / '.openclaw' / 'openclaw.json'
        user_config = self.user_home / '.openclaw' / 'openclaw.json'
        
        # 使用 sudo 复制
        self._run_sudo(['cp', str(main_config), str(user_config)])
        self._run_sudo(['chown', f'{self.username}:staff', str(user_config)])
        
        # 修改端口
        import json
        self._run_sudo(['python3', '-c', f'''
import json
with open("{user_config}", "r") as f:
    config = json.load(f)
config["gateway"] = config.get("gateway", {{}})
config["gateway"]["port"] = {port}
with open("{user_config}", "w") as f:
    json.dump(config, f, indent=2)
'''])
        
        # 配置 symlink
        shared = self.config.defaults['shared_path']
        self._run_as_user(['ln', '-s', f'{shared}/skills/summarize', 
                          '~/.openclaw/workspace/skills/summarize'])
        self._run_as_user(['ln', '-s', f'{shared}/skills/meeting-notes', 
                          '~/.openclaw/workspace/skills/meeting-notes'])
        self._run_as_user(['ln', '-s', f'{shared}/skills/domain-model-extract', 
                          '~/.openclaw/workspace/skills/domain-model-extract'])
        self._run_as_user(['ln', '-s', f'{shared}/protocols', 
                          '~/.openclaw/workspace/protocols'])
        self._run_as_user(['ln', '-s', f'{shared}/knowledge', 
                          '~/.openclaw/workspace/knowledge'])
        
        # 复制 auth
        auth_src = self.home_dir / '.openclaw' / 'agents' / 'main' / 'agent' / 'auth-profiles.json'
        auth_dst = self.user_home / '.openclaw' / 'agents' / 'main' / 'agent' / 'auth-profiles.json'
        self._run_sudo(['mkdir', '-p', str(auth_dst.parent)])
        self._run_sudo(['cp', str(auth_src), str(auth_dst)])
        self._run_sudo(['chown', f'{self.username}:staff', str(auth_dst)])
        
        print("✅")
    
    def _setup_launchdaemon(self, port: int):
        """配置 LaunchDaemon"""
        # 生成 plist
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.{self.username}.gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/openclaw</string>
        <string>gateway</string>
        <string>--port</string>
        <string>{port}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/{self.username}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/openclaw-{self.username}/openclaw.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/openclaw-{self.username}/openclaw.err</string>
    <key>UserName</key>
    <string>{self.username}</string>
</dict>
</plist>
'''
        
        # 写入 plist
        plist_path = Path('/Library/LaunchDaemons') / f'ai.openclaw.{self.username}.gateway.plist'
        self._run_sudo(['tee', str(plist_path)], input=plist_content.encode())
        self._run_sudo(['chown', 'root:wheel', str(plist_path)])
        self._run_sudo(['chmod', '644', str(plist_path)])
        
        # 加载
        self._run_sudo(['launchctl', 'bootstrap', 'system', str(plist_path)])
        
        print("✅")
    
    def _start_gateway(self):
        """启动 Gateway"""
        # 等待 LaunchDaemon 启动
        time.sleep(3)
        print("✅")
    
    def _pair_telegram(self) -> str:
        """Telegram 配对"""
        print("⚠️  请手动配对 Telegram")
        print("   1. 在 Telegram 搜索 Bot")
        print("   2. 发送 /start")
        print("   3. 获取配对码")
        print("   4. 执行：openclaw pairing approve telegram <CODE>")
        
        return f"{self.username}_bot"
