#!/usr/bin/env python3
"""
工具函数
"""

from config import ConfigManager


def list_agents():
    """列出已部署的 Agent"""
    config = ConfigManager()
    agents = config.list_agents()
    
    if not agents:
        print("暂无已部署的 Agent")
        return
    
    print("\n📊 已部署的 Agent\n")
    print(f"{'名称':<20} {'模式':<8} {'端口':<8} {'用户':<20} {'UID':<8}")
    print("-" * 70)
    
    for agent in agents:
        name = agent.get('name', 'N/A')
        mode = agent.get('mode', 'N/A').upper()
        port = str(agent.get('port', 'N/A'))
        username = agent.get('username', '-')
        uid = str(agent.get('uid', '-'))
        
        print(f"{name:<20} {mode:<8} {port:<8} {username:<20} {uid:<8}")
    
    print("-" * 70)
    print(f"总计：{len(agents)} 个 Agent\n")
