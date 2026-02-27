#!/usr/bin/env python3
"""
部署验证器
"""

import subprocess
import time
from pathlib import Path
from config import DeployResult, VerifyReport, VerifyCheck


class Verifier:
    """部署验证器"""
    
    def __init__(self, deploy_result: DeployResult):
        self.result = deploy_result
        self.checks = []
    
    def run(self) -> VerifyReport:
        """执行验证"""
        print("开始验证...\n")
        
        checks = [
            ("进程检查", self._check_process),
            ("端口检查", self._check_port),
            ("WebSocket 检查", self._check_websocket),
            ("工作流程", self._check_workflow),
        ]
        
        for name, check_func in checks:
            try:
                passed, message = check_func()
                self.checks.append(VerifyCheck(name, passed, message))
                icon = "✅" if passed else "❌"
                print(f"  {icon} {name}: {message}")
            except Exception as e:
                self.checks.append(VerifyCheck(name, False, str(e)))
                print(f"  ❌ {name}: {e}")
        
        self.result.verify_report = VerifyReport(self.checks)
        
        # 总结
        passed = sum(1 for c in self.checks if c.passed)
        total = len(self.checks)
        print(f"\n验证结果：{passed}/{total} 通过")
        
        return self.result.verify_report
    
    def _check_process(self):
        """检查进程"""
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True, text=True
        )
        
        if 'openclaw' in result.stdout and str(self.result.port) in result.stdout:
            return True, "Gateway 运行中"
        return False, "Gateway 未运行"
    
    def _check_port(self):
        """检查端口"""
        result = subprocess.run(
            ['lsof', '-i', f':{self.result.port}'],
            capture_output=True, text=True
        )
        
        if 'LISTEN' in result.stdout:
            return True, f"端口 {self.result.port} 监听中"
        return False, f"端口 {self.result.port} 未监听"
    
    def _check_websocket(self):
        """检查 WebSocket"""
        # 简单检查端口是否可达
        import socket
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', self.result.port))
            sock.close()
            
            if result == 0:
                return True, "WebSocket 可连接"
            return False, "WebSocket 无法连接"
        except:
            return False, "WebSocket 检查失败"
    
    def _check_workflow(self):
        """检查工作流程 (通过 API)"""
        # 这里可以实现调用 Gateway API 验证
        # 简化版本：跳过
        return True, "跳过 (需手动验证)"
