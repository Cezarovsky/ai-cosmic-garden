"""
Main Simulation Module

Orchestrates bacterial growth simulations in virtual petri dishes.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json

try:
    from .bacterial_colony import BacterialColony
    from .environment import Environment
    from .colony_optimizer import ColonyOptimizer
except ImportError:
    # Fallback for direct execution
    from bacterial_colony import BacterialColony
    from environment import Environment
    from colony_optimizer import ColonyOptimizer


class Simulation:
    """
    Main simulation class for Virtual Petri Dish.
    
    Manages multiple bacterial colonies and environmental conditions over time.
    """
    
    def __init__(self, 
                 petri_dish_size: tuple = (100.0, 100.0),
                 environment_params: Optional[Dict] = None,
                 enable_optimization: bool = True):
        """
        Initialize simulation.
        
        Args:
            petri_dish_size: (width, height) of virtual petri dish in mm
            environment_params: Initial environmental conditions
            enable_optimization: Enable intelligent colony optimization
        """
        self.petri_dish_size = petri_dish_size
        self.colonies: List[BacterialColony] = []
        self.environment = Environment(**(environment_params or {}))
        
        # Initialize optimizer
        dish_area = (petri_dish_size[0] * petri_dish_size[1]) / 100  # Convert mm² to cm²
        self.optimizer = ColonyOptimizer(
            petri_dish_area=dish_area,
            enable_logging=True
        ) if enable_optimization else None
        
        self.simulation_time = 0.0
        self.time_step = 0.1  # hours
        self.history = []
        
        # Metadata
        self.start_time = None
        self.end_time = None
        self.simulation_id = None
    
    def add_colony(self, 
                   species: str,
                   initial_population: int = 100, 
                   position: Optional[tuple] = None,
                   **kwargs) -> str:
        """
        Add bacterial colony to simulation.
        
        Args:
            species: Species name
            initial_population: Starting population size
            position: (x, y) position, random if None
            **kwargs: Additional colony parameters
            
        Returns:
            Colony ID
        """
        if position is None:
            position = (
                np.random.uniform(10, self.petri_dish_size[0] - 10),
                np.random.uniform(10, self.petri_dish_size[1] - 10)
            )
        
        colony = BacterialColony(
            species=species,
            initial_population=initial_population,
            position=position,
            **kwargs
        )
        
        self.colonies.append(colony)
        return colony.id
    
    def run_simulation(self, 
                       duration_hours: float,
                       time_step: float = 0.1,
                       environmental_changes: Optional[List[Dict]] = None,
                       enable_interactions: bool = True) -> None:
        """
        Run the bacterial growth simulation.
        
        Args:
            duration_hours: Total simulation time in hours
            time_step: Time step for simulation updates in hours
            environmental_changes: List of timed environmental changes
            enable_interactions: Whether to model colony interactions
        """
        self.start_time = datetime.now()
        self.simulation_id = f"sim_{int(self.start_time.timestamp())}"
        self.time_step = time_step
        
        environmental_changes = environmental_changes or []
        change_schedule = {change['time']: change for change in environmental_changes}
        
        print(f"Starting simulation: {self.simulation_id}")
        print(f"Duration: {duration_hours} hours, Time step: {time_step} hours")
        print(f"Colonies: {len(self.colonies)}")
        
        # Main simulation loop
        steps = int(duration_hours / time_step)
        for step in range(steps):
            current_time = step * time_step
            self.simulation_time = current_time
            
            # Apply environmental changes (fix float comparison)
            for change_time in change_schedule:
                if abs(current_time - change_time) < self.time_step / 2:
                    changes = change_schedule[change_time]
                    self.environment.update_conditions(**changes.get('conditions', {}))
                    print(f"t={current_time:.1f}h: Environmental change applied")
                    break
            
            # Apply intelligent optimization
            if self.optimizer:
                optimization_result = self.optimizer.optimize_environment(
                    self.colonies, self.environment, current_time
                )
                
                # Log significant interventions
                if optimization_result.get("optimizations"):
                    for action in optimization_result["optimizations"]:
                        if action["type"] in ["emergency_nutrient_boost", "cannibalistic_population_loss"]:
                            print(f"t={current_time:.1f}h: {action['type']} - {action.get('reason', 'optimization')}")
            
            # Update each colony
            for colony in self.colonies:
                if colony.population > 0:
                    colony.simulate_growth(self.environment, time_step)
            
            # Model colony interactions
            if enable_interactions and len(self.colonies) > 1:
                self._simulate_interactions()
            
            # Record simulation state
            if step % (int(1.0 / time_step)) == 0:  # Record every hour
                self._record_state()
            
            # Progress update (fix division by zero)
            progress_interval = max(1, steps // 10)
            if step % progress_interval == 0:
                progress = (step / steps) * 100
                total_population = sum(c.population for c in self.colonies)
                print(f"Progress: {progress:.0f}% - Total population: {total_population:,}")
        
        self.end_time = datetime.now()
        print(f"Simulation completed in {(self.end_time - self.start_time).total_seconds():.1f} seconds")
    
    def _simulate_interactions(self) -> None:
        """Simulate interactions between colonies."""
        for i, colony1 in enumerate(self.colonies):
            for colony2 in self.colonies[i+1:]:
                if colony1.population > 0 and colony2.population > 0:
                    # Determine interaction type based on species
                    if colony1.species.name == colony2.species.name:
                        interaction_type = "cooperation"
                    else:
                        interaction_type = "competition"
                    
                    colony1.interact_with_colony(colony2, interaction_type)
                    colony2.interact_with_colony(colony1, interaction_type)
    
    def _record_state(self) -> None:
        """Record current simulation state."""
        state = {
            'time': self.simulation_time,
            'environment': self.environment.to_dict(),
            'colonies': [colony.get_colony_stats() for colony in self.colonies],
            'total_population': sum(c.population for c in self.colonies),
            'active_colonies': sum(1 for c in self.colonies if c.population > 0)
        }
        self.history.append(state)
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """Get simulation results as pandas DataFrame."""
        records = []
        for state in self.history:
            base_record = {
                'time': state['time'],
                'total_population': state['total_population'],
                'active_colonies': state['active_colonies'],
                'temperature': state['environment']['conditions']['temperature'],
                'ph': state['environment']['conditions']['ph'],
                'nutrients': state['environment']['conditions']['nutrients'],
                'growth_multiplier': state['environment']['growth_multiplier'],
                'stress_level': state['environment']['stress_level']
            }
            
            # Add colony-specific data
            for colony_stats in state['colonies']:
                record = base_record.copy()
                record.update({
                    'colony_id': colony_stats['id'],
                    'species': colony_stats['species'],
                    'population': colony_stats['population'],
                    'generation': colony_stats['generation'],
                    'fitness': colony_stats['fitness'],
                    'phase': colony_stats['phase'],
                    'mutations': colony_stats['mutations']
                })
                records.append(record)
        
        return pd.DataFrame(records)
    
    def plot_population_growth(self, save_path: Optional[str] = None) -> None:
        """Plot population growth over time."""
        df = self.get_results_dataframe()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Population by species
        for species in df['species'].unique():
            species_data = df[df['species'] == species].groupby('time')['population'].sum()
            ax1.plot(species_data.index, species_data.values, 
                    marker='o', label=species, linewidth=2, markersize=4)
        
        ax1.set_xlabel('Time (hours)')
        ax1.set_ylabel('Population')
        ax1.set_title('Bacterial Population Growth Over Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')
        
        # Environmental conditions
        env_data = df.drop_duplicates('time')
        ax2_twin = ax2.twinx()
        
        ax2.plot(env_data['time'], env_data['temperature'], 'r-', label='Temperature (°C)')
        ax2.plot(env_data['time'], env_data['ph'], 'b-', label='pH')
        ax2_twin.plot(env_data['time'], env_data['nutrients'], 'g-', label='Nutrients')
        
        ax2.set_xlabel('Time (hours)')
        ax2.set_ylabel('Temperature / pH')
        ax2_twin.set_ylabel('Nutrients')
        ax2.set_title('Environmental Conditions')
        
        # Combine legends
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def export_results(self, file_path: str, format: str = 'csv') -> None:
        """
        Export simulation results to file.
        
        Args:
            file_path: Output file path
            format: Export format ('csv', 'json', 'excel')
        """
        if format.lower() == 'csv':
            df = self.get_results_dataframe()
            df.to_csv(file_path, index=False)
        
        elif format.lower() == 'json':
            export_data = {
                'metadata': {
                    'simulation_id': self.simulation_id,
                    'start_time': self.start_time.isoformat() if self.start_time else None,
                    'end_time': self.end_time.isoformat() if self.end_time else None,
                    'duration_hours': self.simulation_time,
                    'petri_dish_size': self.petri_dish_size,
                    'num_colonies': len(self.colonies)
                },
                'results': self.history
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        
        elif format.lower() == 'excel':
            df = self.get_results_dataframe()
            df.to_excel(file_path, index=False, sheet_name='Results')
        
        print(f"Results exported to: {file_path}")
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the simulation."""
        if not self.history:
            return {"error": "No simulation data available"}
        
        df = self.get_results_dataframe()
        
        summary = {
            'simulation_id': self.simulation_id,
            'duration_hours': self.simulation_time,
            'initial_population': df[df['time'] == 0]['population'].sum(),
            'final_population': df[df['time'] == df['time'].max()]['population'].sum(),
            'peak_population': df['population'].max(),
            'species_count': df['species'].nunique(),
            'total_mutations': df['mutations'].sum(),
            'average_fitness': df['fitness'].mean(),
            'nutrient_depletion': self.environment.conditions.nutrients
        }
        
        # Add optimization report if available
        if self.optimizer:
            summary['optimization_report'] = self.optimizer.get_optimization_report()
        
        return summary
    
    def __repr__(self) -> str:
        return f"Simulation(colonies={len(self.colonies)}, time={self.simulation_time:.1f}h)"