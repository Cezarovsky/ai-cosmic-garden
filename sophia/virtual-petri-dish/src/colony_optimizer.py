"""
Colony Optimizer Module

Intelligent optimization system for maintaining healthy bacterial colonies
and preventing cannibalistic behavior through optimal environmental control.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum
import logging

from .bacterial_colony import BacterialColony, GrowthPhase
from .environment import Environment


class ColonyHealth(Enum):
    """Colony health status."""
    THRIVING = "thriving"      # Optimal conditions
    HEALTHY = "healthy"        # Good conditions
    STRESSED = "stressed"      # Suboptimal conditions
    CRITICAL = "critical"      # Near death/cannibalism
    CANNIBALISTIC = "cannibalistic"  # Overcrowded, eating each other


@dataclass
class OptimizationTarget:
    """Target parameters for colony optimization."""
    max_population_density: int = 50000  # bacteria per cm²
    target_growth_rate: float = 0.3     # optimal growth rate
    stress_threshold: float = 0.3        # maximum acceptable stress
    nutrient_buffer: float = 20.0        # minimum nutrient level
    cannibalism_threshold: float = 80000 # population threshold for cannibalism


class ColonyOptimizer:
    """
    Intelligent system for optimizing environmental conditions to maintain
    healthy bacterial colonies and prevent cannibalistic behavior.
    """
    
    def __init__(self, 
                 petri_dish_area: float = 78.5,  # cm² (standard 10cm dish)
                 optimization_interval: float = 0.5,  # hours
                 enable_logging: bool = True):
        """
        Initialize colony optimizer.
        
        Args:
            petri_dish_area: Area of petri dish in cm²
            optimization_interval: How often to optimize (hours)
            enable_logging: Enable optimization logging
        """
        self.petri_dish_area = petri_dish_area
        self.optimization_interval = optimization_interval
        self.last_optimization = 0.0
        
        self.target = OptimizationTarget()
        self.optimization_history = []
        
        # Setup logging
        if enable_logging:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None
    
    def assess_colony_health(self, 
                           colonies: List[BacterialColony], 
                           environment: Environment) -> Dict[str, ColonyHealth]:
        """
        Assess the health status of all colonies.
        
        Args:
            colonies: List of bacterial colonies
            environment: Current environment
            
        Returns:
            Dictionary mapping colony IDs to health status
        """
        colony_health = {}
        total_population = sum(c.population for c in colonies)
        population_density = total_population / self.petri_dish_area
        
        for colony in colonies:
            if colony.population == 0:
                colony_health[colony.id] = ColonyHealth.CRITICAL
                continue
                
            # Check for cannibalism threshold
            if colony.population > self.target.cannibalism_threshold:
                colony_health[colony.id] = ColonyHealth.CANNIBALISTIC
                continue
            
            # Calculate health metrics
            stress_level = environment.get_stress_level()
            growth_rate = self._calculate_current_growth_rate(colony, environment)
            nutrient_adequacy = environment.conditions.nutrients / self.target.nutrient_buffer
            
            # Determine health status
            if (stress_level < 0.1 and 
                growth_rate > self.target.target_growth_rate * 0.8 and
                nutrient_adequacy > 1.5 and
                population_density < self.target.max_population_density * 0.6):
                colony_health[colony.id] = ColonyHealth.THRIVING
                
            elif (stress_level < self.target.stress_threshold and
                  growth_rate > self.target.target_growth_rate * 0.5 and
                  nutrient_adequacy > 1.0):
                colony_health[colony.id] = ColonyHealth.HEALTHY
                
            elif (stress_level < 0.6 and
                  growth_rate > 0 and
                  nutrient_adequacy > 0.5):
                colony_health[colony.id] = ColonyHealth.STRESSED
                
            else:
                colony_health[colony.id] = ColonyHealth.CRITICAL
        
        return colony_health
    
    def optimize_environment(self, 
                           colonies: List[BacterialColony],
                           environment: Environment,
                           current_time: float) -> Dict[str, Any]:
        """
        Optimize environmental conditions based on colony health.
        
        Args:
            colonies: List of bacterial colonies
            environment: Current environment to optimize
            current_time: Current simulation time
            
        Returns:
            Dictionary of optimization actions taken
        """
        if current_time - self.last_optimization < self.optimization_interval:
            return {"action": "skipped", "reason": "too_soon"}
        
        self.last_optimization = current_time
        
        # Assess current situation
        colony_health = self.assess_colony_health(colonies, environment)
        total_population = sum(c.population for c in colonies)
        population_density = total_population / self.petri_dish_area
        
        actions_taken = {
            "time": current_time,
            "total_population": total_population,
            "population_density": population_density,
            "colony_health": {cid: health.value for cid, health in colony_health.items()},
            "optimizations": []
        }
        
        # Critical intervention for cannibalistic colonies
        cannibalistic_colonies = [cid for cid, health in colony_health.items() 
                                if health == ColonyHealth.CANNIBALISTIC]
        
        if cannibalistic_colonies:
            actions_taken["optimizations"].extend(
                self._handle_cannibalistic_behavior(colonies, environment, cannibalistic_colonies)
            )
        
        # Optimize temperature
        temp_optimization = self._optimize_temperature(colonies, environment, colony_health)
        if temp_optimization:
            actions_taken["optimizations"].append(temp_optimization)
        
        # Optimize pH
        ph_optimization = self._optimize_ph(colonies, environment, colony_health)
        if ph_optimization:
            actions_taken["optimizations"].append(ph_optimization)
        
        # Optimize nutrients
        nutrient_optimization = self._optimize_nutrients(colonies, environment, colony_health)
        if nutrient_optimization:
            actions_taken["optimizations"].append(nutrient_optimization)
        
        # Log optimization actions
        if self.logger and actions_taken["optimizations"]:
            self.logger.info(f"t={current_time:.1f}h: Optimization applied - "
                           f"{len(actions_taken['optimizations'])} actions")
        
        self.optimization_history.append(actions_taken)
        return actions_taken
    
    def _handle_cannibalistic_behavior(self, 
                                     colonies: List[BacterialColony],
                                     environment: Environment,
                                     cannibalistic_colony_ids: List[str]) -> List[Dict[str, Any]]:
        """Handle colonies that have become cannibalistic due to overpopulation."""
        actions = []
        
        # Emergency nutrient boost
        current_nutrients = environment.conditions.nutrients
        emergency_nutrients = max(100.0, current_nutrients * 2.0)
        environment.update_conditions(nutrients=emergency_nutrients)
        
        actions.append({
            "type": "emergency_nutrient_boost",
            "reason": "cannibalistic_behavior_detected",
            "colony_ids": cannibalistic_colony_ids,
            "nutrients_added": emergency_nutrients - current_nutrients
        })
        
        # Reduce temperature to slow growth
        emergency_temp = max(15.0, environment.conditions.temperature - 5.0)
        environment.update_conditions(temperature=emergency_temp)
        
        actions.append({
            "type": "emergency_temperature_reduction", 
            "reason": "population_control",
            "new_temperature": emergency_temp
        })
        
        # Simulate population reduction through cannibalism
        for colony in colonies:
            if colony.id in cannibalistic_colony_ids:
                # Cannibalistic colonies consume each other
                population_loss = int(colony.population * 0.15)  # 15% loss
                colony.population = max(1000, colony.population - population_loss)
                
                actions.append({
                    "type": "cannibalistic_population_loss",
                    "colony_id": colony.id,
                    "population_lost": population_loss,
                    "remaining_population": colony.population
                })
        
        return actions
    
    def _optimize_temperature(self, 
                            colonies: List[BacterialColony],
                            environment: Environment,
                            colony_health: Dict[str, ColonyHealth]) -> Optional[Dict[str, Any]]:
        """Optimize temperature for colony health."""
        if not colonies:
            return None
            
        # Calculate optimal temperature range for all species
        temp_ranges = [colony.species.temperature_range for colony in colonies]
        
        # Find overlapping optimal range
        min_optimal = max(temp_range[0] + 5 for temp_range in temp_ranges)  # +5 for comfort margin
        max_optimal = min(temp_range[1] - 5 for temp_range in temp_ranges)  # -5 for comfort margin
        
        if min_optimal > max_optimal:
            # No overlap, use average
            target_temp = np.mean([np.mean(temp_range) for temp_range in temp_ranges])
        else:
            target_temp = (min_optimal + max_optimal) / 2
        
        current_temp = environment.conditions.temperature
        temp_difference = abs(current_temp - target_temp)
        
        if temp_difference > 2.0:  # Significant temperature adjustment needed
            new_temp = current_temp + np.sign(target_temp - current_temp) * min(temp_difference, 3.0)
            environment.update_conditions(temperature=new_temp)
            
            return {
                "type": "temperature_optimization",
                "old_temperature": current_temp,
                "new_temperature": new_temp,
                "target_temperature": target_temp
            }
        
        return None
    
    def _optimize_ph(self,
                   colonies: List[BacterialColony], 
                   environment: Environment,
                   colony_health: Dict[str, ColonyHealth]) -> Optional[Dict[str, Any]]:
        """Optimize pH for colony health."""
        if not colonies:
            return None
            
        # Calculate optimal pH range
        ph_ranges = [colony.species.ph_range for colony in colonies]
        
        min_optimal = max(ph_range[0] + 0.5 for ph_range in ph_ranges)
        max_optimal = min(ph_range[1] - 0.5 for ph_range in ph_ranges)
        
        if min_optimal > max_optimal:
            target_ph = np.mean([np.mean(ph_range) for ph_range in ph_ranges])
        else:
            target_ph = (min_optimal + max_optimal) / 2
        
        current_ph = environment.conditions.ph
        ph_difference = abs(current_ph - target_ph)
        
        if ph_difference > 0.5:
            new_ph = current_ph + np.sign(target_ph - current_ph) * min(ph_difference, 0.8)
            environment.update_conditions(ph=new_ph)
            
            return {
                "type": "ph_optimization",
                "old_ph": current_ph,
                "new_ph": new_ph,
                "target_ph": target_ph
            }
        
        return None
    
    def _optimize_nutrients(self,
                          colonies: List[BacterialColony],
                          environment: Environment, 
                          colony_health: Dict[str, ColonyHealth]) -> Optional[Dict[str, Any]]:
        """Optimize nutrient levels for colony health."""
        if not colonies:
            return None
            
        total_population = sum(c.population for c in colonies)
        current_nutrients = environment.conditions.nutrients
        
        # Calculate required nutrients based on population
        base_requirement = total_population * 0.001  # Base nutrient requirement
        
        # Adjust based on colony health
        stressed_colonies = sum(1 for health in colony_health.values() 
                              if health in [ColonyHealth.STRESSED, ColonyHealth.CRITICAL])
        
        if stressed_colonies > 0:
            nutrient_multiplier = 1.5 + (stressed_colonies * 0.2)
        else:
            nutrient_multiplier = 1.0
        
        target_nutrients = max(self.target.nutrient_buffer, 
                             base_requirement * nutrient_multiplier)
        
        if current_nutrients < target_nutrients * 0.8:
            nutrient_addition = target_nutrients - current_nutrients
            new_nutrients = current_nutrients + nutrient_addition
            environment.update_conditions(nutrients=new_nutrients)
            
            return {
                "type": "nutrient_optimization",
                "nutrients_added": nutrient_addition,
                "new_nutrient_level": new_nutrients,
                "reason": f"supporting_{total_population}_bacteria"
            }
        
        return None
    
    def _calculate_current_growth_rate(self,
                                     colony: BacterialColony,
                                     environment: Environment) -> float:
        """Calculate current effective growth rate for a colony."""
        if not colony.growth_history or len(colony.growth_history) < 2:
            return 0.0
            
        # Get recent growth data
        recent_data = colony.growth_history[-2:]
        time_delta = recent_data[-1]['time'] - recent_data[-2]['time']
        pop_delta = recent_data[-1]['population'] - recent_data[-2]['population']
        
        if time_delta <= 0 or recent_data[-2]['population'] <= 0:
            return 0.0
            
        # Calculate instantaneous growth rate
        growth_rate = (pop_delta / recent_data[-2]['population']) / time_delta
        return max(0.0, growth_rate)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report."""
        if not self.optimization_history:
            return {"error": "No optimization history available"}
        
        total_optimizations = sum(len(action.get("optimizations", [])) 
                                for action in self.optimization_history)
        
        action_types = {}
        for action_record in self.optimization_history:
            for optimization in action_record.get("optimizations", []):
                action_type = optimization.get("type", "unknown")
                action_types[action_type] = action_types.get(action_type, 0) + 1
        
        return {
            "total_optimization_cycles": len(self.optimization_history),
            "total_optimization_actions": total_optimizations,
            "action_breakdown": action_types,
            "cannibalistic_incidents": action_types.get("cannibalistic_population_loss", 0),
            "emergency_interventions": (action_types.get("emergency_nutrient_boost", 0) + 
                                       action_types.get("emergency_temperature_reduction", 0)),
            "latest_optimization": self.optimization_history[-1] if self.optimization_history else None
        }
    
    def __repr__(self) -> str:
        return f"ColonyOptimizer(dish_area={self.petri_dish_area}cm², optimizations={len(self.optimization_history)})"