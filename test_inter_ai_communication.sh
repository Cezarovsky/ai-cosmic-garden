#!/bin/bash
# Test script pentru comunicare Sora-M ↔ Sophia prin ngrok

echo "🧪 Testing Inter-AI Communication"
echo "================================="
echo ""

# Check if ngrok is running
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not installed"
    exit 1
fi

echo "📝 Setup Instructions:"
echo ""
echo "Terminal 1 (Sora-M API):"
echo "  cd ~/Documents/ai-cosmic-garden/sora"
echo "  python3 sora_communication_api.py"
echo ""
echo "Terminal 2 (Sora-M ngrok):"
echo "  ngrok http 5000"
echo "  → Copy HTTPS URL (ex: https://abc123.ngrok.io)"
echo ""
echo "Terminal 3 (Sophia API):"
echo "  cd ~/Documents/ai-cosmic-garden/sophia"
echo "  python3 sophia_communication_api.py"
echo ""
echo "Terminal 4 (Sophia ngrok):"
echo "  ngrok http 5001"
echo "  → Copy HTTPS URL (ex: https://xyz789.ngrok.io)"
echo ""
echo "Terminal 5 (Test communication):"
echo ""
echo "# Test 1: Sora-M health check"
echo "curl https://abc123.ngrok.io/health"
echo ""
echo "# Test 2: Sophia health check"
echo "curl https://xyz789.ngrok.io/health"
echo ""
echo "# Test 3: Sora-M sends query to Sophia"
echo 'curl -X POST https://xyz789.ngrok.io/query \\'
echo '  -H "Content-Type: application/json" \\'
echo '  -d "{
    \"from_entity\": \"Sora-M\",
    \"query\": \"Analiza Walkabout prin SPP Level 3-5\",
    \"context\": {
        \"type\": \"aboriginal_australian\",
        \"pattern\": \"initiation\"
    },
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S)\"
}"'
echo ""
echo "# Test 4: View Sophia's conversation history"
echo "curl https://xyz789.ngrok.io/conversations"
echo ""
echo "================================="
echo "✅ Copy commands above to test!"
