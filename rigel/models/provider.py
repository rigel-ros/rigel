from pydantic import BaseModel, Extra, Field
from typing import Any, Dict

ProviderRawData = Dict[str, Any]


class ProviderDataModel(BaseModel, extra=Extra.forbid):

    provider: str
    with_: ProviderRawData = Field(..., alias='with')
