#!/usr/bin/env python3
"""
L1 Profile 模式部署器
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional
from config import ConfigManager, DeployResult, VerifyReport, VerifyCheck


class L1Deployer:
    """L1 Profile 模式部署器"""
    
    def __init__(self, config: ConfigManager, args, sudo_password: str):
        self.config = config
        self.args = args
        self.sudo_password = sudo_password
        self.profile_name = args.name
        self.home_dir = Path.home()
        self.profile_dir = self.home_dir / f'.openclaw-{self.profile_name}'
        
    def run(self):
        """执行部署"""
        result = DeployResult(success=True, mode='l1', agent_name=self.profile_name)
        
        try:
            # 1. 检查前置条件
            self._print_step(1, 7, "检查前置条件")
            self._check_prerequisites()
            
            # 2. 分配端口
            self._print_step(2, 7, "分配端口")
            result.port = self.config.allocate_port('l1')
            
            # 3. 创建 Profile 目录
            self._print_step(3, 7, "创建 Profile 目录")
            self._create_profile_dir()
            
            # 4. 生成配置文件
            self._print_step(4, 7, "生成配置文件")
            self._generate_config(result.port)
            
            # 5. 配置共享层 symlink
            self._print_step(5, 7, "配置共享层")
            self._setup_symlinks()
            
            # 6. 启动 Gateway
            self._print_step(6, 7, "启动 Gateway")
            self._start_gateway()
            result.gateway_running = True
            
            # 7. Telegram 配对
            self._print_step(7, 7, "Telegram 配对")
            result.bot_username = self._pair_telegram()
            
            # 注册 Agent
            self.config.register_agent(
                self.profile_name, 'l1', result.port
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
        print(f"  2. 分配端口 (预计：{self.config.allocate_port('l1')})")
        print(f"  3. 创建目录：~/.openclaw-{self.profile_name}")
        print(f"  4. 生成配置文件")
        print(f"  5. 配置共享层 symlink")
        print(f"  6. 启动 Gateway")
        print(f"  7. Telegram 配对")
        print(f"\n✅ 预演完成")
    
    def rollback(self):
        """回滚"""
        print(f"🔄 回滚 L1 部署：{self.profile_name}")
        
        # 停止 Gateway
        try:
            subprocess.run(['pkill', '-f', f'openclaw.*{self.profile_name}'], 
                          capture_output=True)
        except:
            pass
        
        # 删除 Profile 目录
        if self.profile_dir.exists():
            shutil.rmtree(self.profile_dir)
            print(f"✅ 已删除 {self.profile_dir}")
    
    def _print_step(self, current: int, total: int, message: str):
        """打印步骤"""
        print(f"[{current}/{total}] {message}... ", end='', flush=True)
    
    def _check_prerequisites(self):
        """检查前置条件"""
        # 检查 OpenClaw 是否安装
        if not shutil.which('openclaw'):
            raise Exception("OpenClaw 未安装")
        
        # 检查共享层是否存在
        shared_path = Path(self.config.defaults['shared_path'])
        if not shared_path.exists():
            raise Exception(f"共享层不存在：{shared_path}")
        
        # 检查 Profile 是否已存在
        if self.profile_dir.exists():
            raise Exception(f"Profile 已存在：{self.profile_dir}")
        
        print("✅")
    
    def _create_profile_dir(self):
        """创建 Profile 目录"""
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        (self.profile_dir / 'workspace').mkdir(exist_ok=True)
        print("✅")
    
    def _generate_config(self, port: int):
        """生成配置文件"""
        # 复制主配置作为模板
        main_config = Path.home() / '.openclaw' / 'openclaw.json'
        if main_config.exists():
            shutil.copy(main_config, self.profile_dir / 'openclaw.json')
        
        # 修改端口
        import json
        config_path = self.profile_dir / 'openclaw.json'
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        config['gateway'] = config.get('gateway', {})
        config['gateway']['port'] = port
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅")
    
    def _setup_symlinks(self):
        """配置共享层 symlink"""
        shared = Path(self.config.defaults['shared_path'])
        workspace = self.profile_dir / 'workspace'
        
        # 创建 symlink
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
        
        print("✅")
    
    def _start_gateway(self):
        """启动 Gateway"""
        # 设置环境变量
        env = {**os.environ, 'OPENCLAW_CONFIG': str(self.profile_dir)}
        
        # 启动 Gateway
        subprocess.Popen(
            ['openclaw', 'gateway', '--port', str(self.config.allocate_port('l1'))],
            env=env,
            start_new_session=True
        )
        
        # 等待启动
        import time
        time.sleep(3)
        
        print("✅")
    
    def _pair_telegram(self) -> str:
        """Telegram 配对"""
        # 这里需要实现自动配对逻辑
        # 简化版本：提示用户手动配对
        print("⚠️  请手动配对 Telegram")
        print("   1. 在 Telegram 搜索 Bot")
        print("   2. 发送 /start")
        print("   3. 获取配对码")
        print("   4. 执行：openclaw pairing approve telegram <CODE>")
        
        # 返回 Bot 用户名 (从配置读取)
        return f"{self.profile_name}_bot"


# 导入 os
import os
