"""The DeepFinderList and DeepFinderDict container subclasses."""

import unittest

from deepfinder.entity import DeepFinderDict, DeepFinderList


class TestNativeDeepFind(unittest.TestCase):
    def test_deep_finder_list(self) -> None:
        """
        Test that DeepFinderList can access elements using the deep_find method.

        This test verifies that the DeepFinderList class properly wraps a list
        and allows accessing its elements using the deep_find method. It tests
        the basic functionality of accessing elements in a list using numeric
        indices through the native deep_find interface.

        Expected: DeepFinderList(['a', 'b', 'c']).deep_find('0') -> 'a'
        """
        data = DeepFinderList(['a', 'b', 'c'])
        result = data.deep_find('0')
        self.assertEqual(result, 'a')

    def test_deep_finder_dict(self) -> None:
        """
        Test that DeepFinderDict can access elements using the deep_find method.

        This test verifies that the DeepFinderDict class properly wraps a dictionary
        and allows accessing its elements using the deep_find method. It tests
        the basic functionality of accessing values in a dictionary using keys
        through the native deep_find interface.

        Expected: DeepFinderDict({'a': 'b', 'c': 'd'}).deep_find('a') -> 'b'
        """
        data = DeepFinderDict({'a': 'b', 'c': 'd'})
        result = data.deep_find('a')
        self.assertEqual(result, 'b')


if __name__ == '__main__':
    unittest.main()
