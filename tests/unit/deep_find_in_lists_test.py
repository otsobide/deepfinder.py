"""List traversal, including the fan-out operators and nested lists."""

import unittest
from typing import Any

from deepfinder import deep_find


class TestFindInLists(unittest.TestCase):
    def test_first_value_of_a_list(self) -> None:
        """
        Test that deep_find can access the first value of a list using numeric index.

        This test verifies that deep_find can access elements in a list using
        numeric indices. It tests the basic functionality of accessing the
        first element (index 0) of a list.

        Expected: deep_find(['a', 'b', 'c'], '0') -> 'a'
        """
        data: list[str] = ['a', 'b', 'c']
        result = deep_find(data, '0')
        self.assertEqual(result, 'a')

    def test_array_access_by_non_numeric_value(self) -> None:
        """
        Test that deep_find returns None when trying to access a list with a non-numeric index.

        This test verifies that deep_find handles invalid access attempts gracefully
        when trying to access a list using a non-numeric index. Since lists can
        only be accessed by numeric indices, any other type of index should
        return None.

        Expected: deep_find(['a', 'b', 'c'], 'b') -> None
        """
        data: list[str] = ['a', 'b', 'c']
        result = deep_find(data, 'b')
        self.assertEqual(result, None)

    def test_array_access_by_not_hashable_json(self) -> None:
        """
        Test that deep_find returns None when trying to access a list with a non-hashable index.

        This test verifies that deep_find handles attempts to access a list using
        a non-hashable value (like a list) as the index. Since list indices must
        be integers, any attempt to use a non-hashable value as an index should
        return None.

        Expected: deep_find(['a', 'b', 'c'], '[]') -> None
        """
        data: list[str] = ['a', 'b', 'c']
        result = deep_find(data, '[]')
        self.assertEqual(result, None)

    def test_first_value_of_embedded_list(self) -> None:
        """
        Test that deep_find can access the first value of a list nested within a dictionary.

        This test verifies that deep_find can access elements in a list that is
        embedded within a dictionary structure. It tests the ability to traverse
        through a dictionary to reach a list and then access its elements.

        Expected: deep_find({'values': ['a', 'b', 'c']}, 'values.0') -> 'a'
        """
        data: dict[str, Any] = {
            'values': ['a', 'b', 'c'],
        }
        result = deep_find(data, 'values.0')
        self.assertEqual(result, 'a')

    def test_all_values_of_list(self) -> None:
        """
        Test that deep_find can retrieve all values from a list using the wildcard operator.

        This test verifies that deep_find can use the wildcard operator (*) to
        retrieve all values from a list that is embedded within a dictionary.
        It tests the ability to access all elements of a list in a single operation.

        Expected: deep_find({'values': ['a', 'b', 'c']}, 'values.*') -> ['a', 'b', 'c']
        """
        data: dict[str, Any] = {
            'values': ['a', 'b', 'c'],
        }
        result = deep_find(data, 'values.*')
        self.assertEqual(result, data['values'])

    def test_first_value_in_dict_of_a_list(self) -> None:
        """
        Test that deep_find can access a value in a dictionary that is the first element of a list.

        This test verifies that deep_find can traverse through a list of dictionaries
        and access a specific value in the first dictionary. It tests the ability
        to combine list indexing with dictionary key access.

        Expected: deep_find({'values': [{'value': 'a'}, {'value': 'b'}, {'value': 'c'}]},
                 'values.0.value') -> 'a'
        """
        data: dict[str, Any] = {
            'values': [
                {
                    'value': 'a',
                },
                {
                    'value': 'b',
                },
                {
                    'value': 'c',
                },
            ],
        }
        result = deep_find(data, 'values.0.value')
        self.assertEqual(result, 'a')

    def test_all_values_of_a_list(self) -> None:
        """
        Test that deep_find can retrieve all values of a specific key from a list of dictionaries.

        This test verifies that deep_find can use the wildcard operator to collect
        all values of a specific key from each dictionary in a list. It tests the
        ability to perform a map-like operation across a list of dictionaries.

        Expected: deep_find({'values': [{'value': 'a'}, {'value': 'b'}, {'value': 'c'}]},
                 'values.*.value') -> ['a', 'b', 'c']
        """
        data: dict[str, Any] = {
            'values': [
                {
                    'value': 'a',
                },
                {
                    'value': 'b',
                },
                {
                    'value': 'c',
                },
            ],
        }
        result = deep_find(data, 'values.*.value')
        self.assertEqual(result, [value['value'] for value in data['values']])

    def test_existing_path_values_of_a_list(self) -> None:
        """
        Test that deep_find can find the first dictionary in a list that has a specific key.

        This test verifies that deep_find can use the first match operator (?) to
        find the first dictionary in a list that contains a specific key. It tests
        the ability to search through a list of dictionaries for the first valid path.

        Expected: deep_find({'values': [{'nya': 'a'}, {'value': 'b'}, {'nya': 'c'}]},
                 'values.?.value') -> 'b'
        """
        data: dict[str, Any] = {
            'values': [
                {
                    'nya': 'a',
                },
                {
                    'value': 'b',
                },
                {
                    'nya': 'c',
                },
            ],
        }
        result = deep_find(data, 'values.?.value')
        self.assertEqual(result, 'b')

    def test_all_values_of_a_list_inside_list(self) -> None:
        """
        Test that deep_find can retrieve all nested lists from a list of dictionaries.

        This test verifies that deep_find can use the wildcard operator to collect
        all lists that are values of a specific key in a list of dictionaries.
        It tests the ability to handle nested list structures within dictionaries.

        Expected: deep_find({'all-values': [{'values': ['a']}, {'values': ['b', 'c', 'd']},
                 {'values': ['e']}]}, 'all-values.*.values') -> [['a'], ['b', 'c', 'd'], ['e']]
        """
        data: dict[str, Any] = {
            'all-values': [
                {
                    'values': ['a'],
                },
                {
                    'values': ['b', 'c', 'd'],
                },
                {
                    'values': ['e'],
                },
            ],
        }
        result = deep_find(data, 'all-values.*.values')
        self.assertEqual(result, [['a'], ['b', 'c', 'd'], ['e']])

    def test_complete_list_inside_list(self) -> None:
        """
        Test that deep_find can retrieve all nested lists from a list of lists.

        This test verifies that deep_find can use the wildcard operator to collect
        all lists that are elements of another list. It tests the ability to
        handle nested list structures without dictionaries.

        Expected: deep_find({'all-values': [['a'], ['b', 'c', 'd'], ['e']]},
                 'all-values.*.*') -> [['a'], ['b', 'c', 'd'], ['e']]
        """
        data: dict[str, Any] = {
            'all-values': [['a'], ['b', 'c', 'd'], ['e']],
        }
        result = deep_find(data, 'all-values.*.*')
        self.assertEqual(result, [['a'], ['b', 'c', 'd'], ['e']])

    def test_first_value_of_list_inside_list(self) -> None:
        """
        Test that deep_find can retrieve the first value from each nested list.

        This test verifies that deep_find can use the wildcard operator to collect
        the first element from each list in a list of lists. It tests the ability
        to perform a map-like operation across nested lists.

        Expected: deep_find({'all-values': [['a'], ['b', '3', '4'], ['c']]},
                 'all-values.*.0') -> ['a', 'b', 'c']
        """
        data: dict[str, Any] = {
            'all-values': [['a'], ['b', '3', '4'], ['c']],
        }
        result = deep_find(data, 'all-values.*.0')
        self.assertEqual(result, ['a', 'b', 'c'])

    def test_existing_path_of_list_inside_list(self) -> None:
        """
        Test that deep_find can find the first list that has a value at a specific index.

        This test verifies that deep_find can use the first match operator (?) to
        find the first list that has a value at a specific index. It tests the
        ability to search through nested lists for the first valid index.

        Expected: deep_find({'all-values': [['a'], ['b', 'c', 'd'], ['e']]},
                 'all-values.?.2') -> 'd'
        """
        data: dict[str, Any] = {
            'all-values': [['a'], ['b', 'c', 'd'], ['e']],
        }
        result = deep_find(data, 'all-values.?.2')
        self.assertEqual(result, 'd')

    def test_existing_path_inside_existing_path(self) -> None:
        """
        Test that several first-match operators (?) can be chained in one path.

        This test verifies that deep_find can use multiple first match operators (?) to
        find a value in a complex nested structure. It tests the ability to search
        through multiple levels of nesting to find the first valid path.

        Expected: deep_find({'all-values': [['a'], ['b', {'correct': 'correct'}, 'c'], ['d']]},
                 'all-values.?.?.correct') -> 'correct'
        """
        data: dict[str, Any] = {
            'all-values': [['a'], ['b', {'correct': 'correct'}, 'c'], ['d']],
        }
        result = deep_find(data, 'all-values.?.?.correct')
        self.assertEqual(result, 'correct')


if __name__ == '__main__':
    unittest.main()
