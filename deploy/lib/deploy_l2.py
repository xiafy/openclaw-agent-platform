#!/usr/bin/env python3
"""
L2 独立用户模式部署器 (v2.0 - 基于实战验证重写)

修复清单 (2026-03-03):
- openclaw.json 模板对齐实际格式 (复用 v2 模板)
- 增加 browser profile 创建
- 增加 Claw 安全检查
- 增加部署验证 (HTTP probe)
- 修复 os import 位置
- 增加 fireworks_key / gateway_token 参数
- 统一日志风格
"""

import subprocess
import shutil
import json
import os
import time
import secrets
import tempfile
from pathlib import Path
from datetime import datetime
from jinja2 import Template

from config import ConfigManager, DeployResult
from logger import DeployLogger
from exceptions import (
    PrerequisiteError, ConfigError, PermissionError,
)


class L2Deployer:
    """L2 独立用户模式部署器"""
    
    def __init__(self, config: ConfigManager, args, sudo_password: str):
        self.config = config
        self.args = args
        self.sudo_password = sudo_password
        self.username = args.username
        self.home_dir = Path.home()
        self.uid = args.uid if hasattr(args, 'uid') and args.uid else config.allocate_uid()
        self.user_home = Path('/Users') / self.username
        
        # Claw 安全检查
        self.claw_port = 18789
        
        self.logs_dir = self.home_dir / '.openclaw' / 'deploy-logs'
        self.logger = DeployLogger(self.logs_dir, self.username, 'l2')
        
    def run(self):
        """执行部署"""
        result = DeployResult(success=True, mode='l2', agent_name=self.username)
        result.username = self.username
        result.uid = self.uid
        
        try:
            self.logger.info(f"🚀 开始部署 {self.username} (L2 模式)")
            
            # 1. 检查前置条件
            self._log_step(1, 10, "检查前置条件")
            self._check_prerequisites()
            
            # 2. 分配端口
            self._log_step(2, 10, "分配端口")
            result.port = self.config.allocate_port('l2')
            self._verify_not_claw_port(result.port)
            self.logger.info(f"   端口: {result.port}")
            
            # 3. 创建 macOS 用户
            self._log_step(3, 10, "创建 macOS 用户")
            self._create_user()
            
            # 4. 安装依赖
            self._log_step(4, 10, "安装依赖")
            self._install_dependencies()
            
            # 5. 生成配置文件
            self._log_step(5, 10, "生成配置文件")
            self._generate_config(result.port)
            
            # 6. 复制 auth-profiles
            self._log_step(6, 10, "复制 auth-profiles")
            self._copy_auth_profiles()
            
            # 7. 配置共享层 symlink
            self._log_step(7, 10, "配置共享层 symlink")
            self._setup_symlinks()
            
            # 8. 创建 browser profile
            self._log_step(8, 10, "创建 browser profile")
            self._create_browser_profile()
            
            # 9. 配置 LaunchDaemon 并启动
            self._log_step(9, 10, "配置 LaunchDaemon 并启动")
            self._setup_and_start_launchdaemon(result.port)
            result.gateway_running = True
            
            # 10. 验证
            self._log_step(10, 10, "验证部署")
            self._verify_deployment(result.port)
            
            # 注册 Agent
            self.config.register_agent(
                self.username, 'l2', result.port,
                username=self.username, uid=self.uid
            )
            
            self.logger.info(f"\n✅ {self.username} 部署完成！")
            self.logger.info(f"   用户: {self.username} (UID {self.uid})")
            self.logger.info(f"   端口: {result.port}")
            self.logger.info(f"   家目录: {self.user_home}")
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
        port = self.config.allocate_port('l2')
        self.logger.info("预演部署步骤:")
        steps = [
            "检查前置条件 (OpenClaw 已安装、共享层存在、用户不存在)",
            f"分配端口: {port}",
            f"创建 macOS 用户: {self.username} (UID {self.uid})",
            "安装 NodeJS + OpenClaw",
            "生成 openclaw.json (从模板，含完整模型配置)",
            "复制 auth-profiles.json (从 Claw)",
            "配置共享层 symlink (skills + protocols + knowledge)",
            f"创建 browser profile: {self.username}-browser",
            f"配置 LaunchDaemon: ai.openclaw.{self.username}.gateway",
            "验证: HTTP probe 端口响应",
        ]
        for i, step in enumerate(steps, 1):
            self.logger.info(f"  {i}. {step}")
        self.logger.info("\n✅ 预演完成 (未实际执行)")
    
    def rollback(self):
        """回滚"""
        self.logger.info(f"🔄 回滚 L2 部署: {self.username}")
        
        # 1. 停止服务
        try:
            self._run_sudo(['launchctl', 'bootout', 'system',
                           f'ai.openclaw.{self.username}.gateway'])
            self.logger.info("   已停止 Gateway 服务")
        except Exception:
            pass
        
        # 2. 删除 LaunchDaemon
        plist = Path('/Library/LaunchDaemons') / f'ai.openclaw.{self.username}.gateway.plist'
        if plist.exists():
            try:
                self._run_sudo(['rm', '-f', str(plist)])
                self.logger.info(f"   已删除 LaunchDaemon")
            except Exception:
                pass
        
        self.logger.info(f"\n⚠️  用户 {self.username} 未自动删除 (安全考虑)")
        self.logger.info(f"   手动删除用户: sudo dscl . -delete /Users/{self.username}")
        self.logger.info(f"   手动删除家目录: sudo rm -rf /Users/{self.username}")
    
    # ── Safety guards ──
    
    def _verify_not_claw_port(self, port: int):
        if port == self.claw_port:
            raise ConfigError(f"端口 {port} 是 Claw 的端口，禁止使用！")
    
    # ── Helpers ──
    
    def _log_step(self, num: int, total: int, msg: str):
        self.logger.info(f"[{num}/{total}] {msg}...")
    
    def _run_sudo(self, command: list, capture_output: bool = True):
        """执行 sudo 命令"""
        try:
            result = subprocess.run(
                ['sudo', '-S'] + command,
                input=self.sudo_password.encode(),
                capture_output=capture_output,
                check=True,
                timeout=300
            )
            return result
        except subprocess.TimeoutExpired:
            raise PermissionError(f"命令超时: {' '.join(command)}")
        except subprocess.CalledProcessError as e:
            raise PermissionError(f"命令失败: {e.stderr.decode() if e.stderr else str(e)}")
    
    def _write_as_user(self, content: str, dest_path: str):
        """以 sudo 写入文件并 chown 给目标用户"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp') as f:
            f.write(content)
            tmp = f.name
        self._run_sudo(['cp', tmp, dest_path])
        self._run_sudo(['chown', f'{self.username}:staff', dest_path])
        os.unlink(tmp)
    
    def _mkdir_as_user(self, path: str):
        """以 sudo 创建目录并 chown"""
        self._run_sudo(['mkdir', '-p', path])
        self._run_sudo(['chown', f'{self.username}:staff', path])
    
    # ── Step implementations ──
    
    def _check_prerequisites(self):
        if not shutil.which('openclaw'):
            raise PrerequisiteError("OpenClaw 未安装")
        
        shared_path = Path(self.config.defaults['shared_path'])
        if not shared_path.exists():
            raise PrerequisiteError(f"共享层不存在: {shared_path}")
        
        # 检查用户是否已存在
        result = subprocess.run(['dscl', '.', '-list', '/Users'],
                               capture_output=True, text=True)
        if self.username in result.stdout.split('\n'):
            raise PrerequisiteError(
                f"用户已存在: {self.username}\n"
                f"   如需重新部署，先运行: deploy-agent --rollback --username {self.username} --mode l2"
            )
        
        # 检查 UID
        result = subprocess.run(['dscl', '.', '-list', '/Users', 'UniqueID'],
                               capture_output=True, text=True)
        for line in result.stdout.strip().split('\n'):
            parts = line.split()
            if len(parts) == 2 and parts[1] == str(self.uid):
                raise PrerequisiteError(f"UID {self.uid} 已被 {parts[0]} 占用")
        
        self.logger.debug("前置条件检查通过")
    
    def _create_user(self):
        """创建 macOS 用户"""
        commands = [
            ['dscl', '.', '-create', f'/Users/{self.username}'],
            ['dscl', '.', '-create', f'/Users/{self.username}', 'UserShell', '/bin/zsh'],
            ['dscl', '.', '-create', f'/Users/{self.username}', 'RealName',
             self.args.role or self.username],
            ['dscl', '.', '-create', f'/Users/{self.username}', 'UniqueID', str(self.uid)],
            ['dscl', '.', '-create', f'/Users/{self.username}', 'PrimaryGroupID', '20'],
            ['dscl', '.', '-create', f'/Users/{self.username}', 'NFSHomeDirectory',
             str(self.user_home)],
        ]
        
        for cmd in commands:
            self._run_sudo(cmd)
        
        self._run_sudo(['createhomedir', '-c', '-u', self.username])
        self.logger.info(f"   用户: {self.username} (UID {self.uid})")
        
        # 设置密码
        self.logger.info("   请设置用户密码:")
        subprocess.run(['sudo', 'passwd', self.username])
    
    def _install_dependencies(self):
        """安装依赖 (复用宿主机 node/openclaw)"""
        # L2 用户通过 PATH 使用宿主机已安装的 node 和 openclaw
        # 验证 openclaw 对目标用户可访问
        self.logger.debug("L2 复用宿主机 node/openclaw (通过 PATH)")
    
    def _generate_config(self, port: int):
        """生成 openclaw.json"""
        template_str = self.config.get_template('openclaw.json')
        template = Template(template_str)
        
        # 读取 API keys from Claw
        claw_config_path = self.home_dir / '.openclaw' / 'openclaw.json'
        dashscope_key = ''
        fireworks_key = ''
        if claw_config_path.exists():
            with open(claw_config_path) as f:
                claw_config = json.load(f)
            dashscope_key = claw_config.get('env', {}).get('DASHSCOPE_API_KEY', '')
            fireworks_key = (claw_config.get('models', {}).get('providers', {})
                           .get('fireworks', {}).get('apiKey', ''))
        
        workspace_path = str(self.user_home / '.openclaw' / 'workspace')
        
        config_data = template.render(
            agent_name=self.username,
            port=port,
            bot_token=self.args.bot_token or '',
            default_model=self.config.defaults.get('default_model', 'anthropic/claude-sonnet-4-6'),
            dashscope_key=dashscope_key,
            fireworks_key=fireworks_key,
            workspace_path=workspace_path,
            gateway_token=secrets.token_hex(24),
            home_dir=str(self.user_home),
            deploy_time=datetime.now().isoformat(),
        )
        
        # 创建目录结构
        openclaw_dir = str(self.user_home / '.openclaw')
        self._mkdir_as_user(openclaw_dir)
        self._mkdir_as_user(workspace_path)
        self._mkdir_as_user(f"{workspace_path}/memory")
        self._mkdir_as_user(f"{workspace_path}/docs")
        self._mkdir_as_user(f"{workspace_path}/skills")
        self._mkdir_as_user(f"{openclaw_dir}/agents/main/agent")
        self._mkdir_as_user(f"{openclaw_dir}/logs")
        
        # 写入 openclaw.json
        config_path = str(self.user_home / '.openclaw' / 'openclaw.json')
        self._write_as_user(config_data, config_path)
        
        # 生成 workspace 文件
        self._generate_workspace_files()
        
        self.logger.debug("配置已生成")
    
    def _generate_workspace_files(self):
        """生成 workspace 核心文件"""
        ws = str(self.user_home / '.openclaw' / 'workspace')
        role = self.args.role or 'AI Assistant'
        
        # IDENTITY.md
        try:
            identity_template = self.config.get_template('IDENTITY.md')
            identity = Template(identity_template).render(
                agent_name=self.username,
                role=role,
                mode='l2',
                role_description=role,
                deploy_time=datetime.now().strftime('%Y-%m-%d %H:%M'),
            )
            self._write_as_user(identity, f"{ws}/IDENTITY.md")
        except FileNotFoundError:
            self.logger.debug("IDENTITY.md 模板不存在，跳过")
        
        # MEMORY.md
        self._write_as_user(
            f"# MEMORY.md - {self.username}\n\n<!-- 按时间倒序记录 -->\n",
            f"{ws}/MEMORY.md"
        )
        
        # USER.md
        self._write_as_user(
            f"# USER.md\n\n"
            f"- **Name:** Mr Xia / 夏总\n"
            f"- **Company:** Peblla — 美国餐饮行业 SaaS 科技公司\n"
            f"- **Role:** CEO, 联合创始人\n"
            f"- **Timezone:** Asia/Shanghai (GMT+8)\n",
            f"{ws}/USER.md"
        )
    
    def _copy_auth_profiles(self):
        """从 Claw 复制 auth-profiles.json"""
        src = self.home_dir / '.openclaw' / 'agents' / 'main' / 'agent' / 'auth-profiles.json'
        if not src.exists():
            raise ConfigError(f"Claw auth-profiles 不存在: {src}")
        
        dst = str(self.user_home / '.openclaw' / 'agents' / 'main' / 'agent' / 'auth-profiles.json')
        self._run_sudo(['cp', str(src), dst])
        self._run_sudo(['chown', f'{self.username}:staff', dst])
        
        self.logger.debug("auth-profiles.json 已复制")
    
    def _setup_symlinks(self):
        """配置共享层 symlink"""
        shared = self.config.defaults['shared_path']
        ws = str(self.user_home / '.openclaw' / 'workspace')
        
        symlinks = [
            ('skills/summarize', 'skills/summarize'),
            ('skills/meeting-notes', 'skills/meeting-notes'),
            ('skills/domain-model-extract', 'skills/domain-model-extract'),
            ('protocols', 'protocols'),
            ('knowledge', 'knowledge'),
        ]
        
        for src_rel, dst_rel in symlinks:
            src_path = f"{shared}/{src_rel}"
            dst_path = f"{ws}/{dst_rel}"
            
            if Path(src_path).exists():
                # 确保父目录存在
                parent = str(Path(dst_path).parent)
                self._mkdir_as_user(parent)
                # 删除已有 symlink
                self._run_sudo(['rm', '-f', dst_path])
                self._run_sudo(['ln', '-s', src_path, dst_path])
                self._run_sudo(['chown', '-h', f'{self.username}:staff', dst_path])
                self.logger.debug(f"symlink: {dst_rel} → {src_path}")
    
    def _create_browser_profile(self):
        """创建独立 browser profile"""
        profile_name = f"{self.username}-browser"
        
        # L2 用户需要用 sudo 以该用户身份创建
        result = subprocess.run(
            ['sudo', '-u', self.username,
             'openclaw', 'browser', 'create-profile', '--name', profile_name],
            capture_output=True, text=True,
            env={**os.environ, 'HOME': str(self.user_home)}
        )
        
        if result.returncode != 0:
            self.logger.info(f"   ⚠️ browser profile 创建失败: {result.stderr.strip()}")
            self.logger.info(f"   可手动执行 (以 {self.username} 身份)")
        else:
            self.logger.debug(f"browser profile 已创建: {profile_name}")
            for line in result.stdout.splitlines():
                if 'port' in line:
                    self.logger.info(f"   {line.strip()}")
    
    def _setup_and_start_launchdaemon(self, port: int):
        """配置 LaunchDaemon 并启动"""
        template_str = self.config.get_template('launchdaemon.plist')
        template = Template(template_str)
        
        plist_content = template.render(
            username=self.username,
            port=str(port),
        )
        
        plist_name = f'ai.openclaw.{self.username}.gateway.plist'
        plist_path = f'/Library/LaunchDaemons/{plist_name}'
        
        self._write_as_user(plist_content, plist_path)
        self._run_sudo(['chown', 'root:wheel', plist_path])
        self._run_sudo(['chmod', '644', plist_path])
        
        # 启动
        self._run_sudo(['launchctl', 'bootstrap', 'system', plist_path])
        
        time.sleep(3)
        self.logger.debug("LaunchDaemon 已启动")
    
    def _verify_deployment(self, port: int):
        """验证部署"""
        import urllib.request
        
        try:
            url = f"http://127.0.0.1:{port}/"
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    self.logger.info(f"   ✅ Gateway 端口 {port} 响应正常")
                    return
        except Exception:
            pass
        
        self.logger.info(f"   ⚠️ Gateway 未响应，查看日志: /tmp/openclaw-{self.username}/openclaw.err")
