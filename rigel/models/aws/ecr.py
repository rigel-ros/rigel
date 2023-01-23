from pydantic import Extra
from rigel.models.data import ComplexDataModel


class ECR(ComplexDataModel, extra=Extra.forbid):

    server: str
    credentials: str
