#!/usr/bin/env python3
"""
L1 Profile 模式部署器 (增强版)
"""

import subprocess
import shutil
import json
import os
from pathlib import Path
from datetime import datetime
from jinja2 import Template

from config import ConfigManager, DeployResult, VerifyReport, VerifyCheck
from logger import DeployLogger
from exceptions import PrerequisiteError, ConfigError, PermissionError


class L1Deployer:
    """L1 Profile 模式部署器"""
    
    def __init__(self, config: ConfigManager, args, sudo_password: str):
        self.config = config
        self.args = args
        self.sudo_password = sudo_password
        self.profile_name = args.name
        self.home_dir = Path.home()
        self.profile_dir = self.home_dir / f'.openclaw-{self.profile_name}'
        self.logs_dir = self.home_dir / '.openclaw' / 'deploy-logs'
        
        # 初始化日志
        self.logger = DeployLogger(self.logs_dir, self.profile_name, 'l1')
        
    def run(self):
        """执行部署"""
        result = DeployResult(success=True, mode='l1', agent_name=self.profile_name)
        
        try:
            self.logger.info(f"🚀 开始部署 {self.profile_name} (L1 模式)")
            self.logger.debug(f"Profile 目录：{self.profile_dir}")
            self.logger.debug(f"日志目录：{self.logs_dir}")
            
            # 1. 检查前置条件
            self.logger.step_start(1, 7, "检查前置条件")
            try:
                self._check_prerequisites()
                self.logger.step_complete(1, 7, "检查前置条件")
            except PrerequisiteError as e:
                self.logger.step_failed(1, 7, "检查前置条件", str(e))
                raise
            
            # 2. 分配端口
            self.logger.step_start(2, 7, "分配端口")
            result.port = self.config.allocate_port('l1')
            self.logger.debug(f"分配端口：{result.port}")
            self.logger.step_complete(2, 7, "分配端口")
            
            # 3. 创建 Profile 目录
            self.logger.step_start(3, 7, "创建 Profile 目录")
            self._create_profile_dir()
            self.logger.step_complete(3, 7, "创建 Profile 目录")
            
            # 4. 生成配置文件
            self.logger.step_start(4, 7, "生成配置文件")
            self._generate_config(result.port)
            self.logger.step_complete(4, 7, "生成配置文件")
            
            # 5. 配置共享层 symlink
            self.logger.step_start(5, 7, "配置共享层")
            self._setup_symlinks()
            self.logger.step_complete(5, 7, "配置共享层")
            
            # 6. 启动 Gateway
            self.logger.step_start(6, 7, "启动 Gateway")
            self._start_gateway(result.port)
            result.gateway_running = True
            self.logger.step_complete(6, 7, "启动 Gateway")
            
            # 7. Telegram 配对
            self.logger.step_start(7, 7, "Telegram 配对")
            result.bot_username = self._pair_telegram()
            self.logger.step_complete(7, 7, "Telegram 配对")
            
            # 注册 Agent
            self.config.register_agent(self.profile_name, 'l1', result.port)
            
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
            f"分配端口 (预计：{self.config.allocate_port('l1')})",
            f"创建目录：~/.openclaw-{self.profile_name}",
            "生成配置文件 (openclaw.json, IDENTITY.md)",
            "配置共享层 symlink",
            "启动 Gateway",
            "Telegram 配对",
        ]
        for i, step in enumerate(steps, 1):
            self.logger.info(f"  {i}. {step}")
        self.logger.success("预演完成")
    
    def rollback(self):
        """回滚"""
        self.logger.warning(f"回滚 L1 部署：{self.profile_name}")
        
        # 停止 Gateway
        try:
            subprocess.run(['pkill', '-f', f'openclaw.*{self.profile_name}'], 
                          capture_output=True)
            self.logger.debug("已停止 Gateway 进程")
        except Exception as e:
            self.logger.debug(f"停止进程失败：{e}")
        
        # 删除 Profile 目录
        if self.profile_dir.exists():
            shutil.rmtree(self.profile_dir)
            self.logger.success(f"已删除 {self.profile_dir}")
    
    def _check_prerequisites(self):
        """检查前置条件"""
        # 检查 OpenClaw 是否安装
        if not shutil.which('openclaw'):
            raise PrerequisiteError("OpenClaw 未安装，请先执行：npm install -g openclaw")
        
        # 检查共享层是否存在
        shared_path = Path(self.config.defaults['shared_path'])
        if not shared_path.exists():
            raise PrerequisiteError(f"共享层不存在：{shared_path}")
        
        # 检查 Profile 是否已存在
        if self.profile_dir.exists():
            raise PrerequisiteError(f"Profile 已存在：{self.profile_dir}\n如需重新部署，请先删除该目录")
        
        self.logger.debug("前置条件检查通过")
    
    def _create_profile_dir(self):
        """创建 Profile 目录"""
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        (self.profile_dir / 'workspace').mkdir(exist_ok=True)
        (self.profile_dir / 'workspace' / 'skills').mkdir(exist_ok=True)
        self.logger.debug(f"创建目录：{self.profile_dir}")
    
    def _generate_config(self, port: int):
        """生成配置文件"""
        # 使用模板生成 openclaw.json
        template = self.config.get_template('openclaw.json')
        jinja_template = Template(template)
        
        config_data = jinja_template.render(
            agent_name=self.profile_name,
            port=port,
            bot_token=self.args.bot_token or '',
            default_model=self.config.defaults['default_model'],
            dashscope_key=self.config.defaults['dashscope_key'],
            workspace_path=str(self.profile_dir / 'workspace'),
            deploy_time=datetime.now().isoformat()
        )
        
        config_path = self.profile_dir / 'openclaw.json'
        with open(config_path, 'w') as f:
            f.write(config_data)
        
        self.logger.debug(f"生成配置：{config_path}")
        
        # 复制核心文档
        core_docs = ['AGENTS.md', 'TOOLS.md']
        for doc in core_docs:
            src = self.home_dir / '.openclaw' / 'workspace' / doc
            dst = self.profile_dir / 'workspace' / doc
            if src.exists():
                shutil.copy(src, dst)
                self.logger.debug(f"复制文档：{doc}")
        
        # 生成 IDENTITY.md
        self._generate_identity()
    
    def _generate_identity(self):
        """生成 IDENTITY.md"""
        template = self.config.get_template('IDENTITY.md')
        jinja_template = Template(template)
        
        content = jinja_template.render(
            agent_name=self.profile_name,
            role=self.args.role or 'AI Assistant',
            mode='l1',
            role_description=self.args.role or 'AI 助手',
            deploy_time=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        identity_path = self.profile_dir / 'workspace' / 'IDENTITY.md'
        with open(identity_path, 'w') as f:
            f.write(content)
        
        self.logger.debug(f"生成 IDENTITY.md")
    
    def _setup_symlinks(self):
        """配置共享层 symlink"""
        shared = Path(self.config.defaults['shared_path'])
        workspace = self.profile_dir / 'workspace'
        
        symlinks = [
            ('skills/summarize', 'skills/summarize'),
            ('skills/meeting-notes', 'skills/meeting-notes'),
            ('skills/domain-model-extract', 'skills/domain-model-extract'),
            ('protocols', 'protocols'),
            ('knowledge', 'knowledge'),
        ]
        
        for src, dst in symlinks:
            src_path = shared / src
            dst_path = workspace / dst
            
            if src_path.exists():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                if dst_path.exists() or dst_path.is_symlink():
                    dst_path.unlink()
                dst_path.symlink_to(src_path)
                self.logger.debug(f"创建 symlink: {dst} → {src_path}")
    
    def _start_gateway(self, port: int):
        """启动 Gateway"""
        # 设置环境变量
        env = {**os.environ, 'OPENCLAW_CONFIG': str(self.profile_dir)}
        
        # 启动 Gateway
        subprocess.Popen(
            ['openclaw', 'gateway', '--port', str(port)],
            env=env,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # 等待启动
        import time
        time.sleep(3)
        
        self.logger.debug(f"Gateway 已启动 (端口 {port})")
    
    def _pair_telegram(self) -> str:
        """Telegram 配对"""
        bot_username = f"{self.profile_name}_bot"
        
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
            agent_name=self.profile_name,
            role=self.args.role or 'AI Assistant',
            mode='l1',
            port=result.port,
            bot_username=result.bot_username,
            deploy_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            steps=[
                "检查前置条件",
                "分配端口",
                "创建 Profile 目录",
                "生成配置文件",
                "配置共享层",
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
        
        record_path = self.profile_dir / 'DEPLOY_RECORD.md'
        with open(record_path, 'w') as f:
            f.write(content)
        
        self.logger.debug(f"生成部署记录：{record_path}")
