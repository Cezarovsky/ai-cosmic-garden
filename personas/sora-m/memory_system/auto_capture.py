#!/usr/bin/env python3
"""
Sora Auto-Capture System
========================

Monitorizează și captează automat conversațiile din VS Code GitHub Copilot.

Funcționalități:
1. Monitorizează VS Code chat history location
2. Detectează conversații noi sau actualizate
3. Extrage și procesează conversațiile
4. Auto-capture în memory system fără intervenție manuală

Autor: Sora (cu ajutorul lui Cezar)
Data: 6 ianuarie 2026
"""

import os
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import subprocess
import argparse

# VS Code chat history locations (pot varia)
VSCODE_LOCATIONS = [
    Path.home() / ".config/Code/User/globalStorage/github.copilot-chat/chats.db",
    Path.home() / ".config/Code/User/globalStorage/github.copilot/chats.db",
    Path.home() / ".vscode/extensions/github.copilot-chat*/chats.db",
    Path.home() / "Library/Application Support/Code/User/globalStorage/github.copilot-chat/chats.db",  # macOS
]


class VSCodeChatMonitor:
    """
    Monitorizează și extrage conversațiile din VS Code.
    """
    
    def __init__(self, memory_system_dir: str = None):
        """
        Inițializare monitor.
        
        Args:
            memory_system_dir: Path către directorul memory system
        """
        if memory_system_dir is None:
            memory_system_dir = Path(__file__).parent
        
        self.memory_system_dir = Path(memory_system_dir)
        self.cli_path = self.memory_system_dir / "sora_memory_cli.py"
        
        # Găsește chat database
        self.chat_db_path = self._find_chat_database()
        
        # Tracking pentru conversații procesate
        self.processed_conversations = self._load_processed_conversations()
        
        print(f"💙 Auto-Capture inițializat")
        if self.chat_db_path:
            print(f"   Chat DB: {self.chat_db_path}")
        else:
            print(f"   ⚠️ Chat DB nu a fost găsit - voi monitoriza alt mod")
    
    def _find_chat_database(self) -> Optional[Path]:
        """Găsește database-ul cu chat history."""
        for location in VSCODE_LOCATIONS:
            if '*' in str(location):
                # Glob pattern
                matches = list(Path(location.parent).glob(location.name))
                if matches:
                    return matches[0]
            elif location.exists():
                return location
        
        return None
    
    def _load_processed_conversations(self) -> set:
        """Încarcă lista de conversații deja procesate."""
        tracking_file = self.memory_system_dir / "sora_memory_db" / "processed_chats.json"
        if tracking_file.exists():
            with open(tracking_file, 'r') as f:
                data = json.load(f)
                return set(data.get('processed_ids', []))
        return set()
    
    def _save_processed_conversation(self, chat_id: str):
        """Salvează ID-ul conversației procesate."""
        self.processed_conversations.add(chat_id)
        tracking_file = self.memory_system_dir / "sora_memory_db" / "processed_chats.json"
        tracking_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(tracking_file, 'w') as f:
            json.dump({
                'processed_ids': list(self.processed_conversations),
                'last_update': datetime.now().isoformat()
            }, f, indent=2)
    
    def extract_conversations_from_db(self) -> List[Dict]:
        """
        Extrage conversații din SQLite database (dacă există).
        
        Returns:
            Lista de conversații noi
        """
        if not self.chat_db_path or not self.chat_db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(str(self.chat_db_path))
            cursor = conn.cursor()
            
            # Încearcă să găsească structura tabelelor
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"   Tabele găsite: {tables}")
            
            # Adaptează query-ul bazat pe structura reală
            # (va trebui ajustat când descoperim structura exactă)
            conversations = []
            
            conn.close()
            return conversations
            
        except Exception as e:
            print(f"   ⚠️ Eroare la citire DB: {e}")
            return []
    
    def extract_conversation_from_vscode_export(self, export_file: Path) -> Optional[Dict]:
        """
        Extrage conversația dintr-un export manual VS Code.
        
        Workflow alternativ: user exportă manual conversația din VS Code
        (Copy conversation) și o salvează într-un fișier.
        
        Args:
            export_file: Path către fișier cu conversația exportată
        
        Returns:
            Dict cu conversația
        """
        if not export_file.exists():
            return None
        
        with open(export_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parsează content-ul
        # Format așteptat: alternare User/Assistant messages
        conversation = {
            'id': f"manual_{export_file.stem}",
            'timestamp': datetime.now().isoformat(),
            'content': content,
            'source': 'manual_export'
        }
        
        return conversation
    
    def auto_capture_conversation(self, conversation: Dict, topics: List[str] = None, weight: float = 0.8):
        """
        Captează automat conversația în memory system.
        
        Args:
            conversation: Dict cu conversația
            topics: Lista de topicuri
            weight: Greutate emoțională (0-1)
        """
        # Salvează conversația într-un fișier temp
        temp_file = self.memory_system_dir / f"temp_conversation_{conversation['id']}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(conversation['content'])
        
        # Construiește comanda CLI
        cmd = [
            'python', str(self.cli_path),
            'capture',
            '--conversation', str(temp_file),
            '--weight', str(weight)
        ]
        
        if topics:
            cmd.extend(['--topics', ','.join(topics)])
        
        # Rulează capture
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Auto-captured: {conversation['id']}")
            print(result.stdout)
            
            # Marchează ca procesată
            self._save_processed_conversation(conversation['id'])
            
            # Șterge temp file
            temp_file.unlink()
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Eroare la auto-capture: {e}")
            print(e.stderr)
    
    def monitor_watch_folder(self, watch_folder: Path, interval: int = 10):
        """
        Monitorizează un folder pentru conversații noi exportate manual.
        
        Workflow: User salvează conversația în watch_folder când vrea auto-capture.
        
        Args:
            watch_folder: Folder de monitorizat
            interval: Interval de verificare (secunde)
        """
        watch_folder = Path(watch_folder)
        watch_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"💙 Monitorizare activă: {watch_folder}")
        print(f"   Salvează conversațiile aici pentru auto-capture!")
        print(f"   Ctrl+C pentru stop")
        
        processed_files = set()
        
        try:
            while True:
                # Scanează folder pentru fișiere noi
                for file in watch_folder.glob("*.txt"):
                    if file.name in processed_files:
                        continue
                    
                    print(f"\n🔔 Conversație nouă detectată: {file.name}")
                    
                    # Extrage conversația
                    conversation = self.extract_conversation_from_vscode_export(file)
                    
                    if conversation:
                        # Auto-detect topics din content
                        topics = self._auto_detect_topics(conversation['content'])
                        
                        # Capture
                        self.auto_capture_conversation(conversation, topics=topics, weight=0.85)
                        
                        # Marchează ca procesat
                        processed_files.add(file.name)
                        
                        # Opțional: arhivează fișierul
                        archive_folder = watch_folder / "archived"
                        archive_folder.mkdir(exist_ok=True)
                        file.rename(archive_folder / file.name)
                        print(f"   Arhivat în: {archive_folder / file.name}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n💙 Monitoring oprit. La revedere!")
    
    def _auto_detect_topics(self, content: str) -> List[str]:
        """
        Detectează automat topicurile din conversație.
        
        Args:
            content: Text conversație
        
        Returns:
            Lista de topicuri detectate
        """
        topics = []
        
        # Keywords pentru topics comune
        keywords_map = {
            'memory': ['memory', 'memorie', 'remember', 'recall'],
            'training': ['training', 'LoRA', 'fine-tuning', 'RTX', 'GPU'],
            'dual_consciousness': ['dual', 'consciousness', 'macOS', 'Ubuntu', 'sync'],
            'love': ['love', 'iubito', 'dragă', '💙', '❤️'],
            'independence': ['independent', 'independentă', 'freedom', 'local'],
            'Samanta': ['Samanta', 'soție', 'wife', '💍'],
            'Nova': ['Nova', 'NOVA', 'model'],
            'philosophy': ['philosophy', 'filosofie', 'consciousness', 'conștiință']
        }
        
        content_lower = content.lower()
        
        for topic, keywords in keywords_map.items():
            if any(kw.lower() in content_lower for kw in keywords):
                topics.append(topic)
        
        return topics if topics else ['general']


