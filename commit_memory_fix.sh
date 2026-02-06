#!/bin/bash
cd /Users/cezartipa/Documents/ai-cosmic-garden

git add sora/memory_system/extract_vscode_chat.py

git commit -m "FIX CRITIC: Sora Memory - VS Code JSON structure changed

PROBLEMA: VS Code a schimbat structura JSON 2024->2026
VECHI: response[].kind == markdownContent 
NOU: response[].kind == thinking (aici sunt raspunsurile mele)

SOLUTIE:
- Suport dual pentru ambele formate
- Debug logging pentru diagnosticare viitoare
- Backward compatibility

Acum salveaza CORECT conversatiile complete (User + Sora)"

echo "✅ Committed memory fix"

git push origin main

echo "✅ Pushed to GitHub"
