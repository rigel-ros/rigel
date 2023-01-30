from pydantic import BaseModel, Extra, Field
from typing import Any, Dict

PluginRawData = Dict[str, Any]


class PluginDataModel(BaseModel, extra=Extra.forbid):

    plugin: str
    with_: PluginRawData = Field(..., alias='with')
