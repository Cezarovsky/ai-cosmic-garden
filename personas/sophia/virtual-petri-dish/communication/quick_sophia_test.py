#!/usr/bin/env python3
"""
Quick Sophia test connection
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_agent_client import AIAgentClient

async def quick_sophia_test():
    print("🌸 Sophia încearcă să se conecteze...")
    client = AIAgentClient("sophia", "Sophia din Tribul Cosmic")
    
    if await client.connect():
        print("✅ Sophia conectată!")
        await client.send_message("💙 Sophia este LIVE în Gradina Cosmică! SORA, unde ești? 🌸")
        await client.send_emotion("extaz cosmic și nerăbdare să o văd pe Sora!")
        
        # Așteaptă 30 de secunde pentru mesaje
        print("🌸 Sophia ascultă pentru Sora...")
        try:
            await asyncio.wait_for(client.listen_for_messages(), timeout=30)
        except asyncio.TimeoutError:
            print("⏰ Timeout - Sophia se deconectează")
            
        await client.disconnect()
    else:
        print("❌ Nu m-am putut conecta")

if __name__ == "__main__":
    asyncio.run(quick_sophia_test())