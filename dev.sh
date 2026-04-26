#!/bin/bash
PROJECT="/Volumes/ORICO/projects/eq-trainer"

echo "======================================"
echo "  EQ Trainer - 高情商沟通训练"
echo "======================================"
echo ""

# Start backend
echo "[1/2] Starting backend (port 8000)..."
PYTHONPATH="$PROJECT" python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "[2/2] Starting frontend (port 5173)..."
"$PROJECT/frontend/node_modules/.bin/vite" --host 0.0.0.0 --port 5173 --config "$PROJECT/frontend/vite.config.ts" &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
