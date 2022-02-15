from pydantic.errors import (
    MissingError,
    NoneIsNotAllowedError
)
from pydantic.error_wrappers import (
    ValidationError
)
from rigel.exceptions import (
    MissingRequiredFieldError,
    UndeclaredValueError
)
from typing import Any, Dict, Type


class YAMLInjector:
    """
    A helper class to instantiate dataclasses in a safe way.
    """

    def __init__(self, instance_type: Type) -> None:
        """
        Set the type of instances this class will produce.
        """
        self.instance_type = instance_type

    def inject(self, yaml_data: Dict[str, Any]) -> Any:
        """
        Inject YAML data and instantiate a dataclass.

        :type cls: Any
        :param cls: The class to be instantiated.
        :type yaml_data: Dict[str, Any]
        :param yaml_data: The data to be passed to the dataclass constructor.
        """
        try:
            return self.instance_type(**yaml_data)

        except ValidationError as err:
            print(err)

            for wrapper in err.args[0]:
                field = wrapper.loc_tuple()[0]

                if isinstance(wrapper.exc, MissingError):
                    raise MissingRequiredFieldError(field=field)

                elif isinstance(wrapper.exc, NoneIsNotAllowedError):
                    raise UndeclaredValueError(path=field)
