"""
Test Enhanced Evolution System

Verify that colonies now properly evolve, mutate, and differentiate over time.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.simulation import Simulation

def test_realistic_evolution():
    """Test the enhanced mutation and evolution system."""
    print("🧬 TESTING ENHANCED BACTERIAL EVOLUTION")
    print("=" * 50)
    
    # Create simulation with challenging conditions
    sim = Simulation(
        petri_dish_size=(60, 60),
        environment_params={
            'temperature': 32.0,  # Slightly stressful
            'ph': 6.5,
            'nutrients': 80.0
        },
        enable_optimization=True
    )
    
    # Add colonies
    colony_ids = []
    colony_ids.append(sim.add_colony("E.coli", 4000, (20, 20)))
    colony_ids.append(sim.add_colony("B.subtilis", 3000, (40, 40)))  
    colony_ids.append(sim.add_colony("S.aureus", 3500, (30, 15)))
    
    print(f"Initial Conditions:")
    for i, colony in enumerate(sim.colonies):
        print(f"  Colony {i+1} ({colony.species.name}):")
        print(f"    Population: {colony.population:,}")
        print(f"    Fitness: {colony.fitness:.3f}")
        print(f"    Generation: {colony.generation}")
        print(f"    Max growth rate: {colony.species.max_growth_rate:.3f}")
        print(f"    Nutrient efficiency: {colony.species.nutrient_efficiency:.3f}")
    
    # Environmental stressors to trigger evolution
    environmental_changes = [
        {'time': 1.5, 'conditions': {'temperature': 42.0}},  # Heat shock
        {'time': 3.0, 'conditions': {'ph': 5.0}},           # Acid stress  
        {'time': 4.5, 'conditions': {'nutrients': 25.0}},   # Starvation
        {'time': 6.0, 'conditions': {'temperature': 15.0}}, # Cold shock
    ]
    
    print(f"\n🚨 Environmental Stressors Planned:")
    for change in environmental_changes:
        conditions = change['conditions']
        stress_type = list(conditions.keys())[0]
        value = list(conditions.values())[0]
        print(f"  t={change['time']}h: {stress_type} → {value}")
    
    print(f"\n🔬 Running 8-hour evolution simulation...")
    
    # Run simulation
    sim.run_simulation(
        duration_hours=8.0,
        time_step=0.1,
        environmental_changes=environmental_changes,
        enable_interactions=True
    )
    
    print(f"\n" + "=" * 50)
    print("🧬 EVOLUTION RESULTS ANALYSIS")
    print("=" * 50)
    
    # Analyze final results
    print(f"\nFINAL COLONY STATUS:")
    total_mutations = 0
    
    for i, colony in enumerate(sim.colonies):
        print(f"\n🦠 Colony {i+1} ({colony.species.name}):")
        print(f"    Final Population: {colony.population:,}")
        print(f"    Fitness: {colony.fitness:.3f} ({'↑' if colony.fitness > 1.0 else '↓' if colony.fitness < 1.0 else '→'})")
        print(f"    Generation: {colony.generation}")
        print(f"    Age: {colony.age_hours:.1f} hours")
        print(f"    Current Phase: {colony.current_phase.value.upper()}")
        
        # Evolution details
        print(f"    🧬 EVOLUTION DETAILS:")
        print(f"      Mutations: {len(colony.mutations)}")
        print(f"      Growth Rate: {colony.species.max_growth_rate:.3f} (evolved)")
        print(f"      Nutrient Efficiency: {colony.species.nutrient_efficiency:.3f}")
        print(f"      Temp Range: {colony.species.temperature_range}")
        print(f"      pH Range: {colony.species.ph_range}")
        
        if colony.mutations:
            print(f"      🔬 MUTATIONS ACQUIRED:")
            for j, mutation in enumerate(colony.mutations[-5:]):  # Show last 5
                effect = mutation.get('fitness_effect', 1.0)
                effect_str = f"{effect:.3f}" if 'fitness_effect' in mutation else "unknown"
                source = mutation.get('source', 'natural')
                print(f"        {j+1}. {mutation['type']} (effect: {effect_str}, {source})")
                print(f"           at gen {mutation['generation']}, t={mutation['time']:.1f}h")
        
        total_mutations += len(colony.mutations)
    
    # Summary statistics
    summary = sim.get_simulation_summary()
    
    print(f"\n📊 EVOLUTION STATISTICS:")
    print(f"  Total mutations across all colonies: {total_mutations}")
    print(f"  Average fitness: {summary['average_fitness']:.3f}")
    print(f"  Population growth factor: {summary['final_population'] / summary['initial_population']:.2f}x")
    print(f"  Species diversity: {summary['species_count']} species survived")
    
    if 'optimization_report' in summary:
        opt = summary['optimization_report']
        print(f"  Optimization interventions: {opt['total_optimization_actions']}")
        print(f"  Emergency situations: {opt['emergency_interventions']}")
    
    # Check if evolution worked
    fitness_values = [c.fitness for c in sim.colonies]
    generation_values = [c.generation for c in sim.colonies]
    
    print(f"\n✅ EVOLUTION VERIFICATION:")
    print(f"  Fitness diversity: {max(fitness_values) - min(fitness_values):.3f}")
    print(f"  Max generation reached: {max(generation_values)}")
    print(f"  Total evolutionary events: {total_mutations}")
    
    if max(generation_values) > 0 and total_mutations > 0:
        print(f"  🎉 SUCCESS: Colonies evolved and differentiated!")
    else:
        print(f"  ⚠️  LIMITED: Evolution may need stronger selective pressure")
    
    # Export detailed results
    df = sim.get_results_dataframe()
    df.to_csv("evolution_test_results.csv", index=False)
    print(f"\n📁 Detailed evolution data exported to: evolution_test_results.csv")
    
    return sim

if __name__ == "__main__":
    test_sim = test_realistic_evolution()