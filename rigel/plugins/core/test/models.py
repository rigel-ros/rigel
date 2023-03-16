from pydantic import BaseModel, Extra, PrivateAttr
from typing import Any, Dict, List, Optional, Tuple


class Introspection(BaseModel, extra=Extra.forbid):

    # Required fields
    requirements: List[str]

    # Optional fields
    publish: Tuple[int, int] = (9090, 9090)
    hostname: Optional[str] = None


class TestComponent(BaseModel):
    """
    A placeholder for information regarding a containerized ROS package to include in the testing.

    :type image: string
    :param image: The Docker image.
    :type name: string
    :param name: The Docker container name.
    :type artifacts: List[string].
    :param artifacts: Files to copy from the container to the host machine.
    :type instrospection: Instrospection.
    :param instrospection: Information regarding test conditions.
    :type _kwargs: Dict[str, Any]
    :param _kwargs: Keyword arguments. Consult the documentation for more information
    (https://gabrieldemarmiesse.github.io/python-on-whales/sub-commands/container/ - run function)
    """
    # Required fields
    name: str
    image: str

    # Optional fields
    introspection: Optional[Introspection] = None
    artifacts: List[str] = []

    # Private fields.
    _kwargs: Dict[str, Any] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**{
            'name': data.pop('name', None),
            'image': data.pop('image', None),
            'artifacts': data.pop('artifacts', []),
            'introspection': data.pop('introspection', None)
        })
        self._kwargs = data


class PluginModel(BaseModel):

    # Required fields.
    components: List[TestComponent]

    # Optional fields.
    timeout: float = 600.0  # seconds
