import copy
from rigel.exceptions import UndeclaredGlobalVariable
from typing import Any, Dict


class RigelfileDecoder:
    """
    A helper class that decodes Rigelfile using a mechanism based on global variable definitions.
    """

    def __aux_decode(self, data: Any, vars: Dict[str, Any], path: str = '') -> None:
        """
        Auxiliary function that recursively looks for fields to decode inside YAML data.
        Fields to decode have values starting with special char @.

        :type data: Any
        :param data: The YAML data to be decoded.
        :type vars: Dicŧ[str, Any]
        :param vars: The value of global variables.
        """
        if isinstance(data, dict):
            self.__aux_decode_dict(data, vars, path)
        elif isinstance(data, list):
            self.__aux_decode_list(data, vars, path)

    def __aux_decode_dict(self, data: Any, vars: Dict[str, Any], path: str = '') -> None:
        """
        This auxiliary function decodes only list elements inside YAML data.
        Fields to decode have values starting with special char @.
        This auxiliary function decodes only dict elements.
        # NOTE: do not call this function directly. User '__aux_decode' instead.

        :type data: Any
        :param data: The YAML data to be decoded.
        :type vars: Dicŧ[str, Any]
        :param vars: The value of global variables.
        """

        for k, v in data.items():
            if isinstance(v, str):  # in order to contain '$' field must be a string.
                if v[0] == '$':
                    var = v[1:]
                    try:
                        data[k] = vars[var]
                    except KeyError:
                        raise UndeclaredGlobalVariable(field=path, var=var)
            else:
                self.__aux_decode(v, vars, f'{path}.{k}' if path else k)

    def __aux_decode_list(self, data: Any, vars: Dict[str, Any], path: str = '') -> None:
        """
        This auxiliary function decodes only list elements inside YAML data.
        Fields to decode have values starting with special char @.
        # NOTE: do not call this function directly. User '__aux_decode' instead.

        :type data: Any
        :param data: The YAML data to be decoded.
        :type vars: Dicŧ[str, Any]
        :param vars: The value of global variables.
        """

        for idx, elem in enumerate(data):
            if isinstance(elem, str):  # in order to contain '$' field must be a string.
                if elem[0] == '$':
                    var = elem[1:]
                    try:
                        data[idx] = vars[var]
                    except KeyError:
                        raise UndeclaredGlobalVariable(field=path, var=var)
            else:
                self.__aux_decode(elem, vars, f'{path}[{idx}]')

    def decode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decode YAML data.

        :type data: Dict[str, Any]
        :param data: The YAML data to be decoded.

        :rtype: Dict[str, Any]
        :return: The decoded YAML data.
        """

        # Function entry point.
        undecoded_data = copy.deepcopy(data)
        variables = undecoded_data.pop('vars') if undecoded_data.get('vars') else []
        self.__aux_decode(undecoded_data, variables)
        return undecoded_data
