from pydantic import BaseModel
from typing import List
from .plugin import PluginSection


class SimulationSection(BaseModel):
    """
    A placeholder for information regarding simulations using containerized ROS nodes.

    It holds information about required section containing information about the plugin to be
    used during simulation.
    It also holds information about simulation requirements to be considered during
    simulation assessment.
    """
    # Required fields.
    plugins: List[PluginSection]

    # Optional fields
    introspection: List[str] = []
    timeout: int = 60  # seconds
