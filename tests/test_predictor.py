import unittest

from predictor import validate_prediction_input


class TestPredictorValidation(unittest.TestCase):

    def test_valid_input(self):
        errors = validate_prediction_input(
            120,
            "3",
            2,
            "Cairo",
            "Madinaty",
            "1st District",
            "1st Neighborhood",
            "No",
            "completed",
        )

        self.assertEqual(errors, [])

    def test_invalid_area(self):
        errors = validate_prediction_input(
            -50,
            "3",
            2,
            "Cairo",
            "Madinaty",
            "1st District",
            "1st Neighborhood",
            "No",
            "completed",
        )

        self.assertIn("Area must be a positive number.", errors)


if __name__ == "__main__":
    unittest.main()
