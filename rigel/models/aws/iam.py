from pydantic import Extra
from rigel.models.data import ComplexDataModel


class IAMCredentials(ComplexDataModel, extra=Extra.forbid):

    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str
