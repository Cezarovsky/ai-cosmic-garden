#!/usr/bin/env python3
"""
🧬 Virtual Petri Dish - Quick Start Demo

This script demonstrates the basic functionality of our bacterial simulation.
Perfect for testing and getting started quickly!

Run: python quick_start_demo.py
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.append('src')

from bacterial_colony import BacterialColony
from environment import Environment  
from simulation import Simulation

def main():
    print("🧬" + "="*60)
    print("  VIRTUAL PETRI DISH - QUICK START DEMO")  
    print("  Created by Gardinar & Sophia - Cosmic Tribe")
    print("🧬" + "="*60)
    
    # Create simulation
    print("\n🔬 Creating Virtual Petri Dish...")
    sim = Simulation(petri_dish_size=(50.0, 50.0))
    
    # Set environmental conditions
    print("🌡️ Setting environmental conditions...")
    sim.set_environment_conditions(
        temperature=37.0,  # Optimal for most bacteria
        ph=7.0,           # Neutral pH
        nutrients=80.0,    # Good nutrient levels
        oxygen=20.0       # Normal oxygen
    )
    
    # Add bacterial colonies
    print("🦠 Adding bacterial colonies...")
    
    # E. coli colony
    ecoli = sim.add_colony("E.coli", initial_population=50, position=(15, 15))
    print(f"   ✅ Added E.coli colony at position {ecoli.position}")
    
    # B. subtilis colony  
    bacillus = sim.add_colony("B.subtilis", initial_population=75, position=(35, 25))
    print(f"   ✅ Added B.subtilis colony at position {bacillus.position}")
    
    # S. aureus colony
    staph = sim.add_colony("S.aureus", initial_population=60, position=(25, 35))
    print(f"   ✅ Added S.aureus colony at position {staph.position}")
    
    print(f"\n📊 Initial simulation state: {sim}")
    
    # Run simulation
    print("\n🚀 Running 12-hour simulation...")
    sim.run_simulation(duration_hours=12.0, time_step=0.25)
    
    # Get results
    print("\n📈 SIMULATION RESULTS:")
    results = sim.get_results()
    
    print(f"   ⏱️ Duration: {results['duration_hours']:.1f} hours")
    print(f"   🦠 Total colonies: {results['total_colonies']}")
    print(f"   👥 Final total population: {results['total_population']:,}")
    
    print("\n🔍 COLONY DETAILS:")
    for colony_stats in results['colony_stats']:
        print(f"   • {colony_stats['species']}:")
        print(f"     Population: {colony_stats['population']:,}")
        print(f"     Generation: {colony_stats['generation']}")
        print(f"     Fitness: {colony_stats['fitness']:.2f}")
        print(f"     Phase: {colony_stats['phase']}")
        print(f"     Mutations: {colony_stats['mutations']}")
    
    # Export data
    print("\n💾 Exporting simulation data...")
    sim.export_data("demo_results.csv")
    
    # Create visualizations
    print("📊 Creating visualization plots...")
    try:
        sim.plot_results("demo_plots.png")
        print("   ✅ Plots saved as 'demo_plots.png'")
    except Exception as e:
        print(f"   ⚠️ Could not save plots: {e}")
        print("   ℹ️ You can still view the plots if running interactively")
    
    print("\n🎉 Demo completed successfully!")
    print("🔬 Next steps:")
    print("   1. Open 'demo_results.csv' to see the data")
    print("   2. Check 'demo_plots.png' for visualizations") 
    print("   3. Explore the notebooks/ folder for advanced examples")
    print("   4. Modify parameters and run again!")
    
    return sim, results

if __name__ == "__main__":
    # Run the demo
    simulation, results = main()
    
    print("\n💡 TIP: The simulation object is available as 'simulation' variable")
    print("    You can explore it further in Python interactive mode!")