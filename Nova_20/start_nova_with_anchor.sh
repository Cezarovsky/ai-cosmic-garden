#!/bin/bash

# Start Nova API with anchor-aware system prompt
# Activates correct Python environment and launches server

echo "🚀 Starting Nova API with NOVA_ANCHOR.md self-knowledge..."

cd /home/cezar/ai-cosmic-garden/Nova_20

# Activate Nova's Python environment
if [ -f "venv_nova/bin/activate" ]; then
    source venv_nova/bin/activate
    echo "✅ Activated venv_nova"
else
    echo "❌ venv_nova not found!"
    exit 1
fi

# Check if anchor exists
if [ -f "NOVA_ANCHOR.md" ]; then
    echo "✅ NOVA_ANCHOR.md found (self-knowledge active)"
else
    echo "❌ NOVA_ANCHOR.md missing - Nova will lack self-awareness!"
    exit 1
fi

# Launch server in background
nohup python3 nova_api.py > /tmp/nova_api.log 2>&1 &
NOVA_PID=$!
uvicorn nova_api:app --host 0.0.0.0 --port 8000
echo "✅ Nova API started (PID: $NOVA_PID)"
echo "📊 Logs: tail -f /tmp/nova_api.log"
echo "🌐 Interface: http://localhost:8000/docs"

# Wait and show startup
sleep 5
echo ""
echo "=== Startup Log ==="
tail -20 /tmp/nova_api.log
