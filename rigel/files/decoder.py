from rigelcore.exceptions import UndeclaredGlobalVariableError
from typing import Any, Dict


class YAMLDataDecoder:
    """
    A class to decode YAML data.

    Decoding is done by iterating through the entire YAML data and
    replacing all marked variables with the correspondent values based on a
    mapping of user-defined global variables. Variables can be mark with the
    special character $.
    """

    def __aux_decode(self, data: Any, vars: Any, path: str = '') -> None:
        """
        Auxiliary function that recursively looks for fields to decode inside YAML data.

        :type data: Any
        :param data: The YAML data to be decoded.
        :type vars: Dicŧ[str, Any]
        :param vars: The value of global variables.
        """
        if isinstance(data, dict):
            self.__aux_decode_dict(data, vars, path)
        elif isinstance(data, list):
            self.__aux_decode_list(data, vars, path)

    def __aux_decode_dict(self, data: Any, vars: Any, path: str = '') -> None:
        """
        This auxiliary function decodes only list elements inside YAML data.
        Fields to decode have values starting with special char $.
        This auxiliary function decodes only dict elements.
        # NOTE: do not call this function directly. User '__aux_decode' instead.

        :type data: Any
        :param data: The YAML data to be decoded.
        :type vars: Dicŧ[str, Any]
        :param vars: The value of global variables.
        """
        for k, v in data.items():

            new_path = f'{path}.{k}' if path else k

            if isinstance(v, str):  # in order to contain '$' field must be a string.
                if v[0] == '$':
                    var = v[1:]
                    try:
                        data[k] = vars[var]
                    except (KeyError, TypeError):
                        raise UndeclaredGlobalVariableError(field=new_path, var=var)
            else:
                self.__aux_decode(v, vars, new_path)

    def __aux_decode_list(self, data: Any, vars: Dict[str, Any], path: str = '') -> None:
        """
        This auxiliary function decodes only list elements inside YAML data.
        Fields to decode have values starting with special char $.
        # NOTE: do not call this function directly. User '__aux_decode' instead.

        :type data: Any
        :param data: The YAML data to be decoded.
        :type vars: Dicŧ[str, Any]
        :param vars: The value of global variables.
        """

        for idx, elem in enumerate(data):

            new_path = f'{path}[{idx}]'

            if isinstance(elem, str):  # in order to contain '$' field must be a string.
                if elem[0] == '$':
                    var = elem[1:]
                    try:
                        data[idx] = vars[var]
                    except KeyError:
                        raise UndeclaredGlobalVariableError(field=new_path, var=var)
            else:
                self.__aux_decode(elem, vars, new_path)

    def decode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decode YAML data.

        :type data: Dict[str, Any]
        :param data: The YAML data to be decoded.

        :rtype: Dict[str, Any]
        :return: The decoded YAML data.
        """

        # Function entry point.
        variables = data.get('vars') or []
        self.__aux_decode(data, variables)
        return data
