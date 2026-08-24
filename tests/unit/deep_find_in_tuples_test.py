"""Tuples, which are materialised before being indexed."""

import unittest
from typing import Any

from deepfinder import deep_find


class TestFindInTuples(unittest.TestCase):
    def test_first_value_of_a_tuple(self) -> None:
        """
        Test that deep_find can access the first value of a tuple using numeric index.

        This test verifies that deep_find can access elements in a tuple using
        numeric indices. It tests the basic functionality of accessing the
        first element (index 0) of a tuple.

        Expected: deep_find((1, 2, 3), '0') -> 1
        """
        data = (1, 2, 3)
        result = deep_find(data, '0')
        self.assertEqual(result, 1)

    def test_tuple_access_by_non_numeric_value(self) -> None:
        """
        Test that deep_find returns None when trying to access a tuple with a non-numeric index.

        This test verifies that deep_find handles invalid access attempts gracefully
        when trying to access a tuple using a non-numeric index. Since tuples can
        only be accessed by numeric indices, any other type of index should
        return None.

        Expected: deep_find((1, 2, 3), 'b') -> None
        """
        data = (1, 2, 3)
        result = deep_find(data, 'b')
        self.assertEqual(result, None)

    def test_tuple_access_by_not_hashable_json(self) -> None:
        """
        Test that deep_find returns None when trying to access a tuple with a non-hashable index.

        This test verifies that deep_find handles attempts to access a tuple using
        a non-hashable value (like a list) as the index. Since tuple indices must
        be integers, any attempt to use a non-hashable value as an index should
        return None.

        Expected: deep_find((1, 2, 3), '[]') -> None
        """
        data = (1, 2, 3)
        result = deep_find(data, '[]')
        self.assertEqual(result, None)

    def test_first_value_of_embedded_tuple(self) -> None:
        """
        Test that deep_find can access the first value of a tuple nested within a dictionary.

        This test verifies that deep_find can access elements in a tuple that is
        embedded within a dictionary structure. It tests the ability to traverse
        through a dictionary to reach a tuple and then access its elements.

        Expected: deep_find({'values': (1, 2, 3)}, 'values.0') -> 1
        """
        data: dict[str, Any] = {
            'values': (1, 2, 3),
        }
        result = deep_find(data, 'values.0')
        self.assertEqual(result, 1)

    def test_all_values_of_tuple(self) -> None:
        """
        Test that deep_find can retrieve all values from a tuple using the wildcard operator.

        This test verifies that deep_find can use the wildcard operator (*) to
        retrieve all values from a tuple that is embedded within a dictionary.
        It tests the ability to access all elements of a tuple in a single operation.

        Expected: deep_find({'values': (1, 2, 3)}, 'values.*') -> [1, 2, 3]
        """
        data: dict[str, Any] = {
            'values': (1, 2, 3),
        }
        result = deep_find(data, 'values.*')
        self.assertEqual(result, [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
