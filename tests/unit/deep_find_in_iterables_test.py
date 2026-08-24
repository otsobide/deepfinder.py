"""Arbitrary iterables, which are materialised before being indexed."""

import unittest

from deepfinder import deep_find


class TestFindInIterables(unittest.TestCase):
    def test_range(self) -> None:
        """
        Test that a range is indexable.

        Expected: deep_find(range(10), '3') -> 3
        """
        self.assertEqual(deep_find(range(10), '3'), 3)

    def test_iterator(self) -> None:
        """
        Test that a plain iterator is materialised and indexed.

        Expected: deep_find(iter(['a', 'b']), '1') -> 'b'
        """
        self.assertEqual(deep_find(iter(['a', 'b']), '1'), 'b')

    def test_generator(self) -> None:
        """
        Test that a generator is materialised and indexed.

        Expected: deep_find((i for i in range(5)), '2') -> 2
        """
        self.assertEqual(deep_find((i for i in range(5)), '2'), 2)

    def test_a_lookup_consumes_the_generator(self) -> None:
        """
        Test that a lookup moves a generator forward.

        Items read to reach the index are gone, so the same path resolves to
        something different the second time. Callers that need repeated lookups
        should pass a concrete sequence.

        Expected: the same generator resolves index 2 once, then misses
        """
        values = (i for i in range(5))
        self.assertEqual(deep_find(values, '2'), 2)
        self.assertIsNone(deep_find(values, '2'))

    def test_dictionary_view(self) -> None:
        """
        Test that a dictionary view is materialised into its items.

        Expected: deep_find({'a': 1, 'b': 2}.keys(), '1') -> 'b'
        """
        self.assertEqual(deep_find({'a': 1, 'b': 2}.keys(), '1'), 'b')

    def test_bytes_are_indexed_as_integers(self) -> None:
        """
        Test that bytes behave like any other non-string iterable.

        Only str is excluded from materialisation, so bytes resolve to the integer
        values of their elements.

        Expected: deep_find(b'abc', '0') -> 97
        """
        self.assertEqual(deep_find(b'abc', '0'), 97)

    def test_bytearray_is_indexed_as_integers(self) -> None:
        """
        Test that bytearray matches the bytes behaviour.

        Expected: deep_find(bytearray(b'abc'), '1') -> 98
        """
        self.assertEqual(deep_find(bytearray(b'abc'), '1'), 98)

    def test_strings_are_not_indexable(self) -> None:
        """
        Test that a string is never traversed as a sequence.

        Strings are excluded so that a path does not accidentally walk into
        individual characters.

        Expected: deep_find({'s': 'abc'}, 's.0') -> None
        """
        self.assertIsNone(deep_find({'s': 'abc'}, 's.0'))

    def test_nested_generator(self) -> None:
        """
        Test that a generator nested in a dictionary is materialised.

        Expected: deep_find({'v': (i for i in [10, 20])}, 'v.*') -> [10, 20]
        """
        self.assertEqual(deep_find({'v': (i for i in [10, 20])}, 'v.*'), [10, 20])


if __name__ == '__main__':
    unittest.main()
