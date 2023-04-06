from pydantic import BaseModel
from typing import List, Tuple


class PluginModel(BaseModel):

    # Required fields.
    hostname: str
    requirements: List[str]

    # Optional fields
    publish: Tuple[int, int] = (9090, 9090)
    timeout: float = 600.0  # seconds
