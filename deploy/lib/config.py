#!/usr/bin/env python3
"""
配置管理器
负责端口分配、UID 分配、配置模板等
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / 'config'
        self.ports_file = self.config_dir / 'ports.yaml'
        self.agents_file = self.config_dir / 'agents.yaml'
        self.defaults_file = self.config_dir / 'defaults.yaml'
        
        # 加载配置
        self.ports = self._load_ports()
        self.agents = self._load_agents()
        self.defaults = self._load_defaults()
    
    def _load_yaml(self, file_path: Path) -> Dict:
        """加载 YAML 文件"""
        if file_path.exists():
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _load_ports(self) -> Dict:
        """加载端口配置"""
        default = {
            'allocated': [],
            'next_available': {'l1': 19003, 'l2': 19004},
            'reserved': [18788, 19000]
        }
        return self._load_yaml(self.ports_file) or default
    
    def _load_agents(self) -> Dict:
        """加载 Agent 配置"""
        return self._load_yaml(self.agents_file) or {}
    
    def _load_defaults(self) -> Dict:
        """加载默认配置"""
        default = {
            'default_model': 'anthropic/claude-sonnet-4-6',
            'dashscope_key': '',  # 从环境变量读取
            'shared_path': '/Users/Shared/openclaw-common',
        }
        config = self._load_yaml(self.defaults_file) or {}
        
        # 从环境变量读取敏感信息
        import os
        config['dashscope_key'] = os.environ.get('DASHSCOPE_API_KEY', '')
        
        return {**default, **config}
    
    def allocate_port(self, mode: str) -> int:
        """分配端口"""
        # 获取下一个可用端口
        port = self.ports['next_available'].get(mode, 19003)
        
        # 检查是否被占用
        while self._is_port_allocated(port):
            port += 1
        
        return port
    
    def _is_port_allocated(self, port: int) -> bool:
        """检查端口是否已分配"""
        if port in self.ports.get('reserved', []):
            return True
        
        for agent in self.ports.get('allocated', []):
            if agent.get('port') == port:
                return True
        
        return False
    
    def allocate_uid(self) -> int:
        """分配 UID"""
        # 从 503 开始 (501=xiafybot, 502=shuaishuai)
        uid = 503
        
        # 检查是否被占用
        while self._is_uid_allocated(uid):
            uid += 1
        
        return uid
    
    def _is_uid_allocated(self, uid: int) -> bool:
        """检查 UID 是否已分配"""
        for agent in self.ports.get('allocated', []):
            if agent.get('uid') == uid:
                return True
        
        return False
    
    def register_agent(self, name: str, mode: str, port: int, username: str = None, uid: int = None):
        """注册 Agent"""
        agent_info = {
            'name': name,
            'mode': mode,
            'port': port,
        }
        
        if username:
            agent_info['username'] = username
        if uid:
            agent_info['uid'] = uid
        
        # 添加到已分配列表
        if 'allocated' not in self.ports:
            self.ports['allocated'] = []
        self.ports['allocated'].append(agent_info)
        
        # 更新下一个可用端口
        next_port = port + 1
        while self._is_port_allocated(next_port):
            next_port += 1
        self.ports['next_available'][mode] = next_port
        
        # 保存配置
        self._save_ports()
    
    def _save_ports(self):
        """保存端口配置"""
        with open(self.ports_file, 'w') as f:
            yaml.safe_dump(self.ports, f, default_flow_style=False)
    
    def get_template(self, name: str) -> str:
        """获取配置模板"""
        template_dir = Path(__file__).parent.parent / 'templates'
        template_path = template_dir / f'{name}.j2'
        
        if template_path.exists():
            with open(template_path, 'r') as f:
                return f.read()
        
        raise FileNotFoundError(f"Template not found: {name}")
    
    def list_agents(self) -> List[Dict]:
        """列出已部署的 Agent"""
        return self.ports.get('allocated', [])


class DeployResult:
    """部署结果"""
    
    def __init__(self, success: bool, mode: str, agent_name: str):
        self.success = success
        self.mode = mode
        self.agent_name = agent_name
        self.port = None
        self.username = None
        self.uid = None
        self.bot_username = None
        self.gateway_running = False
        self.verify_report = None
        self.error = None


class VerifyReport:
    """验证报告"""
    
    def __init__(self, checks: List['VerifyCheck']):
        self.checks = checks
    
    @property
    def all_passed(self) -> bool:
        return all(check.passed for check in self.checks)


class VerifyCheck:
    """验证检查项"""
    
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
