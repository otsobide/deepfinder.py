"""Dictionary traversal at increasing nesting depths."""

import unittest
from typing import Any

from deepfinder import deep_find


class TestFindInDicts(unittest.TestCase):
    def test_dict_with_0_lvl(self) -> None:
        """
        Test that deep_find returns the entire dictionary when given an empty path.

        This test verifies that when deep_find is called with an empty path string,
        it returns the entire input dictionary. This is useful when you want to
        get the whole dictionary structure without accessing any specific key.

        Expected: deep_find({'value': 39}, '') -> {'value': 39}
        """
        data: dict[str, Any] = {
            'value': 39,
        }
        result = deep_find(data, '')
        self.assertEqual(result, data)

    def test_dict_with_1_lvl(self) -> None:
        """
        Test that deep_find can access a value in a single-level dictionary.

        This test verifies that deep_find can correctly access a value in a
        dictionary with no nesting (depth level 1). It tests the basic
        functionality of accessing a direct key-value pair.

        Expected: deep_find({'value': 39}, 'value') -> 39
        """
        data: dict[str, Any] = {
            'value': 39,
        }
        result = deep_find(data, 'value')
        self.assertEqual(result, 39)

    def test_dict_with_2_lvl(self) -> None:
        """
        Test that deep_find can access a value in a two-level nested dictionary.

        This test verifies that deep_find can correctly traverse a dictionary
        with one level of nesting (depth level 2). It tests the ability to
        access a value that is nested one level deep using dot notation.

        Expected: deep_find({'value': {'subdata': 39}}, 'value.subdata') -> 39
        """
        data: dict[str, Any] = {
            'value': {
                'subdata': 39,
            },
        }
        result = deep_find(data, 'value.subdata')
        self.assertEqual(result, 39)

    def test_dict_with_3_lvl(self) -> None:
        """
        Test that deep_find can access a value in a three-level nested dictionary.

        This test verifies that deep_find can correctly traverse a dictionary
        with two levels of nesting (depth level 3). It tests the ability to
        access a value that is nested two levels deep using dot notation,
        including handling of keys with hyphens.

        Expected: deep_find({'value': {'sub-data': {'sub-sub-data': 39}}},
                 'value.sub-data.sub-sub-data') -> 39
        """
        data: dict[str, Any] = {
            'value': {
                'sub-data': {
                    'sub-sub-data': 39,
                },
            },
        }
        result = deep_find(data, 'value.sub-data.sub-sub-data')
        self.assertEqual(result, 39)


if __name__ == '__main__':
    unittest.main()
