from pydantic import BaseModel, PrivateAttr
from typing import Any, Dict, List


class ApplicationComponent(BaseModel):
    """
    A placeholder for information regarding a containerized ROS package to include in the testing.

    :type image: string
    :param image: The Docker image.
    :type name: string
    :param name: The Docker container name.
    :type artifacts: List[string].
    :param artifacts: Files to copy from the container to the host machine.
    :type _kwargs: Dict[str, Any]
    :param _kwargs: Keyword arguments. Consult the documentation for more information
    (https://gabrieldemarmiesse.github.io/python-on-whales/sub-commands/container/ - run function)
    """
    # Required fields
    name: str
    image: str

    # Optional fields
    artifacts: List[str] = []
    introspection: bool = False

    # Private fields.
    _kwargs: Dict[str, Any] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**{
            'name': data.pop('name', None),
            'image': data.pop('image', None),
            'artifacts': data.pop('artifacts', []),
            'introspection': data.pop('introspection', False)
        })
        self._kwargs = data


class PluginModel(BaseModel):

    # Required fields.
    components: List[ApplicationComponent]

    # Optional fields.
    timeout: float = 0.0
