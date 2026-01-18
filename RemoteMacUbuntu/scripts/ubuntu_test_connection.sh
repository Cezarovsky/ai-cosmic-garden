#!/bin/bash
# Test conexiune SSH din Mac către Ubuntu
# Rulează după mac_ssh_setup.sh

echo "🧪 Test Conexiune SSH - Mac → Ubuntu"
echo "====================================="
echo ""

# Test 1: Conexiune simplă
echo "1️⃣ Test conexiune de bază..."
if ssh -o ConnectTimeout=5 nova-ubuntu "echo '✅ SSH OK'"; then
    echo "   ✅ Conexiune SSH funcționează"
else
    echo "   ❌ Conexiune SSH eșuată"
    exit 1
fi

# Test 2: GPU visibility
echo ""
echo "2️⃣ Test GPU (nvidia-smi)..."
ssh nova-ubuntu "nvidia-smi --query-gpu=name,driver_version,memory.total,temperature.gpu --format=csv,noheader"

# Test 3: CUDA availability
echo ""
echo "3️⃣ Test CUDA (nvcc --version)..."
ssh nova-ubuntu "nvcc --version 2>/dev/null || echo '⚠️  CUDA toolkit nu e instalat încă (normal)'"

# Test 4: Python
echo ""
echo "4️⃣ Test Python..."
ssh nova-ubuntu "python3 --version"

# Test 5: Git repos
echo ""
echo "5️⃣ Test Git repositories..."
ssh nova-ubuntu "ls -la ~ | grep -E 'ai-cosmic-garden|NOVA_20'"

# Test 6: Disk space
echo ""
echo "6️⃣ Test Storage (PCIe 4.0 SSD)..."
ssh nova-ubuntu "df -h / | tail -n 1"

# Test 7: Memory
echo ""
echo "7️⃣ Test RAM..."
ssh nova-ubuntu "free -h | grep Mem"

echo ""
echo "🎯 Test complet!"
echo ""
echo "📊 Summary:"
ssh nova-ubuntu "echo 'Hostname: $(hostname)' && echo 'Kernel: $(uname -r)' && echo 'Uptime: $(uptime -p)'"
echo ""
echo "✨ Gata de training! Următorul pas: VSCode Remote SSH"
