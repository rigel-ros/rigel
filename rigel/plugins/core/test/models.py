from pydantic import BaseModel
from typing import List


class PluginModel(BaseModel):

    # Required fields.
    requirements: List[str]
    hostname: str

    # Optional fields
    port: int = 9090
    timeout: float = 300.0  # seconds
    ignore: float = 0.0  # seconds
