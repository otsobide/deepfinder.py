"""Primitive values, bare and nested inside a dictionary."""

import unittest
from typing import Any

from deepfinder import deep_find


class TestFindByType(unittest.TestCase):
    def test_with_basic_number(self) -> None:
        """
        Test that deep_find can handle primitive integer values.

        When given a simple integer and an empty path, deep_find should return
        the integer value itself. This verifies that the function can handle
        primitive numeric types without any nesting.

        Expected: deep_find(39, '') -> 39
        """
        data: int = 39
        result = deep_find(data, '')
        self.assertEqual(result, 39)

    def test_with_number_in_dict(self) -> None:
        """
        Test that deep_find can retrieve integer values from a dictionary.

        When given a dictionary containing an integer value, deep_find should
        be able to access that value using the appropriate key path. This
        verifies that the function can handle numeric values within a
        dictionary structure.

        Expected: deep_find({'value': 39}, 'value') -> 39
        """
        data: dict[str, Any] = {
            'value': 39,
        }
        result = deep_find(data, 'value')
        self.assertEqual(result, 39)

    def test_with_basic_str(self) -> None:
        """
        Test that deep_find can handle primitive string values.

        When given a simple string and an empty path, deep_find should return
        the string value itself. This verifies that the function can handle
        primitive string types without any nesting.

        Expected: deep_find('test str', '') -> 'test str'
        """
        data: str = 'test str'
        result = deep_find(data, '')
        self.assertEqual(result, 'test str')

    def test_with_str_in_dict(self) -> None:
        """
        Test that deep_find can retrieve string values from a dictionary.

        When given a dictionary containing a string value, deep_find should
        be able to access that value using the appropriate key path. This
        verifies that the function can handle string values within a
        dictionary structure.

        Expected: deep_find({'value': 'test str'}, 'value') -> 'test str'
        """
        data: dict[str, Any] = {
            'value': 'test str',
        }
        result = deep_find(data, 'value')
        self.assertEqual(result, 'test str')


if __name__ == '__main__':
    unittest.main()
