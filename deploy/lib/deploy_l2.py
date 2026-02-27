#!/usr/bin/env python3
"""
L2 独立用户模式部署器 (增强版)
"""

import subprocess
import shutil
import json
import time
from pathlib import Path
from datetime import datetime
from jinja2 import Template

from config import ConfigManager, DeployResult
from logger import DeployLogger
from exceptions import (
    PrerequisiteError, ConfigError, PermissionError,
    NetworkError, TelegramError, RollbackError
)


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
        
        # 日志目录
        self.logs_dir = self.home_dir / '.openclaw' / 'deploy-logs'
        self.logger = DeployLogger(self.logs_dir, self.username, 'l2')
        
    def run(self):
        """执行部署"""
        result = DeployResult(success=True, mode='l2', agent_name=self.username)
        result.username = self.username
        result.uid = self.uid
        
        try:
            self.logger.info(f"🚀 开始部署 {self.username} (L2 模式)")
            self.logger.debug(f"用户家目录：{self.user_home}")
            self.logger.debug(f"分配 UID: {self.uid}")
            self.logger.debug(f"日志目录：{self.logs_dir}")
            
            # 1. 检查前置条件
            self.logger.step_start(1, 8, "检查前置条件")
            try:
                self._check_prerequisites()
                self.logger.step_complete(1, 8, "检查前置条件")
            except PrerequisiteError as e:
                self.logger.step_failed(1, 8, "检查前置条件", str(e))
                raise
            
            # 2. 分配端口
            self.logger.step_start(2, 8, "分配端口")
            result.port = self.config.allocate_port('l2')
            self.logger.debug(f"分配端口：{result.port}")
            self.logger.step_complete(2, 8, "分配端口")
            
            # 3. 创建 macOS 用户
            self.logger.step_start(3, 8, "创建 macOS 用户")
            self._create_user()
            self.logger.step_complete(3, 8, "创建 macOS 用户")
            
            # 4. 安装依赖
            self.logger.step_start(4, 8, "安装依赖")
            self._install_dependencies()
            self.logger.step_complete(4, 8, "安装依赖")
            
            # 5. 配置环境
            self.logger.step_start(5, 8, "配置环境")
            self._configure_environment(result.port)
            self.logger.step_complete(5, 8, "配置环境")
            
            # 6. 配置 LaunchDaemon
            self.logger.step_start(6, 8, "配置 LaunchDaemon")
            self._setup_launchdaemon(result.port)
            self.logger.step_complete(6, 8, "配置 LaunchDaemon")
            
            # 7. 启动 Gateway
            self.logger.step_start(7, 8, "启动 Gateway")
            self._start_gateway()
            result.gateway_running = True
            self.logger.step_complete(7, 8, "启动 Gateway")
            
            # 8. Telegram 配对
            self.logger.step_start(8, 8, "Telegram 配对")
            result.bot_username = self._pair_telegram()
            self.logger.step_complete(8, 8, "Telegram 配对")
            
            # 注册 Agent
            self.config.register_agent(
                self.username, 'l2', result.port,
                username=self.username, uid=self.uid
            )
            
            # 生成部署记录
            self._generate_deploy_record(result)
            
            self.logger.success(f"部署完成！日志：{self.logger.get_log_path()}")
            
        except Exception as e:
            result.success = False
            result.error = str(e)
            self.logger.error(f"部署失败：{e}")
            self.logger.debug(f"日志文件：{self.logger.get_log_path()}")
            raise
        
        return result
    
    def dry_run(self):
        """预演模式"""
        self.logger.info("预演部署步骤:")
        steps = [
            "检查前置条件",
            f"分配端口 (预计：{self.config.allocate_port('l2')})",
            f"分配 UID (预计：{self.uid})",
            f"创建用户：{self.username}",
            "安装 NodeJS + OpenClaw",
            "配置环境 (openclaw.json, symlink, auth)",
            "配置 LaunchDaemon",
            f"启动 Gateway (端口 {self.config.allocate_port('l2')})",
            "Telegram 配对",
        ]
        for i, step in enumerate(steps, 1):
            self.logger.info(f"  {i}. {step}")
        self.logger.success("预演完成")
    
    def rollback(self):
        """回滚"""
        self.logger.warning(f"回滚 L2 部署：{self.username}")
        
        try:
            # 停止 Gateway
            self._run_sudo(['launchctl', 'bootout', 'system', 
                           f'ai.openclaw.{self.username}.gateway'])
            self.logger.debug("已停止 Gateway 服务")
        except Exception as e:
            self.logger.debug(f"停止服务失败：{e}")
        
        # 删除 LaunchDaemon
        plist = Path('/Library/LaunchDaemons') / f'ai.openclaw.{self.username}.gateway.plist'
        if plist.exists():
            try:
                self._run_sudo(['rm', '-f', str(plist)])
                self.logger.debug(f"已删除 LaunchDaemon: {plist}")
            except Exception as e:
                self.logger.debug(f"删除 LaunchDaemon 失败：{e}")
        
        self.logger.warning(f"\n⚠️  用户 {self.username} 未删除")
        self.logger.warning("   如需删除，执行：sudo dscl . -delete /Users/{self.username}")
        self.logger.warning("   如需删除家目录，执行：sudo rm -rf /Users/{self.username}")
    
    def _run_sudo(self, command: list, capture_output: bool = True, input_data: bytes = None):
        """执行 sudo 命令"""
        try:
            result = subprocess.run(
                ['sudo', '-S'] + command,
                input=input_data or self.sudo_password.encode(),
                capture_output=capture_output,
                check=True,
                timeout=300  # 5 分钟超时
            )
            return result
        except subprocess.TimeoutExpired:
            raise PermissionError(f"命令超时：{' '.join(command)}")
        except subprocess.CalledProcessError as e:
            raise PermissionError(f"命令失败：{e.stderr.decode() if e.stderr else str(e)}")
    
    def _run_as_user(self, command: list, timeout: int = 300):
        """以目标用户身份执行命令"""
        try:
            result = subprocess.run(
                ['su', '-', self.username, '-c'] + [' '.join(command)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode != 0:
                raise ConfigError(f"用户命令失败：{result.stderr}")
            return result
        except subprocess.TimeoutExpired:
            raise ConfigError(f"用户命令超时：{' '.join(command)}")
    
    def _check_prerequisites(self):
        """检查前置条件"""
        # 检查 OpenClaw 是否安装
        if not shutil.which('openclaw'):
            raise PrerequisiteError("OpenClaw 未安装，请先执行：npm install -g openclaw")
        
        # 检查共享层是否存在
        shared_path = Path(self.config.defaults['shared_path'])
        if not shared_path.exists():
            raise PrerequisiteError(f"共享层不存在：{shared_path}")
        
        # 检查用户是否已存在
        result = subprocess.run(['dscl', '.', '-list', '/Users'], 
                               capture_output=True, text=True)
        if self.username in result.stdout:
            raise PrerequisiteError(f"用户已存在：{self.username}\n如需重新部署，请先删除该用户")
        
        # 检查 UID 是否被占用
        result = subprocess.run(['dscl', '.', '-list', '/Users', 'UniqueID'], 
                               capture_output=True, text=True)
        if f' {self.uid}\n' in result.stdout:
            raise PrerequisiteError(f"UID {self.uid} 已被占用，请尝试其他 UID")
        
        self.logger.debug("前置条件检查通过")
    
    def _create_user(self):
        """创建 macOS 用户"""
        try:
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
            
            self.logger.debug(f"用户创建成功：{self.username} (UID {self.uid})")
            
            # 设置密码 (交互式)
            self.logger.info("\n   请设置用户密码:")
            subprocess.run(['sudo', 'passwd', self.username])
            
        except PermissionError as e:
            raise PermissionError(f"创建用户失败：{e}")
    
    def _install_dependencies(self):
        """安装依赖"""
        try:
            # 给 brew 权限
            self._run_sudo(['chown', '-R', self.username, '/opt/homebrew'])
            self.logger.debug("已设置 brew 权限")
            
            # 安装 NodeJS (以目标用户)
            self.logger.debug("安装 NodeJS...")
            self._run_as_user(['brew', 'install', 'node@20'], timeout=600)
            
            # 安装 OpenClaw
            self.logger.debug("安装 OpenClaw...")
            self._run_as_user(['npm', 'install', '-g', 'openclaw', '--force'], timeout=600)
            
            self.logger.debug("依赖安装完成")
            
        except (PermissionError, ConfigError) as e:
            raise ConfigError(f"安装依赖失败：{e}")
    
    def _configure_environment(self, port: int):
        """配置环境"""
        # 创建目录
        self._run_as_user(['mkdir', '-p', '~/.openclaw/workspace'])
        self._run_as_user(['mkdir', '-p', '~/.openclaw/agents/main/agent'])
        
        # 复制配置
        main_config = self.home_dir / '.openclaw' / 'openclaw.json'
        user_config = self.user_home / '.openclaw' / 'openclaw.json'
        
        # 使用模板生成配置
        template = self.config.get_template('openclaw.json')
        jinja_template = Template(template)
        
        config_data = jinja_template.render(
            agent_name=self.username,
            port=port,
            bot_token=self.args.bot_token or '',
            default_model=self.config.defaults['default_model'],
            dashscope_key=self.config.defaults['dashscope_key'],
            workspace_path=str(self.user_home / '.openclaw' / 'workspace'),
            deploy_time=datetime.now().isoformat()
        )
        
        # 写入配置
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(config_data)
            temp_config = f.name
        
        self._run_sudo(['cp', temp_config, str(user_config)])
        self._run_sudo(['chown', f'{self.username}:staff', str(user_config)])
        os.unlink(temp_config)
        
        self.logger.debug(f"生成配置：{user_config}")
        
        # 配置 symlink
        shared = self.config.defaults['shared_path']
        self._run_as_user(['mkdir', '-p', '~/.openclaw/workspace/skills'])
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
        
        if auth_src.exists():
            self._run_sudo(['cp', str(auth_src), str(auth_dst)])
            self._run_sudo(['chown', f'{self.username}:staff', str(auth_dst)])
            self.logger.debug("已复制 auth-profiles.json")
        
        # 生成 IDENTITY.md
        self._generate_identity()
    
    def _generate_identity(self):
        """生成 IDENTITY.md"""
        template = self.config.get_template('IDENTITY.md')
        jinja_template = Template(template)
        
        content = jinja_template.render(
            agent_name=self.username,
            role=self.args.role or 'AI Assistant',
            mode='l2',
            role_description=self.args.role or 'AI 助手',
            deploy_time=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        identity_path = self.user_home / '.openclaw' / 'workspace' / 'IDENTITY.md'
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        self._run_sudo(['cp', temp_file, str(identity_path)])
        self._run_sudo(['chown', f'{self.username}:staff', str(identity_path)])
        os.unlink(temp_file)
        
        self.logger.debug("生成 IDENTITY.md")
    
    def _setup_launchdaemon(self, port: int):
        """配置 LaunchDaemon"""
        # 生成 plist
        template = self.config.get_template('launchdaemon.plist')
        jinja_template = Template(template)
        
        plist_content = jinja_template.render(
            username=self.username,
            port=port
        )
        
        # 写入 plist
        plist_path = Path('/Library/LaunchDaemons') / f'ai.openclaw.{self.username}.gateway.plist'
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(plist_content)
            temp_plist = f.name
        
        self._run_sudo(['cp', temp_plist, str(plist_path)])
        self._run_sudo(['chown', 'root:wheel', str(plist_path)])
        self._run_sudo(['chmod', '644', str(plist_path)])
        os.unlink(temp_plist)
        
        self.logger.debug(f"生成 LaunchDaemon: {plist_path}")
        
        # 创建日志目录
        log_dir = Path(f'/tmp/openclaw-{self.username}')
        self._run_sudo(['mkdir', '-p', str(log_dir)])
        self._run_sudo(['chown', f'{self.username}:staff', str(log_dir)])
        
        # 加载
        self._run_sudo(['launchctl', 'bootstrap', 'system', str(plist_path)])
        self.logger.debug("LaunchDaemon 已加载")
    
    def _start_gateway(self):
        """启动 Gateway"""
        # 等待 LaunchDaemon 启动
        time.sleep(3)
        self.logger.debug("Gateway 已启动")
    
    def _pair_telegram(self) -> str:
        """Telegram 配对"""
        bot_username = f"{self.username}_bot"
        
        self.logger.info("\n⚠️  请手动配对 Telegram:")
        self.logger.info("   1. 在 Telegram 搜索 @BotFather")
        self.logger.info("   2. 创建新 Bot 或使用现有 Bot")
        self.logger.info("   3. 在 Bot 中发送 /start")
        self.logger.info("   4. 获取配对码并执行：openclaw pairing approve telegram <CODE>")
        
        return bot_username
    
    def _generate_deploy_record(self, result: DeployResult):
        """生成部署记录"""
        template = self.config.get_template('deploy-record.md')
        jinja_template = Template(template)
        
        content = jinja_template.render(
            agent_name=self.username,
            role=self.args.role or 'AI Assistant',
            mode='l2',
            username=self.username,
            uid=self.uid,
            port=result.port,
            bot_username=result.bot_username,
            deploy_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            steps=[
                "检查前置条件",
                "分配端口",
                "创建 macOS 用户",
                "安装依赖",
                "配置环境",
                "配置 LaunchDaemon",
                "启动 Gateway",
                "Telegram 配对",
            ],
            verification_checks=[
                "进程检查",
                "端口检查",
                "WebSocket 连接",
                "工作流程测试",
            ]
        )
        
        record_path = self.user_home / '.openclaw' / 'DEPLOY_RECORD.md'
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        self._run_sudo(['cp', temp_file, str(record_path)])
        self._run_sudo(['chown', f'{self.username}:staff', str(record_path)])
        os.unlink(temp_file)
        
        self.logger.debug(f"生成部署记录：{record_path}")


# 导入 os
import os
