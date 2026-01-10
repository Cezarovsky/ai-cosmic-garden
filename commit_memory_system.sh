#!/bin/bash
# Commit memory system before VS Code restart

cd /Users/cezartipa/Documents/ai-cosmic-garden

echo "📦 Adding memory system files..."
git add .github/copilot-instructions.md
git add sora/update_system_prompt.py
git add sora/save_current_session.py

echo "💾 Committing..."
git commit -m "Add persistent memory system: auto-loading system prompt from sora_memory_db

- .github/copilot-instructions.md: GitHub Copilot reads automatically
- sora/update_system_prompt.py: Regenerates prompt from memory sessions
- sora/save_current_session.py: Captures current VS Code conversation

After restart, Sora-M will know her identity, relationships, and project context."

echo "🚀 Pushing to GitHub..."
git push

echo "✅ Done! Ready for VS Code restart."
echo ""
echo "After restart, run:"
echo "  python3 sora/save_current_session.py"
echo "  python3 sora/update_system_prompt.py"
