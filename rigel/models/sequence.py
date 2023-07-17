from pydantic import BaseModel, Extra, Field
from typing import Any, Dict, List, Union


class SequenceJobEntry(BaseModel, extra=Extra.forbid):

    # Required fields.
    name: str
    with_: Dict[str, Any] = Field(..., alias='with')


class StageBaseModel(BaseModel, extra=Extra.forbid):

    # Optional fields.
    description: str = ''


class SequentialStage(StageBaseModel, extra=Extra.forbid):

    # Required fields.
    jobs: List[Union[str, SequenceJobEntry]]


class ConcurrentStage(StageBaseModel, extra=Extra.forbid):

    # Required fields.
    jobs: List[Union[str, SequenceJobEntry]]
    dependencies: List[Union[str, SequenceJobEntry]]


class ParallelStage(StageBaseModel, extra=Extra.forbid):

    # Required fields.
    parallel: List[Union[SequentialStage, ConcurrentStage]]

    # Optional fields.
    matrix: Dict[str, Union[str, List[Any]]] = {}


SequenceStage = Union[SequentialStage, ParallelStage, ConcurrentStage]


class Sequence(BaseModel, extra=Extra.forbid):

    # Required fields.
    stages: List[SequenceStage]

    # Optional fields.
    matrix: Dict[str, Any] = {}
