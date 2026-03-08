"""
Launch Live Bacterial Animation

Start real-time animation of bacterial colony growth, competition, and cannibalism.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.real_time_animator import create_live_animation

def main():
    """Launch the live bacterial growth animation."""
    print("🧬 VIRTUAL PETRI DISH - LIVE ANIMATION 🎬")
    print("=" * 60)
    print("Real-time bacterial colony growth simulation")
    print("Watch colonies grow, compete, and potentially become cannibalistic!")
    print("=" * 60)
    
    # Animation settings
    ANIMATION_SPEED = 4.0  # 4x real-time for faster demo
    PETRI_SIZE = (40, 40)  # Small dish for faster overcrowding
    DURATION = 6.0         # 6 hours simulation
    
    print(f"⚙️  Settings:")
    print(f"   Petri dish: {PETRI_SIZE[0]}x{PETRI_SIZE[1]}mm")
    print(f"   Animation speed: {ANIMATION_SPEED}x")
    print(f"   Duration: {DURATION} hours")
    
    print(f"\n🎭 Visual Legend:")
    print(f"   🔴 Red circles = E.coli (fast growing)")
    print(f"   🟢 Cyan circles = B.subtilis (spore forming)")  
    print(f"   🟡 Yellow circles = S.aureus (antibiotic resistant)")
    print(f"   ")
    print(f"   Circle size = Population (bigger = more bacteria)")
    print(f"   Circle edge = Health status:")
    print(f"     • White edge = Healthy")
    print(f"     • Red edge = Cannibalistic!")
    print(f"     • Orange edge = Critical condition")
    
    print(f"\n🚨 Events to watch for:")
    print(f"   💀 Cannibalism detected!")
    print(f"   🍽️ Emergency feeding intervention")
    print(f"   🌡️ Temperature/pH optimization")
    
    input(f"\n🎬 Press ENTER to start the live animation...")
    
    try:
        # Create and start animation
        animator = create_live_animation(
            petri_size=PETRI_SIZE,
            animation_speed=ANIMATION_SPEED
        )
        
        animator.start_animation(duration_hours=DURATION)
        
    except KeyboardInterrupt:
        print(f"\n🛑 Animation stopped by user")
    except Exception as e:
        print(f"❌ Animation error: {e}")
        print(f"Make sure you have matplotlib and other dependencies installed:")
        print(f"pip install matplotlib numpy pandas")

if __name__ == "__main__":
    main()