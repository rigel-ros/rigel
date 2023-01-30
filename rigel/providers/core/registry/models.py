from pydantic import BaseModel, Extra


class ContainerRegistryProviderModel(BaseModel, extra=Extra.forbid):

    # Required fields
    server: str
    username: str
    password: str
