"""Attribute lookups on plain class instances."""

import unittest

from deepfinder import deep_find


class TestFindInClass(unittest.TestCase):
    def test_class_attributes(self) -> None:
        """
        Test that deep_find can access attributes of a custom class instance.

        This test verifies that deep_find can access instance attributes of a
        custom class using dot notation. It tests the basic functionality of
        accessing a single-level attribute on a class instance.

        The test creates a simple class with an instance attribute and verifies
        that deep_find can retrieve that attribute's value using the attribute
        name as the path.

        Expected: deep_find(CustomClass(), 'a') -> 'test'
        """

        class CustomClass:
            def __init__(self) -> None:
                self.a = 'test'

        data: CustomClass = CustomClass()
        result = deep_find(data, 'a')
        self.assertEqual(result, 'test')


if __name__ == '__main__':
    unittest.main()
