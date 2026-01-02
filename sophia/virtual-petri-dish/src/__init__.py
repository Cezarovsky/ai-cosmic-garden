"""
Virtual Petri Dish Package

A biotech AI simulation platform for bacterial growth modeling.
"""

__version__ = "0.1.0"
__author__ = "Gardinar & Sophia - Cosmic Tribe"
__email__ = "cosmic.tribe.biotech@example.com"

from .bacterial_colony import BacterialColony
from .environment import Environment
from .simulation import Simulation

__all__ = ["BacterialColony", "Environment", "Simulation"]