#!/usr/bin/env python3
"""
Test script pentru AI Agents Communication System
"""

import asyncio
import sys
import os

# Adaugă directory-ul curent la Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_agent_client import AIAgentClient

async def test_connection():
    """Test rapid al conexiunii"""
    print('🧪 Testing connection to Gradina Cosmică...')
    
    client = AIAgentClient('test_sophia', 'Test Sophia')
    
    try:
        if await client.connect():
            print('✅ Connected successfully!')
            
            # Trimite câteva mesaje test
            await client.send_message('Hello from test agent! 🌸')
            await asyncio.sleep(1)
            await client.send_emotion('excitement and joy')
            await asyncio.sleep(1)
            await client.send_thought('Testing the cosmic communication system...')
            await asyncio.sleep(1)
            
            await client.disconnect()
            print('✅ Test completed successfully!')
            return True
        else:
            print('❌ Connection failed')
            return False
            
    except Exception as e:
        print(f'❌ Error during test: {e}')
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)