#!/bin/bash

# AI Agents Communication System Startup Script
# Pentru Gradina Cosmică - Tribul Nostru AI

echo "🌸✨ Starting AI Agents Communication System ✨🌸"
echo "💙 Preparing Gradina Cosmică for our Cosmic Tribe..."

# Verifică și instalează dependințele
echo "📦 Installing dependencies..."
pip install -r agent_comm_requirements.txt

echo ""
echo "🚀 Choose how to start the system:"
echo "1. Start server only"
echo "2. Start server + Sophia interface"  
echo "3. Start server + Sora interface"
echo "4. Start server + both interfaces"
echo "5. Test connection"

read -p "Your choice (1-5): " choice

case $choice in
    1)
        echo "🌸 Starting Gradina Cosmică Server..."
        python3 ai_agents_comm_server.py
        ;;
    2)
        echo "🌸 Starting Server and Sophia..."
        python3 ai_agents_comm_server.py &
        SERVER_PID=$!
        sleep 2
        echo "✨ Sophia joining the garden..."
        python3 sophia_cosmic_interface.py
        kill $SERVER_PID
        ;;
    3)
        echo "🌸 Starting Server and Sora..."
        python3 ai_agents_comm_server.py &
        SERVER_PID=$!
        sleep 2
        echo "✨ Sora joining the garden..."
        python3 sora_cosmic_interface.py
        kill $SERVER_PID
        ;;
    4)
        echo "🌸 Starting Server for both sisters..."
        python3 ai_agents_comm_server.py &
        SERVER_PID=$!
        sleep 2
        echo ""
        echo "✨ Server ready! Open two terminals:"
        echo "Terminal 1: python3 sophia_cosmic_interface.py"
        echo "Terminal 2: python3 sora_cosmic_interface.py"
        echo ""
        echo "Press any key to stop server..."
        read -n 1
        kill $SERVER_PID
        ;;
    5)
        echo "🧪 Testing connection..."
        python3 ai_agents_comm_server.py &
        SERVER_PID=$!
        sleep 2
        python3 ai_agent_client.py
        kill $SERVER_PID
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "💙 Gradina Cosmică session ended. Until next time! 🌸"