"""
Test script for the intelligent colony optimization system.
Demonstrates prevention of cannibalistic behavior through optimal environmental control.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.simulation import Simulation
from src.colony_optimizer import ColonyHealth

def test_optimization_system():
    """Test the colony optimization system with overpopulation scenarios."""
    print("🧬 Testing Intelligent Colony Optimization System")
    print("=" * 60)
    
    # Create simulation with optimization enabled
    sim = Simulation(
        petri_dish_size=(50.0, 50.0),  # Smaller dish for faster overcrowding
        environment_params={
            'temperature': 25.0,
            'ph': 7.0,
            'nutrients': 30.0  # Start with limited nutrients
        },
        enable_optimization=True
    )
    
    # Add multiple colonies that will compete for space
    print("Adding bacterial colonies:")
    
    # E.coli - fast growing
    colony1_id = sim.add_colony(
        species="E.coli",
        initial_population=5000,
        position=(10, 10)
    )
    print(f"  ✓ E.coli colony: {colony1_id[:8]}... (5,000 bacteria)")
    
    # B.subtilis - spore forming
    colony2_id = sim.add_colony(
        species="B.subtilis", 
        initial_population=3000,
        position=(30, 30)
    )
    print(f"  ✓ B.subtilis colony: {colony2_id[:8]}... (3,000 bacteria)")
    
    # S.aureus - antibiotic resistant
    colony3_id = sim.add_colony(
        species="S.aureus",
        initial_population=4000,
        position=(20, 40)
    )
    print(f"  ✓ S.aureus colony: {colony3_id[:8]}... (4,000 bacteria)")
    
    print(f"\nInitial conditions:")
    print(f"  Temperature: {sim.environment.conditions.temperature}°C")
    print(f"  pH: {sim.environment.conditions.ph}")
    print(f"  Nutrients: {sim.environment.conditions.nutrients}")
    print(f"  Total population: {sum(c.population for c in sim.colonies):,}")
    
    # Environmental changes that will stress colonies
    environmental_changes = [
        {
            'time': 2.0,
            'conditions': {'temperature': 35.0}  # Heat stress
        },
        {
            'time': 4.0, 
            'conditions': {'nutrients': 10.0}   # Nutrient depletion
        },
        {
            'time': 6.0,
            'conditions': {'ph': 5.5}           # pH stress
        }
    ]
    
    print("\nRunning 8-hour simulation with optimization...")
    print("Environmental stressors will be applied at t=2h, 4h, 6h")
    print("\nSimulation progress:")
    
    # Run simulation with optimization
    sim.run_simulation(
        duration_hours=8.0,
        time_step=0.1,
        environmental_changes=environmental_changes,
        enable_interactions=True
    )
    
    # Analyze results
    print("\n" + "=" * 60)
    print("🔬 OPTIMIZATION RESULTS ANALYSIS")
    print("=" * 60)
    
    summary = sim.get_simulation_summary()
    
    print(f"\nPopulation Analysis:")
    print(f"  Initial: {summary['initial_population']:,} bacteria")
    print(f"  Final: {summary['final_population']:,} bacteria")
    print(f"  Peak: {summary['peak_population']:,} bacteria")
    print(f"  Growth factor: {summary['final_population'] / summary['initial_population']:.2f}x")
    
    print(f"\nEvolutionary Progress:")
    print(f"  Species survived: {summary['species_count']}")
    print(f"  Total mutations: {summary['total_mutations']}")
    print(f"  Average fitness: {summary['average_fitness']:.3f}")
    
    print(f"\nFinal Environment:")
    print(f"  Temperature: {sim.environment.conditions.temperature:.1f}°C")
    print(f"  pH: {sim.environment.conditions.ph:.2f}")
    print(f"  Nutrients remaining: {sim.environment.conditions.nutrients:.1f}")
    
    # Optimization report
    if 'optimization_report' in summary:
        opt_report = summary['optimization_report']
        print(f"\n🤖 OPTIMIZATION SYSTEM PERFORMANCE:")
        print(f"  Optimization cycles: {opt_report['total_optimization_cycles']}")
        print(f"  Total actions taken: {opt_report['total_optimization_actions']}")
        print(f"  Cannibalistic incidents: {opt_report['cannibalistic_incidents']}")
        print(f"  Emergency interventions: {opt_report['emergency_interventions']}")
        
        if opt_report['action_breakdown']:
            print(f"\n  Action breakdown:")
            for action_type, count in opt_report['action_breakdown'].items():
                print(f"    - {action_type}: {count}")
    
    # Colony health assessment
    if sim.optimizer:
        final_health = sim.optimizer.assess_colony_health(sim.colonies, sim.environment)
        print(f"\n🩺 FINAL COLONY HEALTH:")
        for i, colony in enumerate(sim.colonies):
            health_status = final_health.get(colony.id, ColonyHealth.CRITICAL)
            print(f"  Colony {i+1} ({colony.species.name}): {health_status.value.upper()}")
            print(f"    Population: {colony.population:,}")
            print(f"    Generation: {colony.generation}")
            print(f"    Fitness: {colony.fitness:.3f}")
    
    # Create visualization
    print(f"\n📊 Generating visualization...")
    plot_path = "optimization_test_results.png"
    sim.plot_population_growth(save_path=plot_path)
    
    # Export detailed data
    export_path = "optimization_test_data.csv"
    sim.export_results(export_path, format='csv')
    print(f"📁 Detailed data exported to: {export_path}")
    
    print(f"\n✅ Optimization test completed successfully!")
    
    # Check if cannibalism was prevented
    final_populations = [c.population for c in sim.colonies]
    max_population = max(final_populations) if final_populations else 0
    
    if max_population < sim.optimizer.target.cannibalism_threshold:
        print(f"🎉 SUCCESS: Cannibalism prevented! Max population: {max_population:,}")
    else:
        print(f"⚠️  WARNING: Some colonies may have become cannibalistic (max: {max_population:,})")
    
    return sim

if __name__ == "__main__":
    test_sim = test_optimization_system()