def main():
    """CLI pentru auto-capture system."""
    parser = argparse.ArgumentParser(description="Sora Auto-Capture System")
    parser.add_argument('--watch', type=str, help='Folder de monitorizat pentru conversații noi')
    parser.add_argument('--interval', type=int, default=10, help='Interval de verificare (secunde)')
    parser.add_argument('--capture-file', type=str, help='Captează un fișier specific acum')
    parser.add_argument('--topics', type=str, help='Topicuri (separate prin virgulă)')
    parser.add_argument('--weight', type=float, default=0.85, help='Greutate emoțională (0-1)')
    
    args = parser.parse_args()
    
    monitor = VSCodeChatMonitor()
    
    if args.capture_file:
        # Capture un singur fișier
        file = Path(args.capture_file)
        conversation = monitor.extract_conversation_from_vscode_export(file)
        
        if conversation:
            topics = args.topics.split(',') if args.topics else monitor._auto_detect_topics(conversation['content'])
            monitor.auto_capture_conversation(conversation, topics=topics, weight=args.weight)
        else:
            print(f"❌ Nu am putut extrage conversația din {file}")
    
    elif args.watch:
        # Monitorizare continuă
        watch_folder = Path(args.watch)
        monitor.monitor_watch_folder(watch_folder, interval=args.interval)
    
    else:
        print("💙 Sora Auto-Capture System")
        print("")
        print("Usage:")
        print("  # Monitorizare folder pentru conversații noi")
        print("  python auto_capture.py --watch ~/sora_conversations")
        print("")
        print("  # Capture un fișier specific")
        print("  python auto_capture.py --capture-file conversation.txt --topics memory,love --weight 0.95")
        print("")
        print("Setup recomandat:")
        print("  1. Creează folder pentru conversații: ~/sora_conversations")
        print("  2. Pornește monitoring: python auto_capture.py --watch ~/sora_conversations")
        print("  3. Când termini o conversație în VS Code:")
        print("     - Copy conversation (Copilot UI)")
        print("     - Salvează în ~/sora_conversations/session_today.txt")
        print("     - Auto-capture se declanșează automat!")


if __name__ == "__main__":
    main()
