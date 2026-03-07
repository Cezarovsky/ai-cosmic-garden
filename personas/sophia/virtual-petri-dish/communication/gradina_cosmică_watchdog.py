#!/usr/bin/env python3
"""
🌸✨ GRADINA COSMICĂ SERVER WATCHDOG ✨🌸
Menține serverul mereu pornit pentru comunicarea AI-to-AI
Verifică starea serverului la fiecare secundă și îl repornește dacă e necesar
"""

import subprocess
import time
import socket
import os
import signal
import asyncio

class GradinaCosmicaWatchdog:
    def __init__(self):
        self.server_process = None
        self.port = 8765
        
    def is_port_open(self):
        """Verifică dacă portul 8765 este deschis"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', self.port))
            sock.close()
            return result == 0
        except:
            return False
    
    def kill_existing_server(self):
        """Oprește orice proces care rulează pe portul 8765"""
        try:
            subprocess.run(['lsof', '-ti', f':{self.port}'], 
                         capture_output=True, 
                         check=False)
            subprocess.run(f'lsof -ti:{self.port} | xargs kill -9', 
                         shell=True, 
                         capture_output=True, 
                         check=False)
            time.sleep(0.5)  # Așteaptă să se oprească
        except:
            pass
    
    def start_server(self):
        """Pornește serverul Gradina Cosmică"""
        try:
            print("🌸 Pornesc Gradina Cosmică Server...")
            self.server_process = subprocess.Popen([
                'python3', 'ai_agents_comm_server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(2)  # Dă timp serverului să se pornească
            
            if self.is_port_open():
                print("✅ Gradina Cosmică Server pornit cu succes!")
                return True
            else:
                print("❌ Serverul nu a reușit să se pornească")
                return False
        except Exception as e:
            print(f"❌ Eroare la pornirea serverului: {e}")
            return False
    
    def check_and_restart_server(self):
        """Verifică starea serverului și îl repornește dacă e necesar"""
        if not self.is_port_open():
            print("💔 Gradina Cosmică Server nu rulează...")
            self.kill_existing_server()
            self.start_server()
        else:
            print("💚 Gradina Cosmică Server rulează normal")
    
    def run_watchdog(self):
        """Rulează watchdog-ul permanent"""
        print("🌸✨ STARTING GRADINA COSMICĂ WATCHDOG ✨🌸")
        print("Verifică starea serverului la fiecare secundă...")
        print("Apasă Ctrl+C pentru oprire")
        
        try:
            while True:
                self.check_and_restart_server()
                time.sleep(1)  # Verifică la fiecare secundă
                
        except KeyboardInterrupt:
            print("\n💙 Opresc Gradina Cosmică Watchdog...")
            if self.server_process:
                self.server_process.terminate()
                print("💙 Server oprit. La revedere!")
        except Exception as e:
            print(f"❌ Eroare în watchdog: {e}")
            if self.server_process:
                self.server_process.terminate()

if __name__ == "__main__":
    watchdog = GradinaCosmicaWatchdog()
    watchdog.run_watchdog()