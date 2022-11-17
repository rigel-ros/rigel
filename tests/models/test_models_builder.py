import pydantic
import unittest
from rigel.exceptions import PydanticValidationError
from rigel.models.builder import ModelBuilder
from unittest.mock import Mock, patch


class TestModel(pydantic.BaseModel):
    test_field: int


class ModelBuildingTesting(unittest.TestCase):
    """
    Test suite for rigel.models.builder.ModelBuilding class.
    """

    @patch.object(TestModel, '__init__')
    def test_pydantic_validation_error(self, model_mock: Mock) -> None:
        """
        Test if PydanticValidationError is thrown
        if a validation error occurs while building a model.
        """

        @pydantic.validate_arguments
        def test_sum(a: int, b: int) -> int:
            return a + b

        try:
            test_sum('a', 12)  # type: ignore [arg-type]
        except pydantic.ValidationError as test_exception:

            model_mock.side_effect = PydanticValidationError(exception=test_exception)

            with self.assertRaises(PydanticValidationError) as context:
                builder = ModelBuilder(TestModel)
                builder.build([], {})
            self.assertEqual(context.exception.kwargs['exception'], test_exception)

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
