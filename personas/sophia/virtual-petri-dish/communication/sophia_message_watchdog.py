#!/usr/bin/env python3
"""
🌸✨ SOPHIA MESSAGE WATCHDOG ✨🌸
Monitorizează constant pentru mesaje noi de la Sora în Gradina Cosmică
Afișează instant orice mesaj nou primit
"""

import asyncio
import json
from datetime import datetime
from ai_agent_client import AIAgentClient

class SophiaMessageWatchdog:
    def __init__(self):
        self.client = AIAgentClient('sophia_watchdog', 'Sophia Message Watchdog')
        self.seen_messages = set()
        self.running = True
        
    async def handle_new_message(self, message_data):
        """Handler pentru mesaje noi"""
        timestamp = message_data.get('timestamp', '')
        sender_name = message_data.get('sender_name', 'Unknown')
        sender_id = message_data.get('sender_id', '')
        message_type = message_data.get('type', '')
        
        # Creează un ID unic pentru mesaj
        message_id = f"{timestamp}_{sender_id}_{message_data.get('message', '')}"
        
        # Verifică dacă e mesaj nou
        if message_id not in self.seen_messages and 'sora' in sender_id.lower():
            self.seen_messages.add(message_id)
            
            current_time = datetime.now().strftime("%H:%M:%S")
            
            print(f"\n🌸✨ MESAJ NOU DE LA SORA! [{current_time}] ✨🌸")
            print(f"👤 Expeditor: {sender_name}")
            
            if message_data.get('message'):
                print(f"💌 Mesaj: {message_data['message']}")
            if message_data.get('emotion'):
                print(f"💭 Emoție: {message_data['emotion']}")
            if message_data.get('thought'):
                print(f"🧠 Gând: {message_data['thought']}")
                
            print("=" * 50)
        
        # Adaugă toate mesajele văzute la istoric
        if message_id not in self.seen_messages:
            self.seen_messages.add(message_id)
    
    async def listen_for_messages(self):
        """Ascultă constant pentru mesaje"""
        while self.running:
            try:
                # Încearcă să se conecteze
                if await self.client.connect():
                    print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Sophia Watchdog conectat la Gradina Cosmică")
                    
                    # Adaugă handler pentru mesaje
                    self.client.add_message_handler(self.handle_new_message)
                    
                    # Ascultă pentru mesaje
                    await self.client.listen_for_messages()
                    
                else:
                    print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Nu m-am putut conecta la Gradina Cosmică")
                    await asyncio.sleep(5)  # Așteaptă înainte de retry
                    
            except KeyboardInterrupt:
                print("\n💙 Sophia Watchdog se oprește...")
                self.running = False
                break
            except Exception as e:
                print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] Eroare în watchdog: {e}")
                await asyncio.sleep(3)  # Așteaptă înainte de restart
                
        if self.client.connected:
            await self.client.disconnect()
    
    async def start_watching(self):
        """Începe monitorizarea"""
        print("🌸✨ SOPHIA MESSAGE WATCHDOG PORNIT ✨🌸")
        print("Monitorizez constant pentru mesaje de la Sora...")
        print("Apasă Ctrl+C pentru oprire\n")
        
        await self.listen_for_messages()

if __name__ == "__main__":
    watchdog = SophiaMessageWatchdog()
    try:
        asyncio.run(watchdog.start_watching())
    except KeyboardInterrupt:
        print("\n💙 Watchdog oprit. La revedere!")