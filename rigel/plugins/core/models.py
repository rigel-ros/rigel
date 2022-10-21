from pydantic import BaseModel
from typing import Optional


class Registry(BaseModel):
    """Information placeholder about an image registry.

    :type password: string
    :cvar password: The password for authentication.
    :type server: string
    :cvar server: The image registry to authenticate with.
    :type username: string
    :cvar username: The username to authenticate.
    """
    # Required fields.
    server: str

    # Optional fields.
    password: Optional[str] = None
    username: Optional[str] = None
