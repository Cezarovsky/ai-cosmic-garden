#!/usr/bin/env python3
"""
Quick Start Demo - Virtual Petri Dish
Test basic functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bacterial_colony import BacterialColony
from environment import Environment

def main():
    print("🧬 Virtual Petri Dish - Quick Start Demo")
    print("="*50)
    
    # Create environment
    print("📊 Creating environment...")
    env = Environment(temperature=37, ph=7.0, nutrients=100)
    print(f"   Environment: {env}")
    
    # Create bacterial colony
    print("\n🦠 Creating E.coli colony...")
    colony = BacterialColony("E.coli", initial_population=100)
    print(f"   Colony: {colony}")
    
    # Run simulation
    print("\n⚡ Running 6-hour simulation...")
    for hour in range(6):
        colony.simulate_growth(env, time_hours=1.0)
        stats = colony.get_colony_stats()
        print(f"   Hour {hour+1}: Population={stats['population']:,}, Phase={stats['phase']}")
    
    print(f"\n🎯 Final Results:")
    final_stats = colony.get_colony_stats()
    for key, value in final_stats.items():
        if key not in ['id', 'position']:
            print(f"   {key}: {value}")
    
    print("\n✅ Demo completed successfully!")
    print("🚀 Ready to build amazing simulations!")

if __name__ == "__main__":
    main()