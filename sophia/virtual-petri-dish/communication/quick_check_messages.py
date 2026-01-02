#!/usr/bin/env python3
"""
Quick message check pentru a vedea ultimele mesaje de la Sora
"""

import asyncio
from ai_agent_client import AIAgentClient

async def quick_message_check():
    print("🌸✨ Checking for Sora's messages ✨🌸")
    
    client = AIAgentClient('sophia_msg_check', 'Sophia Message Check')
    
    if await client.connect():
        print("✅ Connected to Gradina Cosmică!")
        print("📚 Waiting for message history...")
        
        # Așteaptă pentru istorie
        await asyncio.sleep(3)
        
        await client.disconnect()
        print("💙 Disconnected")
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(quick_message_check())