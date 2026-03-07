"""
Real-time Animation Module

Creates live animations of bacterial colony growth, competition, and cannibalistic behavior.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from typing import List, Dict, Any, Optional
import time
from matplotlib.patches import Circle
from matplotlib.colors import to_rgba
import threading
import queue

try:
    from .simulation import Simulation
    from .bacterial_colony import BacterialColony, GrowthPhase
    from .colony_optimizer import ColonyHealth
except ImportError:
    from simulation import Simulation
    from bacterial_colony import BacterialColony, GrowthPhase
    from colony_optimizer import ColonyHealth


class RealTimeAnimator:
    """
    Real-time animator for bacterial colony growth and interactions.
    
    Shows live visualization of bacterial growth, cannibalism, and environmental changes.
    """
    
    def __init__(self, 
                 simulation: Simulation,
                 animation_speed: float = 1.0,
                 update_interval: int = 100):
        """
        Initialize real-time animator.
        
        Args:
            simulation: Simulation object to animate
            animation_speed: Speed multiplier for animation (1.0 = real-time)
            update_interval: Update interval in milliseconds
        """
        self.simulation = simulation
        self.animation_speed = animation_speed
        self.update_interval = update_interval
        
        # Animation state
        self.current_time = 0.0
        self.max_duration = 8.0  # hours
        self.time_step = 0.1
        self.is_running = False
        self.simulation_thread = None
        
        # Data queues for thread-safe communication
        self.data_queue = queue.Queue()
        self.event_queue = queue.Queue()
        
        # Visual settings
        self.colors = {
            'E.coli': '#FF6B6B',          # Red
            'Escherichia coli': '#FF6B6B',
            'B.subtilis': '#4ECDC4',      # Cyan
            'Bacillus subtilis': '#4ECDC4',
            'S.aureus': '#FFE66D',        # Yellow
            'Staphylococcus aureus': '#FFE66D',
            'default': '#95E1D3'          # Green
        }
        
        # Setup matplotlib
        plt.style.use('dark_background')
        self.fig, self.axes = plt.subplots(2, 2, figsize=(15, 12))
        self.fig.patch.set_facecolor('black')
        
        # Initialize plots
        self._setup_plots()
        
    def _setup_plots(self):
        """Setup the four animation plots."""
        # Plot 1: Petri dish view (top-left)
        self.ax_petri = self.axes[0, 0]
        self.ax_petri.set_xlim(0, self.simulation.petri_dish_size[0])
        self.ax_petri.set_ylim(0, self.simulation.petri_dish_size[1])
        self.ax_petri.set_aspect('equal')
        self.ax_petri.set_title('🧫 Petri Dish View', color='white', fontsize=14)
        self.ax_petri.set_facecolor('#001122')
        
        # Draw petri dish border
        dish_circle = Circle((50, 50), 45, fill=False, color='white', linewidth=2)
        self.ax_petri.add_patch(dish_circle)
        
        # Plot 2: Population growth (top-right)
        self.ax_pop = self.axes[0, 1]
        self.ax_pop.set_title('📈 Population Growth', color='white', fontsize=14)
        self.ax_pop.set_xlabel('Time (hours)', color='white')
        self.ax_pop.set_ylabel('Population (log scale)', color='white')
        self.ax_pop.set_yscale('log')
        self.ax_pop.grid(True, alpha=0.3)
        
        # Plot 3: Environmental conditions (bottom-left)
        self.ax_env = self.axes[1, 0]
        self.ax_env.set_title('🌡️ Environment', color='white', fontsize=14)
        self.ax_env.set_xlabel('Time (hours)', color='white')
        self.ax_env.set_ylabel('Conditions', color='white')
        self.ax_env.grid(True, alpha=0.3)
        
        # Plot 4: Colony health status (bottom-right)
        self.ax_health = self.axes[1, 1]
        self.ax_health.set_title('🩺 Colony Health', color='white', fontsize=14)
        self.ax_health.axis('off')
        
        # Initialize data storage
        self.time_data = []
        self.population_data = {colony.id: [] for colony in self.simulation.colonies}
        self.environment_data = {'temperature': [], 'ph': [], 'nutrients': []}
        self.health_data = {colony.id: [] for colony in self.simulation.colonies}
        
        # Colony visual elements
        self.colony_circles = {}
        self.colony_labels = {}
        
    def _simulate_step(self):
        """Run one simulation step in background thread."""
        try:
            while self.is_running and self.current_time < self.max_duration:
                # Apply optimization
                if self.simulation.optimizer:
                    optimization_result = self.simulation.optimizer.optimize_environment(
                        self.simulation.colonies, self.simulation.environment, self.current_time
                    )
                    
                    # Send optimization events to queue
                    if optimization_result.get("optimizations"):
                        for action in optimization_result["optimizations"]:
                            if action["type"] in ["emergency_nutrient_boost", "cannibalistic_population_loss"]:
                                self.event_queue.put({
                                    'type': 'optimization_event',
                                    'time': self.current_time,
                                    'action': action
                                })
                
                # Update colonies
                for colony in self.simulation.colonies:
                    if colony.population > 0:
                        colony.simulate_growth(self.simulation.environment, self.time_step)
                
                # Model interactions
                if len(self.simulation.colonies) > 1:
                    self.simulation._simulate_interactions()
                
                # Collect data for visualization
                frame_data = {
                    'time': self.current_time,
                    'colonies': [],
                    'environment': {
                        'temperature': self.simulation.environment.conditions.temperature,
                        'ph': self.simulation.environment.conditions.ph,
                        'nutrients': self.simulation.environment.conditions.nutrients
                    }
                }
                
                # Get colony health if optimizer exists
                colony_health = {}
                if self.simulation.optimizer:
                    colony_health = self.simulation.optimizer.assess_colony_health(
                        self.simulation.colonies, self.simulation.environment
                    )
                
                for colony in self.simulation.colonies:
                    frame_data['colonies'].append({
                        'id': colony.id,
                        'species': colony.species.name,
                        'population': colony.population,
                        'position': colony.position,
                        'phase': colony.current_phase.value,
                        'fitness': colony.fitness,
                        'generation': colony.generation,
                        'health': colony_health.get(colony.id, ColonyHealth.HEALTHY).value
                    })
                
                # Send data to animation thread
                self.data_queue.put(frame_data)
                
                self.current_time += self.time_step
                time.sleep(self.time_step / self.animation_speed)
                
        except Exception as e:
            print(f"Simulation error: {e}")
            self.is_running = False
    
    def _update_frame(self, frame):
        """Update animation frame."""
        # Process all available data
        latest_data = None
        while not self.data_queue.empty():
            try:
                latest_data = self.data_queue.get_nowait()
            except queue.Empty:
                break
        
        if latest_data is None:
            return []
        
        # Process events
        events = []
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                events.append(event)
            except queue.Empty:
                break
        
        # Update data arrays
        current_time = latest_data['time']
        self.time_data.append(current_time)
        
        # Update environment data
        for key, value in latest_data['environment'].items():
            self.environment_data[key].append(value)
        
        # Clear previous plots (except petri dish setup)
        self.ax_petri.clear()
        self.ax_petri.set_xlim(0, self.simulation.petri_dish_size[0])
        self.ax_petri.set_ylim(0, self.simulation.petri_dish_size[1])
        self.ax_petri.set_aspect('equal')
        self.ax_petri.set_title(f'🧫 Petri Dish - t={current_time:.1f}h', color='white', fontsize=14)
        self.ax_petri.set_facecolor('#001122')
        
        # Draw petri dish border
        dish_circle = Circle((50, 50), 45, fill=False, color='white', linewidth=2)
        self.ax_petri.add_patch(dish_circle)
        
        # Update colonies
        for colony_data in latest_data['colonies']:
            colony_id = colony_data['id']
            species = colony_data['species']
            population = colony_data['population']
            position = colony_data['position']
            health = colony_data['health']
            phase = colony_data['phase']
            
            # Update population data
            if colony_id not in self.population_data:
                self.population_data[colony_id] = []
            self.population_data[colony_id].append(max(1, population))
            
            # Update health data
            if colony_id not in self.health_data:
                self.health_data[colony_id] = []
            self.health_data[colony_id].append(health)
            
            # Calculate colony size based on population (log scale)
            if population > 0:
                size = min(15, max(2, np.log10(population + 1) * 2))
                
                # Color based on health status
                base_color = self.colors.get(species, self.colors['default'])
                if health == 'cannibalistic':
                    color = '#8B0000'  # Dark red
                    edge_color = '#FF0000'  # Bright red
                    linewidth = 3
                elif health == 'critical':
                    color = '#FF4500'  # Orange red
                    edge_color = '#FF6347'
                    linewidth = 2
                elif health == 'stressed':
                    color = '#FFD700'  # Gold
                    edge_color = base_color
                    linewidth = 1
                else:
                    color = base_color
                    edge_color = 'white'
                    linewidth = 1
                
                # Draw colony
                colony_circle = Circle(position, size, 
                                     color=color, alpha=0.7,
                                     edgecolor=edge_color, linewidth=linewidth)
                self.ax_petri.add_patch(colony_circle)
                
                # Add population label
                self.ax_petri.text(position[0], position[1], f'{population:,}',
                                  ha='center', va='center', fontsize=8, color='white',
                                  weight='bold')
                
                # Add species label
                species_short = species.split()[0] if ' ' in species else species
                self.ax_petri.text(position[0], position[1] - size - 3, species_short,
                                  ha='center', va='center', fontsize=7, color='white')
        
        # Update population plot
        self.ax_pop.clear()
        self.ax_pop.set_title('📈 Population Growth', color='white', fontsize=14)
        self.ax_pop.set_xlabel('Time (hours)', color='white')
        self.ax_pop.set_ylabel('Population (log scale)', color='white')
        self.ax_pop.set_yscale('log')
        self.ax_pop.grid(True, alpha=0.3)
        
        for colony_data in latest_data['colonies']:
            colony_id = colony_data['id']
            species = colony_data['species']
            if colony_id in self.population_data and self.population_data[colony_id]:
                color = self.colors.get(species, self.colors['default'])
                self.ax_pop.plot(self.time_data[-len(self.population_data[colony_id]):],
                               self.population_data[colony_id],
                               color=color, linewidth=2, label=species.split()[0])
        
        self.ax_pop.legend()
        
        # Update environment plot
        self.ax_env.clear()
        self.ax_env.set_title('🌡️ Environment', color='white', fontsize=14)
        self.ax_env.set_xlabel('Time (hours)', color='white')
        self.ax_env.set_ylabel('Conditions', color='white')
        self.ax_env.grid(True, alpha=0.3)
        
        if self.time_data and self.environment_data['temperature']:
            self.ax_env.plot(self.time_data, self.environment_data['temperature'],
                           'r-', label='Temperature (°C)', linewidth=2)
            ax_env2 = self.ax_env.twinx()
            ax_env2.plot(self.time_data, self.environment_data['ph'],
                        'b-', label='pH', linewidth=2)
            ax_env2.plot(self.time_data, self.environment_data['nutrients'],
                        'g-', label='Nutrients', linewidth=2)
            
            self.ax_env.legend(loc='upper left')
            ax_env2.legend(loc='upper right')
        
        # Update health status
        self.ax_health.clear()
        self.ax_health.set_title('🩺 Colony Health Status', color='white', fontsize=14)
        self.ax_health.axis('off')
        
        y_pos = 0.9
        for colony_data in latest_data['colonies']:
            species = colony_data['species']
            population = colony_data['population']
            health = colony_data['health']
            phase = colony_data['phase']
            fitness = colony_data['fitness']
            generation = colony_data['generation']
            
            # Health status emoji
            health_emoji = {
                'thriving': '🌟',
                'healthy': '💚', 
                'stressed': '😰',
                'critical': '🆘',
                'cannibalistic': '🧟‍♂️'
            }.get(health, '❓')
            
            # Phase emoji
            phase_emoji = {
                'lag': '😴',
                'exponential': '🚀',
                'stationary': '⏸️',
                'death': '💀'
            }.get(phase, '❓')
            
            status_text = f"{health_emoji} {species.split()[0]}: {population:,} bacteria\n" \
                         f"   {phase_emoji} {phase.title()} | Gen {generation} | Fit {fitness:.2f}"
            
            color = self.colors.get(species, self.colors['default'])
            self.ax_health.text(0.05, y_pos, status_text,
                              transform=self.ax_health.transAxes,
                              fontsize=10, color=color, weight='bold',
                              verticalalignment='top')
            y_pos -= 0.25
        
        # Show events
        if events:
            event_text = "🚨 RECENT EVENTS:\n"
            for event in events[-3:]:  # Show last 3 events
                if event['type'] == 'optimization_event':
                    action = event['action']
                    if action['type'] == 'cannibalistic_population_loss':
                        event_text += f"💀 Cannibalism detected!\n"
                    elif action['type'] == 'emergency_nutrient_boost':
                        event_text += f"🍽️ Emergency feeding!\n"
            
            self.ax_health.text(0.05, 0.15, event_text,
                              transform=self.ax_health.transAxes,
                              fontsize=9, color='red', weight='bold',
                              verticalalignment='top')
        
        plt.tight_layout()
        return []
    
    def start_animation(self, duration_hours: float = 8.0):
        """Start the real-time animation."""
        self.max_duration = duration_hours
        self.is_running = True
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self._simulate_step)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        # Start animation
        self.ani = animation.FuncAnimation(
            self.fig, self._update_frame,
            interval=self.update_interval,
            blit=False,
            cache_frame_data=False
        )
        
        plt.show()
    
    def stop_animation(self):
        """Stop the animation."""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)


def create_live_animation(petri_size: tuple = (50, 50),
                         animation_speed: float = 2.0) -> RealTimeAnimator:
    """
    Create and start a live bacterial growth animation.
    
    Args:
        petri_size: Size of petri dish (width, height) in mm
        animation_speed: Animation speed multiplier
        
    Returns:
        RealTimeAnimator instance
    """
    print("🎬 Creating Live Bacterial Animation...")
    
    # Create simulation with small dish for faster overcrowding
    sim = Simulation(
        petri_dish_size=petri_size,
        environment_params={
            'temperature': 25.0,
            'ph': 7.0,
            'nutrients': 40.0
        },
        enable_optimization=True
    )
    
    # Add competing colonies
    print("Adding bacterial colonies:")
    
    sim.add_colony("E.coli", initial_population=3000, position=(15, 15))
    print("  ✓ E.coli (red) - Fast growing")
    
    sim.add_colony("B.subtilis", initial_population=2000, position=(35, 35))
    print("  ✓ B.subtilis (cyan) - Spore forming")
    
    sim.add_colony("S.aureus", initial_population=2500, position=(25, 10))
    print("  ✓ S.aureus (yellow) - Resistant")
    
    # Create animator
    animator = RealTimeAnimator(sim, animation_speed=animation_speed)
    
    print(f"\n🎥 Starting {8.0}h animation at {animation_speed}x speed...")
    print("Watch for:")
    print("  🌟 = Thriving colonies")
    print("  😰 = Stressed colonies") 
    print("  🧟‍♂️ = Cannibalistic colonies")
    print("  💀 = Dying colonies")
    
    return animator


if __name__ == "__main__":
    # Create and start animation
    animator = create_live_animation(animation_speed=3.0)
    animator.start_animation(duration_hours=8.0)