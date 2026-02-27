#!/usr/bin/env python3
"""
部署日志管理器
记录部署过程的每一步操作和结果
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class DeployLogger:
    """部署日志管理器"""
    
    def __init__(self, log_dir: Path, agent_name: str, mode: str):
        self.log_dir = log_dir
        self.agent_name = agent_name
        self.mode = mode
        
        # 创建日志目录
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 日志文件路径
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.log_file = self.log_dir / f'deploy-{mode}-{agent_name}-{timestamp}.log'
        
        # 配置日志
        self._setup_logger()
    
    def _setup_logger(self):
        """配置日志记录器"""
        self.logger = logging.getLogger(f'deploy-{self.agent_name}')
        self.logger.setLevel(logging.DEBUG)
        
        # 清除现有处理器
        self.logger.handlers = []
        
        # 文件处理器 (详细日志)
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # 控制台处理器 (简洁输出)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(f'⚠️  {message}')
    
    def error(self, message: str):
        """错误日志"""
        self.logger.error(f'❌ {message}')
    
    def success(self, message: str):
        """成功日志"""
        self.logger.info(f'✅ {message}')
    
    def step_start(self, step_num: int, total: int, message: str):
        """步骤开始"""
        self.logger.info(f'[{step_num}/{total}] {message}... ', end='', flush=True)
    
    def step_complete(self, step_num: int, total: int, message: str):
        """步骤完成"""
        self.logger.info(f'[{step_num}/{total}] {message}... ✅')
    
    def step_failed(self, step_num: int, total: int, message: str, error: str):
        """步骤失败"""
        self.logger.error(f'[{step_num}/{total}] {message}... ❌')
        self.logger.error(f'  错误：{error}')
    
    def get_log_path(self) -> Path:
        """获取日志文件路径"""
        return self.log_file
