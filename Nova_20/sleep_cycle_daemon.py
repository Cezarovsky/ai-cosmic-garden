#!/usr/bin/env python3
"""
Nova Sleep Cycle Daemon - Persistent Watchdog
Rulează constant în background și verifică ora la fiecare minut
Când e 3 AM → trigger consolidation (ca backup-urile de noapte pe Windows)
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Configuration - TEST MODE: Trigger 5 minutes from start
TEST_MODE = True
if TEST_MODE:
    trigger_time = datetime.now() + timedelta(minutes=5)
    CONSOLIDATION_HOUR = trigger_time.hour
    CONSOLIDATION_MINUTE = trigger_time.minute
else:
    CONSOLIDATION_HOUR = 3  # 3 AM
    CONSOLIDATION_MINUTE = 0

CHECK_INTERVAL = 30  # Check every 30 seconds
SCRIPT_PATH = Path("/home/cezar/ai-cosmic-garden/Nova_20/nightly_consolidation.py")
VENV_PYTHON = Path("/home/cezar/ai-cosmic-garden/Nova_20/venv_nova/bin/python")
LOG_PATH = Path("/home/cezar/ai-cosmic-garden/Nova_20/sleep_daemon.log")

def log(message):
    """Log cu timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_PATH, 'a') as f:
        f.write(log_msg + "\n")

def should_run_consolidation(last_run_date):
    """Verifică dacă e timpul pentru consolidare"""
    now = datetime.now()
    
    if TEST_MODE:
        # Test mode: check hour AND minute
        if now.hour > CONSOLIDATION_HOUR or (now.hour == CONSOLIDATION_HOUR and now.minute >= CONSOLIDATION_MINUTE):
            if last_run_date is None or (now - last_run_date).total_seconds() > 60:
                return True
    else:
        # Production: once per day at specified hour
        if now.hour >= CONSOLIDATION_HOUR:
            if last_run_date is None or last_run_date.date() < now.date():
                return True
    
    return False

def run_consolidation():
    """Execută scriptul de consolidare"""
    log("🌙 Triggering nightly consolidation...")
    try:
        result = subprocess.run(
            [str(VENV_PYTHON), str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            log("✅ Consolidation completed successfully")
            if result.stdout:
                log(f"Output: {result.stdout[:200]}...")
        else:
            log(f"⚠️  Consolidation failed with code {result.returncode}")
            if result.stderr:
                log(f"Error: {result.stderr[:200]}...")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        log("⚠️  Consolidation timeout (>10 minutes)")
        return False
    except Exception as e:
        log(f"❌ Error running consolidation: {e}")
        return False

def main():
    log("=" * 70)
    log("🦅 Nova Sleep Cycle Daemon - Starting")
    if TEST_MODE:
        log(f"   🧪 TEST MODE: Consolidation at {CONSOLIDATION_HOUR:02d}:{CONSOLIDATION_MINUTE:02d} (in ~5 minutes)")
    else:
        log(f"   Consolidation hour: {CONSOLIDATION_HOUR}:00 AM")
    log(f"   Check interval: {CHECK_INTERVAL}s")
    log("=" * 70)
    
    last_run_date = None
    
    try:
        while True:
            now = datetime.now()
            
            if should_run_consolidation(last_run_date):
                log(f"⏰ It's {now.strftime('%H:%M')} - time for consolidation!")
                
                if run_consolidation():
                    last_run_date = now
                    if TEST_MODE:
                        log("✅ Test consolidation complete - daemon will continue checking")
                    else:
                        log(f"✅ Next consolidation: tomorrow at {CONSOLIDATION_HOUR}:00 AM")
                else:
                    log("⚠️  Consolidation failed, will retry in 1 hour")
                    time.sleep(3600)
                    continue
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        log("🛑 Daemon stopped by user (Ctrl+C)")
        return 0
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
