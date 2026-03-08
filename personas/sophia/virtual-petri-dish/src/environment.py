"""
Environment Module

Models the environmental conditions affecting bacterial growth.
"""

from typing import Dict, Any
import numpy as np
from dataclasses import dataclass


@dataclass
class EnvironmentalConditions:
    """Environmental parameters affecting bacterial growth."""
    temperature: float = 37.0  # Celsius
    ph: float = 7.0           # pH level
    nutrients: float = 100.0   # Nutrient concentration (arbitrary units)
    oxygen: float = 20.0       # Oxygen percentage
    salinity: float = 0.9      # Salt concentration (%)
    pressure: float = 1.0      # Atmospheric pressure (atm)


class Environment:
    """
    Simulation environment for bacterial colonies.
    
    Manages environmental parameters and their effects on bacterial growth.
    """
    
    def __init__(self, **conditions):
        """
        Initialize environment with specified conditions.
        
        Args:
            **conditions: Environmental parameters (temperature, ph, nutrients, etc.)
        """
        self.conditions = EnvironmentalConditions(**conditions)
        self.history = []
    
    def update_conditions(self, **new_conditions) -> None:
        """Update environmental conditions."""
        for key, value in new_conditions.items():
            if hasattr(self.conditions, key):
                setattr(self.conditions, key, value)
        
        # Record history
        self.history.append({
            'timestamp': len(self.history),
            'conditions': vars(self.conditions).copy()
        })
    
    def get_growth_multiplier(self) -> float:
        """
        Calculate growth rate multiplier based on environmental conditions.
        
        Returns:
            Growth multiplier (0.0 to 2.0)
        """
        # Temperature effect (optimal around 37°C)
        temp_effect = self._gaussian_effect(self.conditions.temperature, 37.0, 10.0)
        
        # pH effect (optimal around 7.0)
        ph_effect = self._gaussian_effect(self.conditions.ph, 7.0, 1.5)
        
        # Nutrient effect (linear up to saturation)
        nutrient_effect = min(self.conditions.nutrients / 50.0, 2.0)
        
        # Oxygen effect (assuming aerobic bacteria)
        oxygen_effect = min(self.conditions.oxygen / 10.0, 1.0)
        
        # Combined effect
        multiplier = temp_effect * ph_effect * nutrient_effect * oxygen_effect
        return max(0.01, min(2.0, multiplier))  # Clamp between 0.01 and 2.0
    
    def _gaussian_effect(self, value: float, optimal: float, std_dev: float) -> float:
        """Calculate Gaussian effect around optimal value."""
        return np.exp(-((value - optimal) ** 2) / (2 * std_dev ** 2))
    
    def get_stress_level(self) -> float:
        """
        Calculate environmental stress level (0 = no stress, 1 = maximum stress).
        
        Returns:
            Stress level between 0.0 and 1.0
        """
        # More sensitive stress calculation
        temp_stress = min(1.0, abs(self.conditions.temperature - 37.0) / 20.0)  # Stress at ±20°C
        ph_stress = min(1.0, abs(self.conditions.ph - 7.0) / 2.0)              # Stress at ±2 pH units
        nutrient_stress = max(0, (50.0 - self.conditions.nutrients) / 50.0)    # Stress below 50 nutrients
        oxygen_stress = max(0, (15.0 - self.conditions.oxygen) / 15.0)         # Stress below 15% oxygen
        
        # Take maximum stress (most limiting factor)
        max_stress = max(temp_stress, ph_stress, nutrient_stress, oxygen_stress)
        
        # Average stress for overall environmental pressure
        avg_stress = (temp_stress + ph_stress + nutrient_stress + oxygen_stress) / 4.0
        
        # Combine max and average for realistic stress response
        return min(1.0, max_stress * 0.7 + avg_stress * 0.3)
    
    def consume_nutrients(self, amount: float) -> None:
        """Consume nutrients from environment."""
        self.conditions.nutrients = max(0, self.conditions.nutrients - amount)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export environment state to dictionary."""
        return {
            'conditions': vars(self.conditions),
            'growth_multiplier': self.get_growth_multiplier(),
            'stress_level': self.get_stress_level()
        }
    
    def __repr__(self) -> str:
        return f"Environment(temp={self.conditions.temperature}°C, pH={self.conditions.ph}, nutrients={self.conditions.nutrients})"