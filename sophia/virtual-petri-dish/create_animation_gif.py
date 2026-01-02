"""
Create Animated GIF of Bacterial Growth

Generate animated GIF showing bacterial colony growth and cannibalistic behavior.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from src.simulation import Simulation
from matplotlib.patches import Circle

def create_bacterial_gif():
    """Create animated GIF of bacterial growth."""
    print("Creating animated GIF of bacterial growth...")
    
    # Create simulation
    sim = Simulation(
        petri_dish_size=(50, 50),
        environment_params={
            'temperature': 28.0,
            'ph': 7.0, 
            'nutrients': 60.0
        },
        enable_optimization=True
    )
    
    # Add colonies
    sim.add_colony("E.coli", 3000, (15, 15))
    sim.add_colony("B.subtilis", 2000, (35, 35)) 
    sim.add_colony("S.aureus", 2500, (25, 40))
    
    print(f"Initial population: {sum(c.population for c in sim.colonies):,}")
    
    # Run full simulation first
    print("Running 6-hour simulation...")
    sim.run_simulation(
        duration_hours=6.0,
        time_step=0.1,
        environmental_changes=[
            {'time': 3.0, 'conditions': {'nutrients': 20.0}},  # Stress at 3h
            {'time': 4.5, 'conditions': {'temperature': 38.0}}  # Heat stress
        ]
    )
    
    # Get results
    df = sim.get_results_dataframe()
    times = sorted(df['time'].unique())
    
    print(f"Simulation complete. Creating {len(times)} frames...")
    
    # Setup animation
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.patch.set_facecolor('black')
    
    colors = {'E.coli': 'red', 'Escherichia coli': 'red',
              'B.subtilis': 'cyan', 'Bacillus subtilis': 'cyan',
              'S.aureus': 'yellow', 'Staphylococcus aureus': 'yellow'}
    
    def animate(frame_idx):
        if frame_idx >= len(times):
            return
            
        current_time = times[frame_idx]
        frame_data = df[df['time'] == current_time]
        
        # Clear all plots
        for ax in [ax1, ax2, ax3, ax4]:
            ax.clear()
        
        # Plot 1: Petri dish view
        ax1.set_xlim(0, 50)
        ax1.set_ylim(0, 50)
        ax1.set_aspect('equal')
        ax1.set_title(f'Petri Dish - t={current_time:.1f}h', color='white')
        ax1.set_facecolor('#001122')
        
        # Draw dish border
        dish_circle = Circle((25, 25), 23, fill=False, color='white', linewidth=2)
        ax1.add_patch(dish_circle)
        
        # Get colony health if available
        colony_health = {}
        if sim.optimizer:
            colony_health = sim.optimizer.assess_colony_health(sim.colonies, sim.environment)
        
        # Draw colonies
        for _, colony_data in frame_data.iterrows():
            pop = colony_data['population']
            if pop > 0:
                # Find colony position
                colony = next(c for c in sim.colonies if c.id == colony_data['colony_id'])
                pos = colony.position
                
                # Size based on population
                size = min(12, max(1.5, np.log10(pop + 1) * 1.5))
                
                # Color based on health
                base_color = colors.get(colony_data['species'], 'green')
                health = colony_health.get(colony_data['colony_id'])
                
                if health and health.name == 'CANNIBALISTIC':
                    color = 'darkred'
                    edge_color = 'red'
                    linewidth = 3
                elif health and health.name == 'CRITICAL':
                    color = 'orange'
                    edge_color = 'red'
                    linewidth = 2
                else:
                    color = base_color
                    edge_color = 'white'
                    linewidth = 1
                
                # Draw colony
                circle = Circle(pos, size, color=color, alpha=0.8,
                              edgecolor=edge_color, linewidth=linewidth)
                ax1.add_patch(circle)
                
                # Population label
                ax1.text(pos[0], pos[1], f'{pop:,}', ha='center', va='center',
                        fontsize=8, color='white', weight='bold')
                
                # Species label
                species_short = colony_data['species'].split()[0]
                ax1.text(pos[0], pos[1]-size-2, species_short, ha='center', va='center',
                        fontsize=7, color='white')
        
        # Plot 2: Population growth over time
        ax2.set_title('Population Growth', color='white')
        ax2.set_xlabel('Time (hours)', color='white')
        ax2.set_ylabel('Population (log)', color='white')
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3)
        
        # Plot population trends up to current time
        current_data = df[df['time'] <= current_time]
        for species in current_data['species'].unique():
            species_data = current_data[current_data['species'] == species]
            species_pop = species_data.groupby('time')['population'].sum()
            ax2.plot(species_pop.index, species_pop.values,
                    color=colors.get(species, 'green'), linewidth=2,
                    label=species.split()[0])
        
        ax2.legend()
        
        # Plot 3: Environmental conditions
        ax3.set_title('Environmental Conditions', color='white')
        ax3.set_xlabel('Time (hours)', color='white')
        ax3.set_ylabel('Conditions', color='white')
        ax3.grid(True, alpha=0.3)
        
        env_data = current_data.drop_duplicates('time')[['time', 'temperature', 'ph', 'nutrients']]
        if not env_data.empty:
            ax3.plot(env_data['time'], env_data['temperature'], 'r-', label='Temp (°C)', linewidth=2)
            ax3_twin = ax3.twinx()
            ax3_twin.plot(env_data['time'], env_data['ph'], 'b-', label='pH', linewidth=2)
            ax3_twin.plot(env_data['time'], env_data['nutrients'], 'g-', label='Nutrients', linewidth=2)
            
            ax3.legend(loc='upper left')
            ax3_twin.legend(loc='upper right')
        
        # Plot 4: Health status summary
        ax4.set_title('Colony Health Status', color='white')
        ax4.axis('off')
        
        total_pop = frame_data['population'].sum()
        active_colonies = len(frame_data[frame_data['population'] > 0])
        
        status_text = f"Time: {current_time:.1f} hours\n"
        status_text += f"Total Population: {total_pop:,}\n"
        status_text += f"Active Colonies: {active_colonies}\n\n"
        
        y_pos = 0.8
        for _, colony_data in frame_data.iterrows():
            if colony_data['population'] > 0:
                species = colony_data['species'].split()[0]
                pop = colony_data['population']
                phase = colony_data['phase']
                fitness = colony_data['fitness']
                
                health = colony_health.get(colony_data['colony_id'])
                health_status = health.value if health else 'unknown'
                
                # Health emoji replacement
                health_symbol = {
                    'thriving': '[THRIV]',
                    'healthy': '[HEAL]',
                    'stressed': '[STRESS]', 
                    'critical': '[CRIT]',
                    'cannibalistic': '[CANN!]'
                }.get(health_status, '[?]')
                
                colony_text = f"{health_symbol} {species}: {pop:,}\n"
                colony_text += f"   Phase: {phase} | Fit: {fitness:.2f}"
                
                color = colors.get(colony_data['species'], 'white')
                ax4.text(0.05, y_pos, colony_text,
                        transform=ax4.transAxes, fontsize=10,
                        color=color, weight='bold', verticalalignment='top')
                y_pos -= 0.25
        
        plt.tight_layout()
    
    # Create animation (sample every 5th frame for reasonable file size)
    sample_frames = range(0, len(times), 5)
    print(f"Creating animation with {len(sample_frames)} frames...")
    
    ani = animation.FuncAnimation(fig, animate, frames=len(sample_frames),
                                interval=400, repeat=True, cache_frame_data=False)
    
    # Save as GIF
    gif_path = "bacterial_growth_animation.gif"
    print(f"Saving animation to {gif_path}...")
    
    try:
        ani.save(gif_path, writer='pillow', fps=3, dpi=80)
        print(f"✅ Animation saved successfully: {gif_path}")
        
        # File size
        file_size = os.path.getsize(gif_path) / (1024 * 1024)
        print(f"📁 File size: {file_size:.1f} MB")
        
    except Exception as e:
        print(f"❌ Error saving animation: {e}")
        print("Try: pip install pillow")
    
    plt.show()

if __name__ == "__main__":
    create_bacterial_gif()