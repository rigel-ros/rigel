import unittest
from rigel.exceptions import UndeclaredGlobalVariableError
from rigel.files import YAMLDataDecoder


class YAMLDataDecoderTesting(unittest.TestCase):
    """
    Test suite for rigel.fields.YAMLDataDecoder class.
    """

    def test_undeclared_variable_error_dict_rigelfile(self) -> None:
        """
        Test if UndeclaredGlobalVariableError is thrown if references
        to unknown Rigelfile variables are made inside an element of type dict.
        """
        test_data = {'test_key': '{{ unknown }}', 'vars': {'template_var': 'test_value'}}
        with self.assertRaises(UndeclaredGlobalVariableError) as context:
            decoder = YAMLDataDecoder()
            decoder.decode(test_data)
        self.assertEqual(context.exception.kwargs['field'], 'test_key')
        self.assertEqual(context.exception.kwargs['var'], 'unknown')

    def test_undeclared_variable_error_list(self) -> None:
        """
        Test if UndeclaredGlobalVariable is thrown if references
        to unknown global variables are made inside an element of type list.
        """
        test_data = {'test_key': ['{{ unknown }}'], 'vars': {'template_var': 'test_value'}}
        with self.assertRaises(UndeclaredGlobalVariableError) as context:
            decoder = YAMLDataDecoder()
            decoder.decode(test_data)
        self.assertEqual(context.exception.kwargs['field'], 'test_key[0]')
        self.assertEqual(context.exception.kwargs['var'], 'unknown')

    def test_decoding_mechanism_dict(self) -> None:
        """
        Test if decoding mechanism works as expected whenever references
        to unknown global variables are made inside a dict.
        """
        template_value = 'test_value'
        unchanged_value = 'unchanged_value'
        test_data = {
            'vars': {'template_var': template_value},
            'test_key': '{{ template_var }}',
            'unchanged_key': unchanged_value
        }
        decoder = YAMLDataDecoder()
        decoded_test_data = decoder.decode(test_data)
        self.assertEqual(decoded_test_data['test_key'], template_value)
        self.assertEqual(decoded_test_data['unchanged_key'], unchanged_value)  # control value

    def test_decoding_mechanism_list(self) -> None:
        """
        Test if decoding mechanism works as expected whenever references
        to unknown global variables are made inside a list.
        """
        template_value = 'test_value'
        unchanged_value = 'unchanged_value'
        test_data = {
            'vars': {'template_var': template_value},
            'test_key': ['{{ template_var }}', unchanged_value]
        }
        decoder = YAMLDataDecoder()
        decoded_test_data = decoder.decode(test_data)
        self.assertEqual(decoded_test_data['test_key'][0], template_value)
        self.assertEqual(decoded_test_data['test_key'][1], unchanged_value)  # control value


if __name__ == '__main__':
    unittest.main()
