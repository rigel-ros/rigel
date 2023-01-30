from pydantic import BaseModel, Extra, validator
from rigel.exceptions import InvalidValueError
from typing import Any, List, Optional


class AWSProviderModel(BaseModel, extra=Extra.forbid):

    # Required fields
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str
    services: List[str]

    # Optional fields
    ecr_servers: List[str] = []

    @validator('services')
    def validate_services(cls, services: List[str]) -> List[str]:
        """
        Ensure that at least one AWS service was selected.
        """
        if not services:
            raise InvalidValueError(field='services', value=services)
        return services


class AWSProviderOutputModel(BaseModel, extra=Extra.forbid):

    # Optional fields
    robomaker_client: Optional[Any] = None
