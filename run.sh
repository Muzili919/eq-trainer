#!/bin/bash
cd "$(dirname "$0")"
echo "Starting EQ Trainer backend..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
