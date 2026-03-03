#!/usr/bin/env python3
"""
L1 Profile 模式部署器 (v2.0 - 基于实战验证重写)

修复清单 (2026-03-03):
- openclaw.json 模板对齐实际格式
- 增加 auth-profiles.json 复制
- 增加 browser profile 创建
- 增加 LaunchAgent plist 创建 (替代 Popen)
- 增加 gateway token 自动生成
- 增加 Telegram allowlist
- 使用 --profile 参数启动 gateway
"""

import subprocess
import shutil
import json
import os
import secrets
from pathlib import Path
from datetime import datetime
from jinja2 import Template

from config import ConfigManager, DeployResult, VerifyReport, VerifyCheck
from logger import DeployLogger
from exceptions import PrerequisiteError, ConfigError


class L1Deployer:
    """L1 Profile 模式部署器"""
    
    def __init__(self, config: ConfigManager, args, sudo_password: str = None):
        self.config = config
        self.args = args
        self.sudo_password = sudo_password
        self.profile_name = args.name
        self.home_dir = Path.home()
        self.profile_dir = self.home_dir / f'.openclaw-{self.profile_name}'
        self.workspace_dir = self.home_dir / '.openclaw' / f'workspace-{self.profile_name}'
        self.logs_dir = self.home_dir / '.openclaw' / 'deploy-logs'
        
        # Claw 的关键路径 — 绝对不能碰
        self.claw_config_dir = self.home_dir / '.openclaw'
        self.claw_port = 18789
        
        self.logger = DeployLogger(self.logs_dir, self.profile_name, 'l1')
        
    def run(self):
        """执行部署"""
        result = DeployResult(success=True, mode='l1', agent_name=self.profile_name)
        
        try:
            self.logger.info(f"🚀 开始部署 {self.profile_name} (L1 模式)")
            
            # 1. 检查前置条件
            self._log_step(1, 9, "检查前置条件")
            self._check_prerequisites()
            
            # 2. 分配端口
            self._log_step(2, 9, "分配端口")
            result.port = self.config.allocate_port('l1')
            self._verify_not_claw_port(result.port)
            self.logger.info(f"   端口: {result.port}")
            
            # 3. 创建目录结构
            self._log_step(3, 9, "创建目录结构")
            self._create_directories()
            
            # 4. 生成配置文件
            self._log_step(4, 9, "生成 openclaw.json")
            self._generate_config(result.port)
            
            # 5. 复制 auth-profiles
            self._log_step(5, 9, "复制 auth-profiles")
            self._copy_auth_profiles()
            
            # 6. 配置共享层 symlink
            self._log_step(6, 9, "配置共享层 symlink")
            self._setup_symlinks()
            
            # 7. 创建 browser profile
            self._log_step(7, 9, "创建 browser profile")
            self._create_browser_profile()
            
            # 8. 创建 LaunchAgent 并启动
            self._log_step(8, 9, "创建 LaunchAgent 并启动 Gateway")
            self._create_and_start_launchagent(result.port)
            result.gateway_running = True
            
            # 9. 验证
            self._log_step(9, 9, "验证部署")
            self._verify_deployment(result.port)
            
            # 注册 Agent
            self.config.register_agent(self.profile_name, 'l1', result.port)
            
            self.logger.info(f"\n✅ {self.profile_name} 部署完成！")
            self.logger.info(f"   端口: {result.port}")
            self.logger.info(f"   配置: {self.profile_dir}/openclaw.json")
            self.logger.info(f"   工作区: {self.workspace_dir}")
            self.logger.info(f"   日志: {self.logger.get_log_path()}")
            self.logger.info(f"\n📱 在 Telegram 给 Bot 发 /start 开始配对")
            
        except Exception as e:
            result.success = False
            result.error = str(e)
            self.logger.info(f"\n❌ 部署失败: {e}")
            self.logger.info(f"   日志: {self.logger.get_log_path()}")
            raise
        
        return result
    
    def dry_run(self):
        """预演模式"""
        port = self.config.allocate_port('l1')
        self.logger.info("预演部署步骤:")
        steps = [
            "检查前置条件 (OpenClaw 已安装、共享层存在、Profile 不存在)",
            f"分配端口: {port}",
            f"创建目录: {self.profile_dir} + {self.workspace_dir}",
            "生成 openclaw.json (从模板，含完整模型配置)",
            f"复制 auth-profiles.json (从 Claw)",
            "配置共享层 symlink (skills + protocols + knowledge)",
            f"创建 browser profile: {self.profile_name}-browser",
            f"创建 LaunchAgent: ai.openclaw.gateway.{self.profile_name}",
            "验证: HTTP probe 端口响应",
        ]
        for i, step in enumerate(steps, 1):
            self.logger.info(f"  {i}. {step}")
        self.logger.info("\n✅ 预演完成 (未实际执行)")
    
    def rollback(self):
        """回滚"""
        self.logger.info(f"🔄 回滚 L1 部署: {self.profile_name}")
        
        # 1. 停止并卸载 LaunchAgent
        plist_path = self.home_dir / 'Library' / 'LaunchAgents' / f'ai.openclaw.gateway.{self.profile_name}.plist'
        if plist_path.exists():
            subprocess.run(['launchctl', 'unload', str(plist_path)], capture_output=True)
            plist_path.unlink()
            self.logger.info("   已卸载 LaunchAgent")
        
        # 2. 杀残留进程
        subprocess.run(
            ['pkill', '-f', f'--profile {self.profile_name} gateway'],
            capture_output=True
        )
        
        # 3. 删除 Profile 目录
        if self.profile_dir.exists():
            shutil.rmtree(self.profile_dir)
            self.logger.info(f"   已删除 {self.profile_dir}")
        
        # 4. 删除 workspace
        if self.workspace_dir.exists():
            shutil.rmtree(self.workspace_dir)
            self.logger.info(f"   已删除 {self.workspace_dir}")
        
        self.logger.info("✅ 回滚完成")
    
    # ── Safety guards ──
    
    def _verify_not_claw_port(self, port: int):
        """确保不会操作 Claw 的端口"""
        if port == self.claw_port:
            raise ConfigError(f"端口 {port} 是 Claw 的端口，禁止使用！")
    
    def _verify_not_claw_service(self, plist_name: str):
        """确保不会操作 Claw 的 LaunchAgent"""
        if plist_name == 'ai.openclaw.gateway.plist':
            raise ConfigError("禁止操作 Claw 的 LaunchAgent！")
    
    # ── Step implementations ──
    
    def _log_step(self, num: int, total: int, msg: str):
        self.logger.info(f"[{num}/{total}] {msg}...")
    
    def _check_prerequisites(self):
        if not shutil.which('openclaw'):
            raise PrerequisiteError("OpenClaw 未安装")
        
        shared_path = Path(self.config.defaults['shared_path'])
        if not shared_path.exists():
            raise PrerequisiteError(f"共享层不存在: {shared_path}")
        
        if self.profile_dir.exists():
            raise PrerequisiteError(
                f"Profile 已存在: {self.profile_dir}\n"
                f"   如需重新部署，先运行: deploy-agent --rollback --name {self.profile_name} --mode l1"
            )
        
        self.logger.debug("前置条件检查通过")
    
    def _create_directories(self):
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        (self.profile_dir / 'logs').mkdir(exist_ok=True)
        
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        (self.workspace_dir / 'memory').mkdir(exist_ok=True)
        (self.workspace_dir / 'docs').mkdir(exist_ok=True)
        (self.workspace_dir / 'skills').mkdir(exist_ok=True)
        
        self.logger.debug(f"目录已创建: {self.profile_dir}, {self.workspace_dir}")
    
    def _generate_config(self, port: int):
        template_str = self.config.get_template('openclaw.json')
        template = Template(template_str)
        
        # 读取 API keys
        dashscope_key = self.config.defaults.get('dashscope_key', '')
        if not dashscope_key:
            # 从 Claw 的 config 读取
            claw_config_path = self.claw_config_dir / 'openclaw.json'
            if claw_config_path.exists():
                with open(claw_config_path) as f:
                    claw_config = json.load(f)
                dashscope_key = claw_config.get('env', {}).get('DASHSCOPE_API_KEY', '')
        
        fireworks_key = self._get_fireworks_key()
        
        config_data = template.render(
            agent_name=self.profile_name,
            port=port,
            bot_token=self.args.bot_token or '',
            default_model=self.config.defaults.get('default_model', 'anthropic/claude-sonnet-4-6'),
            dashscope_key=dashscope_key,
            fireworks_key=fireworks_key,
            workspace_path=str(self.workspace_dir),
            gateway_token=secrets.token_hex(24),
            home_dir=str(self.home_dir),
            deploy_time=datetime.now().isoformat(),
        )
        
        config_path = self.profile_dir / 'openclaw.json'
        with open(config_path, 'w') as f:
            f.write(config_data)
        
        self.logger.debug(f"配置已生成: {config_path}")
        
        # 生成 workspace 核心文件
        self._generate_workspace_files()
    
    def _get_fireworks_key(self) -> str:
        """从 Claw 配置读取 Fireworks API Key"""
        claw_config_path = self.claw_config_dir / 'openclaw.json'
        if claw_config_path.exists():
            with open(claw_config_path) as f:
                claw_config = json.load(f)
            providers = claw_config.get('models', {}).get('providers', {})
            return providers.get('fireworks', {}).get('apiKey', '')
        return ''
    
    def _generate_workspace_files(self):
        """生成 workspace 核心 .md 文件"""
        role = self.args.role or 'AI Assistant'
        
        # IDENTITY.md
        identity_template = self.config.get_template('IDENTITY.md')
        identity = Template(identity_template).render(
            agent_name=self.profile_name,
            role=role,
            mode='l1',
            role_description=role,
            deploy_time=datetime.now().strftime('%Y-%m-%d %H:%M'),
        )
        (self.workspace_dir / 'IDENTITY.md').write_text(identity)
        
        # MEMORY.md (空)
        (self.workspace_dir / 'MEMORY.md').write_text(
            f"# MEMORY.md - {self.profile_name}\n\n<!-- 按时间倒序记录 -->\n"
        )
        
        # USER.md (精简版)
        (self.workspace_dir / 'USER.md').write_text(
            f"# USER.md\n\n"
            f"- **Name:** Mr Xia / 夏总\n"
            f"- **Company:** Peblla — 美国餐饮行业 SaaS 科技公司\n"
            f"- **Role:** CEO, 联合创始人\n"
            f"- **Timezone:** Asia/Shanghai (GMT+8)\n\n"
            f"## 沟通偏好\n"
            f"- 直接、结论优先\n"
            f"- 中文为主，保留必要英文术语\n"
        )
        
        self.logger.debug("Workspace 文件已生成")
    
    def _copy_auth_profiles(self):
        """从 Claw 复制 auth-profiles.json"""
        src = self.claw_config_dir / 'agents' / 'main' / 'agent' / 'auth-profiles.json'
        if not src.exists():
            raise ConfigError(f"Claw auth-profiles 不存在: {src}")
        
        dst_dir = self.profile_dir / 'agents' / 'main' / 'agent'
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst_dir / 'auth-profiles.json')
        
        self.logger.debug(f"auth-profiles.json 已复制")
    
    def _setup_symlinks(self):
        shared = Path(self.config.defaults['shared_path'])
        
        symlinks = [
            ('skills/summarize', 'skills/summarize'),
            ('skills/meeting-notes', 'skills/meeting-notes'),
            ('skills/domain-model-extract', 'skills/domain-model-extract'),
            ('protocols', 'protocols'),
            ('knowledge', 'knowledge'),
        ]
        
        for src_rel, dst_rel in symlinks:
            src_path = shared / src_rel
            dst_path = self.workspace_dir / dst_rel
            
            if src_path.exists():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                if dst_path.exists() or dst_path.is_symlink():
                    dst_path.unlink()
                dst_path.symlink_to(src_path)
                self.logger.debug(f"symlink: {dst_rel} → {src_path}")
            else:
                self.logger.debug(f"跳过 (源不存在): {src_path}")
    
    def _create_browser_profile(self):
        """创建独立 browser profile"""
        profile_name = f"{self.profile_name}-browser"
        
        result = subprocess.run(
            ['openclaw', '--profile', self.profile_name,
             'browser', 'create-profile', '--name', profile_name],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            self.logger.info(f"   ⚠️ browser profile 创建失败: {result.stderr.strip()}")
            self.logger.info(f"   可手动执行: openclaw --profile {self.profile_name} browser create-profile --name {profile_name}")
        else:
            self.logger.debug(f"browser profile 已创建: {profile_name}")
            # 解析端口
            for line in result.stdout.splitlines():
                if 'port' in line:
                    self.logger.info(f"   {line.strip()}")
    
    def _create_and_start_launchagent(self, port: int):
        """创建 LaunchAgent plist 并启动"""
        plist_name = f"ai.openclaw.gateway.{self.profile_name}.plist"
        
        # 安全检查
        self._verify_not_claw_service(plist_name)
        
        template_str = self.config.get_template('launchagent.plist')
        template = Template(template_str)
        
        plist_content = template.render(
            agent_name=self.profile_name,
            port=str(port),
            home_dir=str(self.home_dir),
            profile_dir=str(self.profile_dir),
        )
        
        plist_path = self.home_dir / 'Library' / 'LaunchAgents' / plist_name
        with open(plist_path, 'w') as f:
            f.write(plist_content)
        
        self.logger.debug(f"LaunchAgent 已创建: {plist_path}")
        
        # 加载并启动
        result = subprocess.run(
            ['launchctl', 'load', str(plist_path)],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            raise ConfigError(f"LaunchAgent 加载失败: {result.stderr}")
        
        self.logger.debug("LaunchAgent 已加载")
        
        # 等待启动
        import time
        time.sleep(3)
    
    def _verify_deployment(self, port: int):
        """验证部署是否成功"""
        import urllib.request
        
        try:
            url = f"http://127.0.0.1:{port}/"
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    self.logger.info(f"   ✅ Gateway 端口 {port} 响应正常")
                    return
        except Exception as e:
            pass
        
        # 检查 LaunchAgent 退出码
        result = subprocess.run(
            ['launchctl', 'list'],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if self.profile_name in line:
                self.logger.info(f"   LaunchAgent 状态: {line.strip()}")
        
        self.logger.info(f"   ⚠️ Gateway 未响应，查看日志: {self.profile_dir}/logs/gateway.err.log")
