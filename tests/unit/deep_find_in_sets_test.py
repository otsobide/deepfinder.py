"""Sets, which are materialised before being indexed."""

import unittest
from typing import Any

from deepfinder import deep_find


class TestFindInSets(unittest.TestCase):
    def test_first_value_of_a_set(self) -> None:
        """
        Test that deep_find can access the first value of a set using numeric index.

        This test verifies that deep_find can access elements in a set using
        numeric indices. Which member lands at index 0 is whatever the set
        iterates first, so only membership is asserted.

        Expected: deep_find({1, 2, 3}, '0') -> one of its members
        """
        data = {1, 2, 3}
        result = deep_find(data, '0')
        self.assertIn(result, {1, 2, 3})

    def test_set_access_by_non_numeric_value(self) -> None:
        """
        Test that deep_find returns None when trying to access a set with a non-numeric index.

        This test verifies that deep_find handles invalid access attempts gracefully
        when trying to access a set using a non-numeric index. Since sets can
        only be accessed by numeric indices, any other type of index should
        return None.

        Expected: deep_find({1, 2, 3}, 'b') -> None
        """
        data = {1, 2, 3}
        result = deep_find(data, 'b')
        self.assertEqual(result, None)

    def test_set_access_by_not_hashable_json(self) -> None:
        """
        Test that deep_find returns None when trying to access a set with a non-hashable index.

        This test verifies that deep_find handles attempts to access a set using
        a non-hashable value (like a list) as the index. Since set indices must
        be integers, any attempt to use a non-hashable value as an index should
        return None.

        Expected: deep_find({1, 2, 3}, '[]') -> None
        """
        data = {1, 2, 3}
        result = deep_find(data, '[]')
        self.assertEqual(result, None)

    def test_first_value_of_embedded_set(self) -> None:
        """
        Test that deep_find can access the first value of a set nested within a dictionary.

        This test verifies that deep_find can access elements in a set that is
        embedded within a dictionary structure. It tests the ability to traverse
        through a dictionary to reach a set and then access its elements.

        Expected: deep_find({'values': {1, 2, 3}}, 'values.0') -> one of its members
        """
        data: dict[str, Any] = {
            'values': {1, 2, 3},
        }
        result = deep_find(data, 'values.0')
        self.assertIn(result, {1, 2, 3})

    def test_all_values_of_set(self) -> None:
        """
        Test that deep_find can retrieve all values from a set using the wildcard operator.

        This test verifies that deep_find can use the wildcard operator (*) to
        retrieve all values from a set that is embedded within a dictionary.
        It tests the ability to access all elements of a set in a single operation.

        Expected: deep_find({'values': {1, 2, 3}}, 'values.*') -> every member, in iteration order
        """
        data: dict[str, Any] = {
            'values': {1, 2, 3},
        }
        result = deep_find(data, 'values.*')
        self.assertEqual(result, list({1, 2, 3}))


if __name__ == '__main__':
    unittest.main()
