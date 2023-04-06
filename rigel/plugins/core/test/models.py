from pydantic import BaseModel
from typing import List, Optional


class PluginModel(BaseModel):

    # Required fields.
    requirements: List[str]

    # Optional fields
    hostname: Optional[str] = None
    port: int = 9090
    timeout: float = 600.0  # seconds
