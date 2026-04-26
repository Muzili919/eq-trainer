#!/usr/bin/env bash
# 后端启动脚本
set -e

cd "$(dirname "$0")"

# 激活 venv（如果存在）
if [ -d ".venv" ]; then
  source .venv/bin/activate
elif [ -d "venv" ]; then
  source venv/bin/activate
fi

# 拷贝 .env.example → .env（首次启动）
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
  echo "已创建 .env，请填入 DEEPSEEK_API_KEY 后重新启动"
  exit 1
fi

export PYTHONPATH="$(pwd):$PYTHONPATH"
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
