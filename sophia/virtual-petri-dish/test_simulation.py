#!/usr/bin/env python3
"""
Test Simulation Class
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from simulation import Simulation

def main():
    print("🧬 Testing Full Simulation Class")
    print("="*50)
    
    # Create simulation
    sim = Simulation(petri_dish_size=(50, 50))
    print(f"✅ Simulation created: {sim}")
    
    # Add colonies
    e_coli_id = sim.add_colony("E.coli", initial_population=50, position=(10, 10))
    b_sub_id = sim.add_colony("B.subtilis", initial_population=30, position=(40, 40))
    print(f"✅ Added E.coli colony: {e_coli_id}")
    print(f"✅ Added B.subtilis colony: {b_sub_id}")
    
    # Environmental changes during simulation
    env_changes = [
        {"time": 2.0, "conditions": {"temperature": 42}},
        {"time": 4.0, "conditions": {"ph": 6.5, "nutrients": 50}}
    ]
    
    # Run simulation
    print("\n🚀 Running 6-hour multi-colony simulation...")
    sim.run_simulation(
        duration_hours=6.0,
        time_step=0.5,
        environmental_changes=env_changes,
        enable_interactions=True
    )
    
    # Show results
    print(f"\n📊 Simulation Summary:")
    summary = sim.get_simulation_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Full simulation test completed!")

if __name__ == "__main__":
    main()