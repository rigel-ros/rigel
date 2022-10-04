from hpl.ast import HplBinaryOperator, HplFieldAccess, HplLiteral, HplThisMessage
from typing import Any, Dict, Callable, List, Union

ROSMessageValue = Any
ROSMessageType = Dict[str, Any]
ROSCallbackType = Callable[[ROSMessageType], bool]


class CallbackGenerator:

    def __field_path(self, content: Dict[str, Any], path: List[str]) -> Any:
        """
        Extract the value of a field from within a collection of data.

        :param content: The collection of all data to analyze.
        :type content: Dict[str, Any]
        :param path: The path for the value.
        :type path: List[str]
        :return: The field value.
        :rtype: Any
        """
        next = path[0]
        try:
            if len(path) == 1:
                return content[next]
            return self.__field_path(content[next], path[1:])
        except KeyError as err:
            raise err

    def generate_callback_equal(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a ROS message field equals a certain reference value.

        :param field: The ROS message field.
        :type field: List[str]
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field and the reference value are equal.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) == value)
        return callback

    def generate_callback_different(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a given ROS message field is different from a certain reference value.

        :param field: The ROS message field.
        :type field: List[str]
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field is different from the reference value.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) != value)
        return callback

    def generate_callback_lesser(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a given ROS message field is lesser than a certain reference value.

        :param field: The ROS message field.
        :type field: List[str]
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field is lesser than the reference value.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) < value)
        return callback

    def generate_callback_lesser_than(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a given ROS message field is lesser than or equal to a certain reference value.

        :param field: The ROS message field.
        :type field: List[str]
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field is lesser than or equal to the reference value.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) <= value)
        return callback

    def generate_callback_greater(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a given ROS message field is greater than a certain reference value.

        :param field: The ROS message field.
        :type field: List[str]
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field is greater than the reference value.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) > value)
        return callback

    def generate_callback_greater_than(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a given ROS message field is greater than or equal to a certain reference value.

        :param field: The ROS message field.
        :type field: List[str]
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field is greater than or equal to the reference value.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) >= value)
        return callback

    def generate_callback_iff(self, anterior: ROSCallbackType, posterior: ROSCallbackType) -> ROSCallbackType:
        """
        Generate a base callback function that
        retrives the value of a posterior function in case an anterior function returns True.

        :param anterior: The anterior function.
        :type anterior: Callable[[Dict[str, Any]], bool]
        :param posterior: The posterior function.
        :type posterior: Callable[[Dict[str, Any]], bool]
        :rtype: ROSCallbackType
        :return: A function that retrives the value of a posterior function in case an anterior function returns True.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            if anterior(msg):
                return posterior(msg)
            return False
        return callback

    def generate_callback_and(self, anterior: ROSCallbackType, posterior: ROSCallbackType) -> ROSCallbackType:
        """
        Generate a base callback that
        verifies if both an anterior condition and a posterior condition return True.

        :param anterior: The anterior function.
        :type anterior: Callable[[Dict[str, Any]], bool]
        :param posterior: The posterior function.
        :type posterior: Callable[[Dict[str, Any]], bool]
        :rtype: ROSCallbackType
        :return: A function that returns True if both anterior and posterior functions also return True.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            anterior_value = anterior(msg)
            posterior_value = posterior(msg)
            return anterior_value and posterior_value

        return callback

    def generate_callback_vacuous(self) -> ROSCallbackType:
        """
        Generates a dummy callback function that simply returns True.
        This is useful to check if a message was received on a given topic despite its contents.

        :rtype: ROSCallbackType
        :return: A function that returns True for each return message.
        """
        def callback(msg: ROSMessageType) -> bool:
            return True
        return callback

    def process_vacuous_truth(self) -> ROSCallbackType:
        """
        Retrieve a dummy callback function to be associated with HplVacuousTruth.
        HplVacuousTruth callbacks simply return True

        :return: A ROS message handler callback function.
        :rtype: ROSCallbackType
        """
        return self.generate_callback_vacuous()

    def process_binary_operator(self, operator: HplBinaryOperator) -> ROSCallbackType:
        """
        Retrieve a callback function that verifies the same condition as a HplBinaryOperator.

        :param operator: The HplBinaryOperator holding information regarding the callback logic.
        :type operator: HplBinaryOperator
        :return: A ROS message handler callback function.
        :rtype: ROSCallbackType
        """
        arg1 = self.__extract_argument(operator.operand1)
        arg2 = self.__extract_argument(operator.operand2)

        if operator.op == '=':
            return self.generate_callback_equal(arg1, arg2)
        elif operator.op == '!=':
            return self.generate_callback_different(arg1, arg2)
        elif operator.op == '<':
            return self.generate_callback_lesser(arg1, arg2)
        elif operator.op == '<=':
            return self.generate_callback_lesser_than(arg1, arg2)
        elif operator.op == '>':
            return self.generate_callback_greater(arg1, arg2)
        elif operator.op == '>=':
            return self.generate_callback_greater_than(arg1, arg2)
        elif operator.op in ['iff', 'implies']:
            return self.generate_callback_iff(arg2, arg1)
        elif operator.op == 'and':
            return self.generate_callback_and(arg1, arg2)
        else:
            # TODO: create proper exception.
            raise Exception(f'Unsupported operator "{operator}".')

    def __extract_argument(
            self,
            operand: Union[HplBinaryOperator, HplFieldAccess, HplLiteral]
            ) -> Any:
        """
        :param operand: _description_
        :type operand: Union[HplBinaryOperator, HplFieldAccess, HplLiteral]
        :return: _description_
        :rtype: Union[float, int, List[str], str, ROSCallbackType]
        """
        if isinstance(operand, HplFieldAccess):
            return self.__extract_field_path(operand)
        else:
            return self.__extract_value(operand)

    def __extract_field_path(self, operand: HplFieldAccess) -> List[str]:
        """
        Extract the path for a ROS message field.

        :param operand: The operator to extract the field path.
        :type operand: HplFieldAccess
        :return: The ROS message field path.
        :rtype: List[str]
        """
        path = []
        if operand.message and not isinstance(operand.message, HplThisMessage):
            path += operand.message.field.split('.')
        path += operand.field.split('.')
        return path

    def __extract_value(
            self,
            operand: Union[HplBinaryOperator, HplLiteral]
            ) -> Any:
        """
        Extract arguments from operators.

        :param operand: The operator to extract arguments from.
        :type operand: Union[HplBinaryOperator, HplLiteral]
        :return: The argument value.
        :rtype: Any
        """
        if isinstance(operand, HplLiteral):
            # NOTE: numerical primitive data values and 'bool'
            # have a different access mechanism than 'str'
            for t in [int, float, bool]:
                if isinstance(operand.value, t):
                    return operand.value
            return operand.value.value[1:-1]  # for 'str' typed values - remove quotation marks

        elif isinstance(operand, HplBinaryOperator):
            return self.process_binary_operator(operand)
