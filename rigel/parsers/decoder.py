import copy
from rigel.exceptions import UndeclaredGlobalVariable
from typing import Any, Dict


class RigelfileDecoder:
    """
    A helper class that decodes Rigelfile using a mechanism based on global variable definitions.
    """

    @staticmethod
    def decode(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decode YAML data.

        :type data: Dict[str, Any]
        :param data: The YAML data to be decoded.

        :rtype: Dict[str, Any]
        :return: The decoded YAML data.
        """

        def __aux_decode(data: Any, vars: Dict[str, Any], path='',) -> None:
            """
            Auxiliary function that recursively looks for fields to decode inside YAML data.
            Fields to decode have values starting with special char @.

            :type data: Any
            :param data: The YAML data to be decoded.
            :type vars: Dicŧ[str, Any]
            :param vars: The value of global variables.
            """

            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, str):  # in order to contain '$' field must be a string.
                        if v[0] == '$':
                            var = v[1:]
                            try:
                                data[k] = vars[var]
                            except KeyError:
                                raise UndeclaredGlobalVariable(field=path, var=var)
                    else:
                        __aux_decode(v, vars, f'{path}.{k}' if path else k)

            elif isinstance(data, list):
                for idx, elem in enumerate(data):
                    if isinstance(elem, str):  # in order to contain '$' field must be a string.
                        if elem[0] == '$':
                            var = elem[1:]
                            try:
                                data[idx] = vars[var]
                            except KeyError:
                                raise UndeclaredGlobalVariable(field=path, var=var)
                    else:
                        __aux_decode(elem, vars, f'{path}[{idx}]')

        # Function entry point.
        undecoded_data = copy.deepcopy(data)
        variables = undecoded_data.pop('vars') if undecoded_data.get('vars') else []
        __aux_decode(undecoded_data, variables)
        return undecoded_data
