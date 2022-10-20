import os
from pydantic import BaseModel, validator
from rigel.exceptions import UndeclaredEnvironmentVariableError
from typing import Any, Dict

class Registry(BaseModel):
    """Information placeholder about an image registry.

    :type password: string
    :cvar password: The password for authentication.
    :type server: string
    :cvar server: The image registry to authenticate with.
    :type username: string
    :cvar username: The username to authenticate.
    """
    password: str
    server: str
    username: str
