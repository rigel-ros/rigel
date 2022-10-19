import os
import re
from rigel.exceptions import UndeclaredGlobalVariableError
from typing import Any, Dict


class YAMLDataDecoder:
    """A class to decode YAML data.

    Decoding is done by iterating through the entire YAML data and
    replacing all marked variables with the correspondent values. Variables are
    marked by delimiters {{ and }}. Values can be stored either inside a mapping of
    user-defined variables on the Rigelfile and on environment variables. Values
    declares inside the mapping of user-defined variables has precedence over values
    stored as environment variables.
    """

    def __extract_variable_name(self, match: str) -> str:
        """Auxiliary function that extracts template variables from pattern matches.

        Names of template variables are enclosed between delimiters '{{' and '}}'.

        :type match: string
        :param match: The pattern match.

        :rtype: string
        :return: The name of the variable referred by the pattern match.
        """
        chars_to_remove = ['{', '}', ' ']
        variable_name = match
        for c in chars_to_remove:
            variable_name = variable_name.replace(c, '')
        return variable_name

    def __aux_decode(self, data: Any, vars: Dict[str, Any], path: str = '') -> None:
        """Auxiliary function that recursively looks for fields to decode inside YAML data.

        :param data: Any
        :type data: The YAML data to be encoded.
        :param vars: Dict[str, Any]
        :type vars: Declared global variables.
        :param path: The path for the YAML element being parsed.
        :type path: str
        """
        if isinstance(data, dict):
            self.__aux_decode_dict(data, vars, path)
        elif isinstance(data, list):
            self.__aux_decode_list(data, vars, path)

    def __aux_decode_dict(self, data: Any, vars: Dict[str, Any], path: str = '') -> None:
        """This auxiliary function decodes only dict elements inside YAML data.

        Fields to decode have values delimited by {{ and }}.
        This auxiliary function decodes only dict elements.
        # NOTE: do not call this function directly. User '__aux_decode' instead.

        :param data: Any
        :type data: The YAML data to be encoded.
        :param vars: Dict[str, Any]
        :type vars: Declared global variables.
        :param path: The path for the YAML element being parsed.
        :type path: str
        """
        self.__aux_decode_dict_values(data, vars, path)
        self.__aux_decode_dict_keys(data, vars, path)

    def __aux_decode_dict_values(self, data: Any, vars: Dict[str, Any], path: str = '') -> None:
        """This auxiliary function decodes only the values of dict elements inside the YAML data.

        Fields to decode have values delimited by {{ and }}.
        # NOTE: do not call this function directly. Use '__aux_decode' instead.

        :param data: Any
        :type data: The YAML data to be encoded.
        :param vars: Dict[str, Any]
        :type vars: Declared global variables.
        :param path: The path for the YAML element being parsed.
        :type path: str
        """
        for k, v in data.items():

            new_path = f'{path}.{k}' if path else k

            if isinstance(v, str):  # in order to contain delimiters the field must be of type str
                matches = re.findall(r'{{[a-zA-Z0-9_\s\-\!\?]+}}', v)
                for match in matches:
                    variable_name = self.__extract_variable_name(match)
                    if variable_name in vars:
                        data[k] = data[k].replace(match, vars[variable_name])
                    elif variable_name in os.environ:
                        data[k] = data[k].replace(match, os.environ[variable_name])
                    else:
                        print(f'>>>>>>>>>>>>>>>>>>>>>>>>>>>> {new_path} <<<>>>> {variable_name} <>>>>>>>>>>>>>>>>><')
                        raise UndeclaredGlobalVariableError(field=new_path, var=variable_name)
            else:
                self.__aux_decode(v, vars, new_path)

    def __aux_decode_dict_keys(self, data: Any, vars: Dict[str, Any], path: str = '') -> None:
        """This auxiliary function decodes only the keys of dict elements inside the YAML data.

        Fields to decode have values delimited by {{ and }}.
        # NOTE: do not call this function directly. Use '__aux_decode' instead.

        :param data: Any
        :type data: The YAML data to be encoded.
        :param vars: Dict[str, Any]
        :type vars: Declared global variables.
        :param path: The path for the YAML element being parsed.
        :type path: str
        """
        keys = list(data.keys())
        for k in keys:

            new_path = f'{path}.{k}' if path else k

            if isinstance(k, str):  # in order to contain delimiters the field must be of type str
                matches = re.findall(r'{{[a-zA-Z0-9_\s\-\!\?]+}}', k)
                for match in matches:
                    variable_name = self.__extract_variable_name(match)
                    if variable_name in vars:
                        data[vars[variable_name]] = data.pop(k)
                    elif variable_name in os.environ:
                        data[os.environ[variable_name]] = data.pop(k)
                    else:
                        raise UndeclaredGlobalVariableError(field=new_path, var=variable_name)

    def __aux_decode_list(self, data: Any, vars: Dict[str, Any], path: str = '') -> None:
        """This auxiliary function decodes only list elements inside YAML data.

        Fields to decode have values dlimited by {{ and }}.
        # NOTE: do not call this function directly. User '__aux_decode' instead.

        :param data: Any
        :type data: The YAML data to be encoded.
        :param vars: Dict[str, Any]
        :type vars: Declared global variables.
        :param path: The path for the YAML element being parsed.
        :type path: str
        """
        for idx, elem in enumerate(data):

            new_path = f'{path}[{idx}]'

            if isinstance(elem, str):  # in order to contain delimiters the field must be of type str
                matches = re.findall(r'{{[a-zA-Z0-9_\s\-\!\?]+}}', elem)
                for match in matches:
                    variable_name = self.__extract_variable_name(match)
                    if variable_name in vars:
                        data[idx] = data[idx].replace(match, vars[variable_name])
                    elif variable_name in os.environ:
                        data[idx] = data[idx].replace(match, os.environ[variable_name])
                    else:
                        raise UndeclaredGlobalVariableError(field=new_path, var=variable_name)
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
