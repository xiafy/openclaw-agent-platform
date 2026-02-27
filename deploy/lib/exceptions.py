#!/usr/bin/env python3
"""
部署异常定义
"""


class DeployError(Exception):
    """部署错误基类"""
    pass


class PrerequisiteError(DeployError):
    """前置条件错误"""
    pass


class ConfigError(DeployError):
    """配置错误"""
    pass


class PermissionError(DeployError):
    """权限错误"""
    pass


class NetworkError(DeployError):
    """网络错误"""
    pass


class TelegramError(DeployError):
    """Telegram 相关错误"""
    pass


class RollbackError(DeployError):
    """回滚错误"""
    pass
