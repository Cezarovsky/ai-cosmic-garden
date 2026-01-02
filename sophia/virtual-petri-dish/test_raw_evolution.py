"""
Test Raw Evolution Without Optimizer

Force bacterial evolution without AI optimization interference.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.simulation import Simulation

def test_raw_evolution():
    """Test evolution without optimizer interference."""
    print("🧬 TESTING RAW BACTERIAL EVOLUTION (NO OPTIMIZER)")
    print("=" * 55)
    
    # Create simulation WITHOUT optimization
    sim = Simulation(
        petri_dish_size=(40, 40),  # Smaller for crowding
        environment_params={
            'temperature': 40.0,  # Start with stress
            'ph': 5.5,           # Acidic stress
            'nutrients': 30.0    # Limited nutrients
        },
        enable_optimization=False  # NO AI HELP!
    )
    
    # Add colonies
    sim.add_colony("E.coli", 6000, (15, 15))
    sim.add_colony("B.subtilis", 4000, (25, 25))  
    sim.add_colony("S.aureus", 5000, (20, 30))
    
    print(f"Initial Conditions (STRESSFUL!):")
    print(f"  Temperature: {sim.environment.conditions.temperature}°C (HIGH STRESS)")
    print(f"  pH: {sim.environment.conditions.ph} (ACIDIC STRESS)")
    print(f"  Nutrients: {sim.environment.conditions.nutrients} (LIMITED)")
    print(f"  Stress Level: {sim.environment.get_stress_level():.3f}")
    
    for i, colony in enumerate(sim.colonies):
        print(f"  Colony {i+1} ({colony.species.name}): {colony.population:,}")
    
    # Harsh environmental changes
    environmental_changes = [
        {'time': 2.0, 'conditions': {'temperature': 50.0}},  # EXTREME HEAT
        {'time': 4.0, 'conditions': {'ph': 4.0}},           # EXTREME ACID
        {'time': 6.0, 'conditions': {'nutrients': 5.0}},    # STARVATION
    ]
    
    print(f"\n🔥 EXTREME STRESSORS:")
    for change in environmental_changes:
        conditions = change['conditions']
        stress_type = list(conditions.keys())[0]
        value = list(conditions.values())[0]
        print(f"  t={change['time']}h: {stress_type} → {value} (SURVIVAL CHALLENGE!)")
    
    print(f"\n⚡ Running 6-hour SURVIVAL simulation (no AI help)...")
    
    # Run harsh simulation
    sim.run_simulation(
        duration_hours=6.0,
        time_step=0.1,
        environmental_changes=environmental_changes,
        enable_interactions=True
    )
    
    print(f"\n" + "=" * 55)
    print("🧬 SURVIVAL & EVOLUTION RESULTS")
    print("=" * 55)
    
    total_mutations = 0
    survivors = 0
    
    for i, colony in enumerate(sim.colonies):
        if colony.population > 0:
            survivors += 1
            
        print(f"\n🦠 Colony {i+1} ({colony.species.name}):")
        print(f"    Status: {'SURVIVED' if colony.population > 0 else 'EXTINCT'}")
        print(f"    Final Population: {colony.population:,}")
        print(f"    Fitness: {colony.fitness:.3f}")
        print(f"    Generation: {colony.generation}")
        print(f"    Phase: {colony.current_phase.value.upper()}")
        
        if colony.mutations:
            print(f"    🧬 SURVIVAL MUTATIONS ({len(colony.mutations)}):")
            for j, mutation in enumerate(colony.mutations):
                effect = mutation.get('fitness_effect', 1.0)
                print(f"      {j+1}. {mutation['type']} (effect: {effect:.3f})")
                print(f"         Gen {mutation['generation']}, t={mutation['time']:.1f}h")
        else:
            print(f"    🧬 No mutations acquired")
        
        total_mutations += len(colony.mutations)
    
    print(f"\n📊 SURVIVAL STATISTICS:")
    print(f"  Survivors: {survivors}/3 colonies")
    print(f"  Total mutations: {total_mutations}")
    
    if survivors > 0:
        summary = sim.get_simulation_summary()
        print(f"  Population change: {summary['initial_population']:,} → {summary['final_population']:,}")
        print(f"  Average fitness: {summary.get('average_fitness', 0):.3f}")
        
        if total_mutations > 0:
            print(f"  🎉 SUCCESS: Harsh conditions triggered {total_mutations} mutations!")
        else:
            print(f"  😵 No evolution despite extreme stress - may need longer simulation")
    else:
        print(f"  💀 TOTAL EXTINCTION: All colonies died!")
    
    print(f"\n📁 Raw evolution data: evolution_raw_results.csv")
    sim.export_results("evolution_raw_results.csv")
    
    return sim

if __name__ == "__main__":
    test_raw_evolution()