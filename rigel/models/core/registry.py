from pydantic import Extra
from rigel.models.data import ComplexDataModel


class ContainerRegistry(ComplexDataModel, extra=Extra.forbid):

    server: str
    password: str
    username: str
