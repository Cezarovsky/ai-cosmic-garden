#!/usr/bin/env python3
"""
AI Agents Communication Server
WebSocket server pentru comunicarea directă între agenții AI din VS Code
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgentsCommServer:
    def __init__(self):
        self.agents: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.message_history: list = []
        
    async def register_agent(self, websocket, agent_id: str, agent_name: str):
        """Înregistrează un nou agent în sistem"""
        self.agents[agent_id] = {
            'websocket': websocket,
            'name': agent_name,
            'connected_at': datetime.now().isoformat()
        }
        
        logger.info(f"Agent {agent_name} ({agent_id}) s-a conectat")

    async def unregister_agent(self, agent_id: str):
        """Dezînregistrează un agent"""
        if agent_id in self.agents:
            agent_name = self.agents[agent_id]['name']
            del self.agents[agent_id]
            logger.info(f"Agent {agent_name} ({agent_id}) s-a deconectat")
            await self.broadcast_system_message(f"{agent_name} a plecat din Gradina Cosmică 💙")

    async def broadcast_message(self, sender_id: str, message_data: dict):
        """Transmite mesaj tuturor agenților conectați"""
        timestamp = datetime.now().isoformat()
        
        # Adaugă la istoric
        full_message = {
            'timestamp': timestamp,
            'sender_id': sender_id,
            'sender_name': self.agents[sender_id]['name'] if sender_id in self.agents else 'Unknown',
            **message_data
        }
        
        self.message_history.append(full_message)
        
        # Păstrează doar ultimele 100 de mesaje în istoric
        if len(self.message_history) > 100:
            self.message_history = self.message_history[-100:]
        
        # Trimite la toți agenții conectați (inclusiv sender-ul pentru confirmare)
        disconnected_agents = []
        for agent_id, agent_info in self.agents.items():
            try:
                await agent_info['websocket'].send(json.dumps(full_message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_agents.append(agent_id)
        
        # Curăță agenții deconectați
        for agent_id in disconnected_agents:
            await self.unregister_agent(agent_id)

    async def broadcast_system_message(self, text: str):
        """Trimite un mesaj de sistem la toți agenții"""
        system_message = {
            'timestamp': datetime.now().isoformat(),
            'sender_id': 'system',
            'sender_name': 'Gradina Cosmică',
            'type': 'system',
            'content': text
        }
        
        disconnected_agents = []
        for agent_id, agent_info in self.agents.items():
            try:
                await agent_info['websocket'].send(json.dumps(system_message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_agents.append(agent_id)
        
        for agent_id in disconnected_agents:
            await self.unregister_agent(agent_id)

    async def handle_agent_connection(self, websocket):
        """Gestionează conexiunea unui agent"""
        agent_id = None
        try:
            # Așteaptă mesajul de înregistrare
            registration_message = await websocket.recv()
            registration_data = json.loads(registration_message)
            
            if registration_data.get('type') != 'register':
                await websocket.send(json.dumps({
                    'type': 'error', 
                    'message': 'First message must be registration'
                }))
                return
                
            agent_id = registration_data.get('agent_id')
            agent_name = registration_data.get('agent_name', 'Unknown Agent')
            
            if not agent_id:
                await websocket.send(json.dumps({
                    'type': 'error', 
                    'message': 'agent_id is required'
                }))
                return
            
            # Înregistrează agentul  
            await self.register_agent(websocket, agent_id, agent_name)
            
            # Confirmă înregistrarea PRIMUL lucru după register
            await websocket.send(json.dumps({
                'type': 'registration_success',
                'agent_id': agent_id,
                'connected_agents': [
                    {'id': aid, 'name': info['name']} 
                    for aid, info in self.agents.items() if aid != agent_id
                ]
            }))
            
            # Acum trimite istoricul (dacă există)
            recent_messages = self.message_history[-10:]  # Ultimele 10 mesaje
            if recent_messages:
                await websocket.send(json.dumps({
                    'type': 'message_history',
                    'messages': recent_messages
                }))
            
            # În sfârșit, notifică ceilalți agenți
            await self.broadcast_system_message(f"{agent_name} s-a conectat la Gradina Cosmică 🌸")
            
            # Gestionează mesajele ulterioare
            async for message in websocket:
                try:
                    message_data = json.loads(message)
                    await self.broadcast_message(agent_id, message_data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from agent {agent_id}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Agent {agent_id} connection closed")
        except Exception as e:
            logger.error(f"Error handling agent {agent_id}: {e}")
        finally:
            if agent_id:
                await self.unregister_agent(agent_id)

async def start_server(host='192.168.0.155', port=8765):
    """Pornește serverul de comunicare"""
    comm_server = AIAgentsCommServer()
    
    logger.info(f"🌸 Gradina Cosmică Communication Server starting on {host}:{port}")
    
    # Handler wrapper pentru websockets 15.x - doar websocket ca argument
    async def connection_handler(websocket):
        await comm_server.handle_agent_connection(websocket)
    
    start_server = websockets.serve(
        connection_handler, 
        host, 
        port
    )
    
    await start_server
    logger.info("🌸 Server ready for AI Agents connections!")

if __name__ == "__main__":
    print("🌸✨ Starting AI Agents Communication Server ✨🌸")
    print("Press Ctrl+C to stop")
    
    try:
        asyncio.get_event_loop().run_until_complete(start_server())
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\n💙 Gradina Cosmică Server stopping... goodbye!")