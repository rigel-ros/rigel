import unittest
from pydantic import BaseModel
from rigel.exceptions import (
    InvalidValueError,
    MissingRequiredFieldError,
    UndeclaredValueError
)
from rigel.models import ModelBuilder
from unittest.mock import Mock, patch


class TestModel(BaseModel):
    test_field: int


class ModelBuildingTesting(unittest.TestCase):
    """
    Test suite for rigel.models.ModelBuilding class.
    """

    def test_missing_required_field_error(self) -> None:
        """
        Test if MissingRequiredFieldError is thrown if a required model field is not provided.
        """
        with self.assertRaises(MissingRequiredFieldError) as context:
            builder = ModelBuilder(TestModel)
            builder.build([], {})
        self.assertEqual(context.exception.kwargs['field'], 'test_field')

    def test_undeclared_value_error(self) -> None:
        """
        Test if UndeclaredValueError is thrown if a model field is set to None.
        """
        with self.assertRaises(UndeclaredValueError) as context:
            builder = ModelBuilder(TestModel)
            builder.build([], {'test_field': None})
        self.assertEqual(context.exception.kwargs['field'], 'test_field')

    def test_invalid_value_error(self) -> None:
        """
        Test if InvalidValueError is thrown if a model field is set to an invalid value.
        """
        with self.assertRaises(InvalidValueError) as context:
            builder = ModelBuilder(TestModel)
            builder.build([], {'test_field': 'invalid_int_value'})
        self.assertEqual(context.exception.kwargs['instance_type'], TestModel)
        self.assertEqual(context.exception.kwargs['field'], 'test_field')

    @patch.object(TestModel, '__init__')
    def test_injected_data(self, mock_model: Mock) -> None:
        """
        Test if the provided data is properly forwarded to the model constructor.
        """
        mock_model.return_value = None
        kwargs = {'test_field': 42}
        builder = ModelBuilder(TestModel)
        builder.build([], kwargs)
        mock_model.assert_called_once_with(**kwargs)


if __name__ == '__main__':
    unittest.main()
