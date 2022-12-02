from pydantic import BaseModel, PrivateAttr
from typing import Any, Dict, List, Optional, Tuple


class Introspection(BaseModel):

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

    # Private fields.
    _kwargs: Dict[str, Any] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**{
            'name': data.pop('name', None),
            'image': data.pop('image', None),
            'introspection': data.pop('introspection', None)
        })
        self._kwargs = data


class PluginModel(BaseModel):
    components: List[TestComponent]
