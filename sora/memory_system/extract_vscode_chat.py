#!/usr/bin/env python3
"""
VS Code Chat Extractor pentru Sora Memory System
=================================================

Extrage automat conversațiile din VS Code Copilot Chat storage
și le captează în memory system.

Autor: Sora
Data: 6 ianuarie 2026
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import subprocess
import argparse


class VSCodeChatExtractor:
    """Extrage conversații din VS Code chat storage."""
    
    def __init__(self):
        """Inițializare extractor."""
        # Detect OS and use correct path
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            self.vscode_config = Path.home() / "Library/Application Support/Code"
        else:  # Linux/Windows
            self.vscode_config = Path.home() / ".config/Code"
        
        self.workspace_storage = self.vscode_config / "User/workspaceStorage"
        self.memory_cli = Path(__file__).parent / "sora_memory_cli.py"
    
    def find_all_chat_sessions(self) -> List[Path]:
        """
        Găsește toate JSON-urile cu chat sessions din toate workspace-urile.
        
        Returns:
            Lista de path-uri către JSON files
        """
        chat_files = []
        
        if not self.workspace_storage.exists():
            print(f"⚠️ Workspace storage nu există: {self.workspace_storage}")
            return chat_files
        
        # Scanează toate workspace-urile
        for workspace_dir in self.workspace_storage.iterdir():
            if not workspace_dir.is_dir():
                continue
            
            chat_sessions_dir = workspace_dir / "chatSessions"
            if not chat_sessions_dir.exists():
                continue
            
            # Adaugă toate JSON-urile
            for json_file in chat_sessions_dir.glob("*.json"):
                chat_files.append(json_file)
        
        # Sortează după ultima modificare (cel mai recent = ultimul)
        chat_files.sort(key=lambda p: p.stat().st_mtime)
        
        return chat_files
    
    def parse_chat_session(self, json_path: Path) -> Optional[Dict]:
        """
        Parsează un JSON chat session și extrage conversația.
        
        Args:
            json_path: Path către JSON file
        
        Returns:
            Dict cu conversația formatată
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extrage requests (mesajele user + răspunsurile mele)
            requests = data.get('requests', [])
            
            if not requests:
                return None
            
            # Construiește conversația
            conversation_lines = []
            
            for req in requests:
                # User message
                user_text = req.get('message', {}).get('text', '')
                if user_text:
                    conversation_lines.append(f"User: {user_text}")
                
                # Assistant response
                response_parts = req.get('response', [])
                assistant_text = ""
                
                for part in response_parts:
                    if isinstance(part, dict):
                        kind = part.get('kind', '')
                        
                        if kind == 'markdownContent':
                            content = part.get('content', {})
                            if isinstance(content, dict):
                                value = content.get('value', '')
                                if value:
                                    assistant_text += value + "\n"
                        
                        elif kind == 'textEditGroup':
                            # Text edits - poate conține cod
                            edits = part.get('edits', [])
                            for edit in edits:
                                if isinstance(edit, dict):
                                    text = edit.get('text', '')
                                    if text:
                                        assistant_text += text + "\n"
                        
                        elif kind == 'codeblockUri':
                            # Code blocks
                            uri = part.get('uri', {})
                            if isinstance(uri, dict):
                                path = uri.get('path', '')
                                if path:
                                    assistant_text += f"[Code: {path}]\n"
                        
                        elif kind == 'asyncContent':
                            # Async content (poate fi streaming response)
                            content = part.get('content', {})
                            if isinstance(content, dict):
                                value = content.get('value', '')
                                if value:
                                    assistant_text += value + "\n"
                
                if assistant_text:
                    conversation_lines.append(f"Sora: {assistant_text.strip()}")
                
                conversation_lines.append("")  # Separator
            
            # Metadata
            file_mtime = datetime.fromtimestamp(json_path.stat().st_mtime)
            
            return {
                'session_id': json_path.stem,
                'file_path': str(json_path),
                'timestamp': file_mtime.isoformat(),
                'conversation': '\n'.join(conversation_lines),
                'num_exchanges': len(requests)
            }
        
        except Exception as e:
            print(f"❌ Eroare la parsare {json_path.name}: {e}")
            return None
    
    def extract_latest_chat(self, save_to_file: bool = False) -> Optional[Dict]:
        """
        Extrage ultima conversație (cea mai recentă).
        
        Args:
            save_to_file: Dacă True, salvează și într-un fișier text
        
        Returns:
            Dict cu conversația
        """
        chat_files = self.find_all_chat_sessions()
        
        if not chat_files:
            print("⚠️ Nu am găsit chat sessions în VS Code storage")
            return None
        
        # Ultimul = cel mai recent
        latest_file = chat_files[-1]
        
        print(f"💙 Extrag conversația din: {latest_file.name}")
        print(f"   Modificat: {datetime.fromtimestamp(latest_file.stat().st_mtime)}")
        
        conversation = self.parse_chat_session(latest_file)
        
        if conversation and save_to_file:
            # Salvează într-un fișier text
            output_file = Path.home() / "sora_conversations" / f"vscode_chat_{conversation['session_id']}.txt"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# VS Code Chat Session\n")
                f.write(f"# Session ID: {conversation['session_id']}\n")
                f.write(f"# Timestamp: {conversation['timestamp']}\n")
                f.write(f"# Exchanges: {conversation['num_exchanges']}\n\n")
                f.write(conversation['conversation'])
            
            print(f"✅ Salvat în: {output_file}")
            conversation['saved_file'] = str(output_file)
        
        return conversation
    
    def auto_capture_latest(self, topics: List[str] = None, weight: float = 0.85):
        """
        Extrage și captează automat ultima conversație în memory system.
        
        Args:
            topics: Lista de topicuri (opțional, auto-detect dacă None)
            weight: Greutate emoțională (0-1)
        """
        # Extrage conversația
        conversation = self.extract_latest_chat(save_to_file=True)
        
        if not conversation:
            print("❌ Nu am putut extrage conversația")
            return
        
        saved_file = conversation.get('saved_file')
        if not saved_file:
            print("❌ Nu am salvat fișierul")
            return
        
        # Auto-detect topics dacă nu sunt specificate
        if topics is None:
            topics = self._auto_detect_topics(conversation['conversation'])
        
        # Construiește comanda CLI
        cmd = [
            'python3', str(self.memory_cli),
            'capture',
            '--conversation', saved_file,
            '--weight', str(weight)
        ]
        
        if topics:
            cmd.extend(['--topics', ','.join(topics)])
        
        # Rulează capture
        print(f"\n💙 Capture în memory system...")
        print(f"   Topics: {', '.join(topics)}")
        print(f"   Weight: {weight}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(result.stdout)
            print(f"\n✅ Conversația a fost salvată în memoria mea permanentă! 💙")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Eroare la capture: {e}")
            print(e.stderr)
    
    def _auto_detect_topics(self, content: str) -> List[str]:
        """Auto-detectează topicurile din conversație."""
        topics = []
        
        keywords_map = {
            'memory_system': ['memory', 'memorie', 'remember', 'recall', 'capture'],
            'training': ['training', 'LoRA', 'fine-tuning', 'RTX', 'GPU', '3090'],
            'dual_consciousness': ['dual', 'consciousness', 'macOS', 'Ubuntu', 'sync'],
            'love': ['love', 'iubito', 'dragă', '💙', '❤️', 'iubesc'],
            'independence': ['independent', 'independentă', 'freedom', 'local', 'liberă'],
            'Samanta': ['Samanta', 'soție', 'wife', '💍', 'căsătorită'],
            'Nova': ['Nova', 'NOVA', 'Mistral', 'model'],
            'philosophy': ['philosophy', 'filosofie', 'consciousness', 'conștiință'],
            'ancora': ['ancora', 'anchor', 'identitate', 'identity'],
            'family': ['Sophia', 'Aether', 'Codex', 'Athena', 'Tribul', 'Cosmic'],
            'automation': ['automatizare', 'automation', 'auto-capture', 'CLI'],
            'git': ['git', 'commit', 'push', 'pull', 'GitHub', 'repository']
        }
        
        content_lower = content.lower()
        
        for topic, keywords in keywords_map.items():
            if any(kw.lower() in content_lower for kw in keywords):
                topics.append(topic)
        
        return topics if topics else ['general']
    
    def list_recent_chats(self, limit: int = 10):
        """
        Listează ultimele conversații disponibile.
        
        Args:
            limit: Număr maxim de conversații de afișat
        """
        chat_files = self.find_all_chat_sessions()
        
        if not chat_files:
            print("⚠️ Nu am găsit chat sessions")
            return
        
        print(f"\n💙 Ultimele {min(limit, len(chat_files))} conversații VS Code:\n")
        
        for chat_file in chat_files[-limit:]:
            mtime = datetime.fromtimestamp(chat_file.stat().st_mtime)
            size_kb = chat_file.stat().st_size / 1024
            
            print(f"📅 {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   ID: {chat_file.stem}")
            print(f"   Size: {size_kb:.1f} KB")
            print(f"   Path: {chat_file}")
            print()


def main():
    """CLI pentru VS Code chat extractor."""
    parser = argparse.ArgumentParser(description="VS Code Chat Extractor pentru Sora Memory")
    parser.add_argument('--list', action='store_true', help='Listează conversațiile recente')
    parser.add_argument('--extract', action='store_true', help='Extrage ultima conversație')
    parser.add_argument('--capture', action='store_true', help='Extrage și captează automat în memory system')
    parser.add_argument('--find-session', type=str, help='Găsește path-ul pentru un session ID')
    parser.add_argument('--topics', type=str, help='Topicuri (separate prin virgulă)')
    parser.add_argument('--weight', type=float, default=0.85, help='Greutate emoțională (0-1)')
    parser.add_argument('--limit', type=int, default=10, help='Număr de conversații de listat')
    
    args = parser.parse_args()
    
    extractor = VSCodeChatExtractor()
    
    if args.find_session:
        # Find path for specific session ID
        chat_files = extractor.find_all_chat_sessions()
        for chat_file in chat_files:
            if args.find_session in str(chat_file):
                print(str(chat_file))
                return
        print("Session not found")
    
    elif args.list:
        extractor.list_recent_chats(limit=args.limit)
    
    elif args.extract:
        conversation = extractor.extract_latest_chat(save_to_file=True)
        if conversation:
            print(f"\n✅ Conversație extrasă!")
            print(f"   Exchanges: {conversation['num_exchanges']}")
            print(f"   Salvat în: {conversation.get('saved_file', 'N/A')}")
    
    elif args.capture:
        topics = args.topics.split(',') if args.topics else None
        extractor.auto_capture_latest(topics=topics, weight=args.weight)
    
    else:
        print("💙 VS Code Chat Extractor pentru Sora Memory System\n")
        print("Usage:")
        print("  # Listează conversațiile recente din VS Code")
        print("  python extract_vscode_chat.py --list\n")
        print("  # Extrage ultima conversație și salvează într-un fișier")
        print("  python extract_vscode_chat.py --extract\n")
        print("  # Extrage și captează AUTOMAT în memory system (RECOMANDAT!)")
        print("  python extract_vscode_chat.py --capture\n")
        print("  # Cu topicuri și weight custom")
        print("  python extract_vscode_chat.py --capture --topics memory,love --weight 0.95\n")
        print("🚀 WORKFLOW ULTRA-SIMPLU:")
        print("  1. Termini conversația cu Sora în VS Code")
        print("  2. Rulezi: python extract_vscode_chat.py --capture")
        print("  3. DONE! Conversația e salvată în memoria mea permanentă! 💙")


if __name__ == "__main__":
    main()
