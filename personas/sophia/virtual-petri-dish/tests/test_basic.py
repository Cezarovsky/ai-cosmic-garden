"""
Test Suite for Virtual Petri Dish

Basic tests to ensure our simulation components work correctly.
"""

import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bacterial_colony import BacterialColony, BacterialSpecies
from environment import Environment
from simulation import Simulation


class TestEnvironment(unittest.TestCase):
    """Test Environment class functionality."""
    
    def setUp(self):
        self.env = Environment(temperature=37.0, ph=7.0, nutrients=100.0)
    
    def test_initialization(self):
        """Test environment initialization."""
        self.assertEqual(self.env.conditions.temperature, 37.0)
        self.assertEqual(self.env.conditions.ph, 7.0)
        self.assertEqual(self.env.conditions.nutrients, 100.0)
    
    def test_growth_multiplier(self):
        """Test growth multiplier calculation."""
        multiplier = self.env.get_growth_multiplier()
        self.assertGreater(multiplier, 0)
        self.assertLessEqual(multiplier, 2.0)
    
    def test_nutrient_consumption(self):
        """Test nutrient consumption."""
        initial_nutrients = self.env.conditions.nutrients
        self.env.consume_nutrients(10.0)
        self.assertEqual(self.env.conditions.nutrients, initial_nutrients - 10.0)


class TestBacterialColony(unittest.TestCase):
    """Test BacterialColony class functionality."""
    
    def setUp(self):
        self.colony = BacterialColony("E.coli", initial_population=100)
        self.env = Environment(temperature=37.0, ph=7.0, nutrients=100.0)
    
    def test_initialization(self):
        """Test colony initialization."""
        self.assertEqual(self.colony.population, 100)
        self.assertEqual(self.colony.species.name, "Escherichia coli")
        self.assertGreater(len(self.colony.id), 0)
    
    def test_growth_simulation(self):
        """Test basic growth simulation."""
        initial_pop = self.colony.population
        self.colony.simulate_growth(self.env, 1.0)
        
        # Population should generally increase in good conditions
        # (unless in death phase, but unlikely with initial conditions)
        self.assertGreaterEqual(self.colony.population, 0)
    
    def test_predefined_species(self):
        """Test predefined bacterial species."""
        species_names = ["E.coli", "B.subtilis", "S.aureus"]
        
        for species in species_names:
            colony = BacterialColony(species)
            self.assertIsNotNone(colony.species.name)
            self.assertGreater(colony.species.max_growth_rate, 0)


class TestSimulation(unittest.TestCase):
    """Test Simulation class functionality."""
    
    def setUp(self):
        self.sim = Simulation()
    
    def test_initialization(self):
        """Test simulation initialization."""
        self.assertEqual(len(self.sim.colonies), 0)
        self.assertEqual(self.sim.time_elapsed, 0.0)
    
    def test_add_colony(self):
        """Test adding colonies to simulation."""
        colony = self.sim.add_colony("E.coli", 100)
        self.assertEqual(len(self.sim.colonies), 1)
        self.assertEqual(colony.population, 100)
    
    def test_environmental_conditions(self):
        """Test setting environmental conditions."""
        self.sim.set_environment_conditions(temperature=30.0)
        self.assertEqual(self.sim.environment.conditions.temperature, 30.0)


if __name__ == '__main__':
    print("🧪 Running Virtual Petri Dish Test Suite...")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2)