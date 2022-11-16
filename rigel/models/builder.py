from pydantic.error_wrappers import ValidationError
from rigel.exceptions import PydanticValidationError
from typing import Any, Dict, List, Type


class ModelBuilder:
    """
    A class to help instantiate subclasses of pydantic.BaseModel.
    This class handles all the exceptions that may occur
    while creating instances of a given class.
    """

    def __init__(self, instance_type: Type) -> None:
        """
        Set the class to instantiate.

        :type instance_type: Type
        :param instance_type: The class to instantiate.
        """
        self.instance_type = instance_type

    # TODO: change return type from Any to BaseModel.
    def build(self, args: List[Any], kwargs: Dict[str, Any]) -> Any:
        """
        Create an instance of the specified class.

        :type args: List[Any]
        :param args: List of required class arguments.
        :type kwargs: Dict[str, Any]
        :param kwargs: Positional class arguments.

        :rtype: Type
        :return: An instance of the specified class.
        """
        try:
            return self.instance_type(*args, **kwargs)

        except ValidationError as exception:
            raise PydanticValidationError(exception=exception)
