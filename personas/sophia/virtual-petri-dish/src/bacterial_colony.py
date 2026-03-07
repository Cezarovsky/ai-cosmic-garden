"""
Bacterial Colony Module

Models bacterial colonies with growth, evolution, and interaction capabilities.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import uuid


class GrowthPhase(Enum):
    """Bacterial growth phases."""
    LAG = "lag"
    EXPONENTIAL = "exponential"  
    STATIONARY = "stationary"
    DEATH = "death"


@dataclass
class BacterialSpecies:
    """Bacterial species characteristics."""
    name: str
    max_growth_rate: float = 0.5    # per hour
    carrying_capacity: int = 1000000  # max population
    nutrient_efficiency: float = 1.0  # nutrient consumption rate
    temperature_range: tuple = (20.0, 45.0)  # viable temperature range
    ph_range: tuple = (5.0, 9.0)    # viable pH range
    resistance_genes: List[str] = None
    
    def __post_init__(self):
        if self.resistance_genes is None:
            self.resistance_genes = []


class BacterialColony:
    """
    Represents a bacterial colony with growth dynamics and evolution.
    
    Simulates population growth, environmental adaptation, and genetic changes.
    """
    
    def __init__(self, 
                 species: str,
                 initial_population: int = 100,
                 position: tuple = (0.0, 0.0),
                 custom_species: Optional[BacterialSpecies] = None):
        """
        Initialize bacterial colony.
        
        Args:
            species: Species name or predefined species
            initial_population: Starting population size
            position: (x, y) position in petri dish
            custom_species: Custom species parameters
        """
        self.id = str(uuid.uuid4())
        self.population = initial_population
        self.position = position
        self.age_hours = 0.0
        self.generation = 0
        
        # Set species characteristics
        if custom_species:
            self.species = custom_species
        else:
            self.species = self._get_predefined_species(species)
        
        # Growth tracking
        self.growth_history = []
        self.current_phase = GrowthPhase.LAG
        self.phase_start_time = 0.0
        
        # Genetic tracking
        self.mutations = []
        self.fitness = 1.0
        
        # Resource tracking
        self.nutrient_consumption = 0.0
        
    def _get_predefined_species(self, species_name: str) -> BacterialSpecies:
        """Get predefined species characteristics."""
        species_db = {
            "E.coli": BacterialSpecies(
                name="Escherichia coli",
                max_growth_rate=0.7,
                carrying_capacity=2000000,
                nutrient_efficiency=1.2,
                temperature_range=(15.0, 50.0),
                ph_range=(6.0, 8.0)
            ),
            "B.subtilis": BacterialSpecies(
                name="Bacillus subtilis", 
                max_growth_rate=0.5,
                carrying_capacity=1500000,
                nutrient_efficiency=0.9,
                temperature_range=(10.0, 55.0),
                ph_range=(5.5, 8.5),
                resistance_genes=["spore_formation"]
            ),
            "S.aureus": BacterialSpecies(
                name="Staphylococcus aureus",
                max_growth_rate=0.6,
                carrying_capacity=1800000,
                nutrient_efficiency=1.1,
                temperature_range=(7.0, 48.0),
                ph_range=(4.8, 9.3),
                resistance_genes=["methicillin_resistance"]
            )
        }
        
        return species_db.get(species_name, BacterialSpecies(name=species_name))
    
    def simulate_growth(self, environment, time_hours: float = 1.0) -> None:
        """
        Simulate bacterial growth for specified time period.
        
        Args:
            environment: Environment object with conditions
            time_hours: Simulation time in hours
        """
        initial_population = self.population
        growth_multiplier = environment.get_growth_multiplier()
        
        # Update growth phase
        self._update_growth_phase(environment)
        
        # Calculate growth based on current phase
        if self.current_phase == GrowthPhase.LAG:
            growth_rate = 0.1 * self.species.max_growth_rate
        elif self.current_phase == GrowthPhase.EXPONENTIAL:
            growth_rate = self.species.max_growth_rate * growth_multiplier
        elif self.current_phase == GrowthPhase.STATIONARY:
            growth_rate = 0.0
        else:  # DEATH
            growth_rate = -0.2
        
        # Apply logistic growth model
        carrying_capacity = self.species.carrying_capacity * growth_multiplier
        logistic_factor = 1 - (self.population / carrying_capacity)
        effective_growth_rate = growth_rate * logistic_factor * self.fitness
        
        # Update population
        growth = self.population * effective_growth_rate * time_hours
        self.population = max(0, int(self.population + growth))
        
        # Consume nutrients
        nutrient_consumption = (self.population * self.species.nutrient_efficiency * 
                               time_hours * 0.001)  # Scale factor
        environment.consume_nutrients(nutrient_consumption)
        self.nutrient_consumption += nutrient_consumption
        
        # Update age and generation
        self.age_hours += time_hours
        
        # Generation advances based on population doubling and time
        if growth > 0:
            # Track generation progress as a float, then increment when >= 1.0
            if not hasattr(self, '_generation_progress'):
                self._generation_progress = 0.0
            
            # Generation based on growth rate and time
            generation_increment = time_hours * max(0.2, effective_growth_rate)
            self._generation_progress += generation_increment
            
            # Advance generation when progress >= 1.0
            while self._generation_progress >= 1.0:
                self.generation += 1
                self._generation_progress -= 1.0
            
            # Additional generation for significant population growth
            if self.population > initial_population * 2.0:  # Population doubled
                self.generation += 1
        
        # Check for mutations
        self._check_mutations(environment, time_hours)
        
        # Record history
        self.growth_history.append({
            'time': self.age_hours,
            'population': self.population,
            'phase': self.current_phase.value,
            'growth_rate': effective_growth_rate,
            'generation': self.generation,
            'fitness': self.fitness
        })
    
    def _update_growth_phase(self, environment) -> None:
        """Update current growth phase based on conditions."""
        stress = environment.get_stress_level()
        time_in_phase = self.age_hours - self.phase_start_time
        
        if self.current_phase == GrowthPhase.LAG:
            if time_in_phase > 2.0 and stress < 0.5:  # Exit lag after 2 hours if not stressed
                self._change_phase(GrowthPhase.EXPONENTIAL)
        
        elif self.current_phase == GrowthPhase.EXPONENTIAL:
            if (self.population > 0.8 * self.species.carrying_capacity or 
                environment.conditions.nutrients < 10):
                self._change_phase(GrowthPhase.STATIONARY)
        
        elif self.current_phase == GrowthPhase.STATIONARY:
            if stress > 0.8 or environment.conditions.nutrients < 5:
                self._change_phase(GrowthPhase.DEATH)
    
    def _change_phase(self, new_phase: GrowthPhase) -> None:
        """Change growth phase and record time."""
        self.current_phase = new_phase
        self.phase_start_time = self.age_hours
    
    def _check_mutations(self, environment, time_hours: float) -> None:
        """Check for beneficial mutations under stress."""
        stress = environment.get_stress_level()
        # Base mutation rate + stress-induced mutations
        base_mutation_rate = 0.05  # 5% chance per hour (much higher for visible evolution)
        stress_mutation_rate = stress * 0.1   # Additional stress mutations
        mutation_probability = (base_mutation_rate + stress_mutation_rate) * time_hours
        
        # Simplified but more effective mutation system
        if np.random.random() < mutation_probability:
            mutation_type = np.random.choice([
                "temperature_adaptation",
                "ph_tolerance", 
                "nutrient_efficiency",
                "antibiotic_resistance",
                "growth_rate_boost",
                "stress_resistance",
                "competitive_advantage",
                "metabolic_efficiency"
            ])
            
            # Fitness effect varies
            fitness_change = np.random.uniform(0.95, 1.15)  # -5% to +15%
            
            self.mutations.append({
                'type': mutation_type,
                'time': self.age_hours,
                'generation': self.generation,
                'fitness_effect': fitness_change
            })
            
            # Apply fitness benefit/cost
            self.fitness *= fitness_change
            
            # Specific mutations affect species characteristics
            if mutation_type == "temperature_adaptation":
                # Expand temperature tolerance
                temp_range = self.species.temperature_range
                self.species.temperature_range = (temp_range[0] - 1, temp_range[1] + 1)
            elif mutation_type == "nutrient_efficiency":
                self.species.nutrient_efficiency *= np.random.uniform(0.85, 0.95)  # More efficient
            elif mutation_type == "growth_rate_boost":
                self.species.max_growth_rate *= np.random.uniform(1.05, 1.20)  # Faster growth
            elif mutation_type == "ph_tolerance":
                ph_range = self.species.ph_range
                self.species.ph_range = (ph_range[0] - 0.2, ph_range[1] + 0.2)
            
            # Ensure fitness stays within reasonable bounds
            self.fitness = max(0.1, min(3.0, self.fitness))
            
            print(f"🧬 MUTATION: {self.species.name} acquired {mutation_type} (fitness: {fitness_change:.3f})")
    
    def interact_with_colony(self, other_colony: 'BacterialColony', 
                           interaction_type: str = "competition") -> None:
        """
        Model interaction with another bacterial colony.
        
        Args:
            other_colony: Another BacterialColony instance
            interaction_type: Type of interaction (competition, cooperation, predation)
        """
        distance = np.sqrt((self.position[0] - other_colony.position[0])**2 + 
                          (self.position[1] - other_colony.position[1])**2)
        
        # Interaction strength decreases with distance
        interaction_strength = max(0, 1.0 - distance / 10.0)
        
        if interaction_type == "competition":
            # More intense competition with random outcomes
            competition_factor = other_colony.population / (self.population + other_colony.population)
            base_reduction = competition_factor * interaction_strength * np.random.uniform(0.05, 0.25)
            
            # Factor in fitness differences
            fitness_advantage = self.fitness / (other_colony.fitness + 0.1)
            if fitness_advantage < 1.0:  # We're weaker
                fitness_reduction = base_reduction * (2.0 - fitness_advantage)
            else:  # We're stronger
                fitness_reduction = base_reduction * 0.5
            
            self.fitness = max(0.1, self.fitness - fitness_reduction)
        
        elif interaction_type == "cooperation":
            # Variable cooperation benefits
            cooperation_bonus = interaction_strength * np.random.uniform(0.02, 0.15)
            self.fitness *= (1.0 + cooperation_bonus)
            
            # Chance of beneficial gene transfer
            if np.random.random() < 0.1 * interaction_strength:
                if other_colony.mutations:
                    # Copy a beneficial mutation
                    beneficial_mutation = np.random.choice(other_colony.mutations)
                    if beneficial_mutation not in self.mutations:
                        self.mutations.append({
                            **beneficial_mutation,
                            'time': self.age_hours,
                            'source': 'horizontal_transfer'
                        })
    
    def get_colony_stats(self) -> Dict[str, Any]:
        """Get current colony statistics."""
        return {
            'id': self.id,
            'species': self.species.name,
            'population': self.population,
            'age_hours': self.age_hours,
            'generation': self.generation,
            'fitness': self.fitness,
            'phase': self.current_phase.value,
            'mutations': len(self.mutations),
            'position': self.position,
            'nutrient_consumption': self.nutrient_consumption
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Export growth history to pandas DataFrame."""
        return pd.DataFrame(self.growth_history)
    
    def __repr__(self) -> str:
        return f"BacterialColony({self.species.name}, pop={self.population}, gen={self.generation})"