from pydantic import BaseModel, Extra, Field
from typing import Any, Dict, Union

SimpleDataModel = Union[bool, float, int, str]


class ComplexDataModel(BaseModel, extra=Extra.forbid):

    type: str
    with_: Dict[str, Any] = Field(..., alias='with')
