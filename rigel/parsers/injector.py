from rigel.exceptions import (
    MissingRequiredFieldError,
    UnknownFieldError
)
from typing import Any, Dict


class YAMLInjector:
    """
    A helper class to instantiate dataclasses in a safe way.
    """

    @staticmethod
    def inject(cls: Any, yaml_data: Dict[str, Any]) -> Any:
        """
        Inject YAML data and instantiate a dataclass.

        :type cls: Any
        :param cls: The class to be instantiated.
        :type yaml_data: Dict[str, Any]
        :param yaml_data: The data to be passed to the dataclass constructor.
        """
        try:
            return cls(**yaml_data)

        except TypeError as err:

            message = err.args[0]
            field = message.split()[-1].replace("'", '')

            if 'got an unexpected keyword' in err.args[0]:
                raise UnknownFieldError(field=field)

            elif 'missing' in err.args[0]:
                raise MissingRequiredFieldError(field=field)
