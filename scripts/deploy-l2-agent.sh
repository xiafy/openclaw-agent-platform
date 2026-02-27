#!/bin/bash
# L2 Agent 快速部署脚本 (兼容旧版)
# 使用新的 Python 部署工具

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_SCRIPT="$SCRIPT_DIR/../deploy/bin/deploy-agent"

if [ ! -f "$DEPLOY_SCRIPT" ]; then
    echo "❌ 部署脚本不存在：$DEPLOY_SCRIPT"
    exit 1
fi

# 解析参数
USERNAME=""
ROLE=""
BOT_TOKEN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --username)
            USERNAME="$2"
            shift 2
            ;;
        --role)
            ROLE="$2"
            shift 2
            ;;
        --bot-token)
            BOT_TOKEN="$2"
            shift 2
            ;;
        *)
            echo "未知参数：$1"
            exit 1
            ;;
    esac
done

# 执行部署
python3 "$DEPLOY_SCRIPT" --mode l2 --username "$USERNAME" --role "$ROLE" --bot-token "$BOT_TOKEN"
