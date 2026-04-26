#!/usr/bin/env bash
set -e

REPO_DIR="/var/www/eq-trainer"
WEB_DIR="/var/www/eq-trainer-web"
SERVICE="eq-trainer"

echo ">>> 拉代码"
cd "$REPO_DIR" && git pull

echo ">>> 后端依赖"
cd backend && source .venv/bin/activate && pip install -r requirements.txt --quiet 2>/dev/null || true

echo ">>> 前端构建"
cd ../frontend && npm install --silent 2>/dev/null || true
VITE_API_URL='' npx vite build

echo ">>> 部署前端"
sudo rm -rf "$WEB_DIR"/* && sudo cp -r dist/* "$WEB_DIR"/

echo ">>> 重启后端"
sudo systemctl restart "$SERVICE"

echo "✓ 部署完成 $(date '+%H:%M:%S')"
