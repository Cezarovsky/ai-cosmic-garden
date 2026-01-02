"""
Simple Live Bacterial Animation Test

Test real-time animation without emoji dependencies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from src.simulation import Simulation
import time
import threading
import queue

class SimpleAnimator:
    """Simple real-time bacterial animation."""
    
    def __init__(self):
        # Create small simulation
        self.sim = Simulation(
            petri_dish_size=(40, 40),
            environment_params={'temperature': 30, 'ph': 7.0, 'nutrients': 50},
            enable_optimization=True
        )
        
        # Add colonies
        self.sim.add_colony("E.coli", 2000, (10, 10))
        self.sim.add_colony("B.subtilis", 1500, (30, 30))
        self.sim.add_colony("S.aureus", 1800, (20, 35))
        
        # Setup plot
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.fig.patch.set_facecolor('black')
        
        # Data
        self.time_data = []
        self.pop_data = {c.id: [] for c in self.sim.colonies}
        self.current_time = 0.0
        self.running = True
        
        # Colors
        self.colors = ['red', 'cyan', 'yellow']
        
    def simulate(self):
        """Run simulation in background."""
        while self.running and self.current_time < 5.0:
            # Optimization
            if self.sim.optimizer:
                result = self.sim.optimizer.optimize_environment(
                    self.sim.colonies, self.sim.environment, self.current_time
                )
                
                if result.get("optimizations"):
                    for action in result["optimizations"]:
                        if action["type"] == "cannibalistic_population_loss":
                            print(f"t={self.current_time:.1f}h: CANNIBALISM DETECTED!")
            
            # Update colonies
            for colony in self.sim.colonies:
                if colony.population > 0:
                    colony.simulate_growth(self.sim.environment, 0.1)
            
            # Interactions
            if len(self.sim.colonies) > 1:
                self.sim._simulate_interactions()
            
            self.current_time += 0.1
            time.sleep(0.05)  # Fast animation
    
    def animate(self, frame):
        """Update animation."""
        # Clear plots
        self.ax1.clear()
        self.ax2.clear()
        
        # Plot 1: Petri dish
        self.ax1.set_xlim(0, 40)
        self.ax1.set_ylim(0, 40)
        self.ax1.set_aspect('equal')
        self.ax1.set_title(f'Petri Dish - t={self.current_time:.1f}h')
        self.ax1.set_facecolor('darkblue')
        
        # Draw colonies
        for i, colony in enumerate(self.sim.colonies):
            if colony.population > 0:
                size = min(8, max(1, np.log10(colony.population + 1)))
                
                # Health check for cannibalism
                health = 'normal'
                if self.sim.optimizer:
                    health_dict = self.sim.optimizer.assess_colony_health(
                        self.sim.colonies, self.sim.environment
                    )
                    health = health_dict.get(colony.id, 'normal')
                
                color = 'darkred' if health.name == 'CANNIBALISTIC' else self.colors[i % 3]
                
                circle = plt.Circle(colony.position, size, 
                                  color=color, alpha=0.7)
                self.ax1.add_patch(circle)
                
                # Population label
                self.ax1.text(colony.position[0], colony.position[1], 
                            f'{colony.population:,}', ha='center', va='center',
                            fontsize=8, color='white', weight='bold')
        
        # Plot 2: Population growth
        self.time_data.append(self.current_time)
        for i, colony in enumerate(self.sim.colonies):
            if colony.id not in self.pop_data:
                self.pop_data[colony.id] = []
            self.pop_data[colony.id].append(max(1, colony.population))
        
        # Only plot recent data
        recent_points = min(50, len(self.time_data))
        recent_time = self.time_data[-recent_points:]
        
        for i, colony in enumerate(self.sim.colonies):
            if colony.id in self.pop_data and self.pop_data[colony.id]:
                recent_pop = self.pop_data[colony.id][-recent_points:]
                self.ax2.semilogy(recent_time, recent_pop, 
                                color=self.colors[i % 3], linewidth=2,
                                label=colony.species.name.split()[0])
        
        self.ax2.set_title('Population Growth')
        self.ax2.set_xlabel('Time (hours)')
        self.ax2.set_ylabel('Population (log)')
        self.ax2.legend()
        self.ax2.grid(True, alpha=0.3)
        
        # Show environment info
        env = self.sim.environment
        info_text = f'Temp: {env.conditions.temperature:.1f}C, pH: {env.conditions.ph:.2f}, Nutrients: {env.conditions.nutrients:.1f}'
        self.ax1.text(0.02, 0.98, info_text, transform=self.ax1.transAxes,
                     fontsize=9, color='white', verticalalignment='top')
        
        plt.tight_layout()
        
    def start(self):
        """Start animation."""
        print("Starting live bacterial animation...")
        print("Watch for population growth and cannibalistic behavior!")
        
        # Start simulation thread
        sim_thread = threading.Thread(target=self.simulate)
        sim_thread.daemon = True
        sim_thread.start()
        
        # Start animation
        ani = animation.FuncAnimation(self.fig, self.animate, interval=100, cache_frame_data=False)
        
        try:
            plt.show()
        except KeyboardInterrupt:
            self.running = False
            print("\nAnimation stopped.")

def main():
    print("LIVE BACTERIAL GROWTH ANIMATION")
    print("=" * 40)
    print("Real-time simulation of bacterial colonies")
    print("Red = E.coli, Cyan = B.subtilis, Yellow = S.aureus")
    print("Dark red = Cannibalistic colony!")
    print("=" * 40)
    
    animator = SimpleAnimator()
    animator.start()

if __name__ == "__main__":
    main()