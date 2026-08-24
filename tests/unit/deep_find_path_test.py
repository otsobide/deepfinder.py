"""Path parsing: separators, empty paths and argument validation."""

import unittest
from typing import Any

from deepfinder import deep_find


class TestPathParsing(unittest.TestCase):
    def test_empty_path_returns_the_object(self) -> None:
        """
        Test that an empty path returns the object untouched.

        Expected: deep_find({'a': 1}, '') -> {'a': 1}
        """
        data: dict[str, Any] = {'a': 1}
        self.assertEqual(deep_find(data, ''), data)

    def test_empty_path_on_none_takes_the_default(self) -> None:
        """
        Test that an empty path over None still goes through default substitution.

        Expected: deep_find(None, '', default='d') -> 'd'
        """
        self.assertEqual(deep_find(None, '', default='d'), 'd')

    def test_custom_single_character_separator(self) -> None:
        """
        Test that path_token replaces the dot.

        Expected: deep_find({'a': {'b': 2}}, 'a/b', path_token='/') -> 2
        """
        self.assertEqual(deep_find({'a': {'b': 2}}, 'a/b', path_token='/'), 2)

    def test_custom_multi_character_separator(self) -> None:
        """
        Test that path_token may be longer than one character.

        Expected: deep_find({'a': {'b': 2}}, 'a::b', path_token='::') -> 2
        """
        self.assertEqual(deep_find({'a': {'b': 2}}, 'a::b', path_token='::'), 2)

    def test_custom_separator_frees_the_dot(self) -> None:
        """
        Test that a custom separator makes dotted keys reachable.

        Keys containing the active separator cannot be addressed, so a different
        path_token is the supported way to read them.

        Expected: deep_find({'a.b': 1}, 'a.b')                  -> None
                  deep_find({'a.b': 1}, 'a.b', path_token='/')  -> 1
        """
        data: dict[str, Any] = {'a.b': 1}
        self.assertIsNone(deep_find(data, 'a.b'))
        self.assertEqual(deep_find(data, 'a.b', path_token='/'), 1)

    def test_empty_segment_addresses_the_empty_key(self) -> None:
        """
        Test that consecutive separators address an empty-string key.

        Expected: deep_find({'a': {'': {'b': 1}}}, 'a..b') -> 1
        """
        self.assertEqual(deep_find({'a': {'': {'b': 1}}}, 'a..b'), 1)

    def test_empty_separator_is_rejected(self) -> None:
        """
        Test that an empty path_token raises a clear ValueError.

        str.split rejects an empty separator, so the failure used to surface as an
        opaque ValueError('empty separator') from deep inside the call.

        Expected: deep_find({'a': 1}, 'a', path_token='') -> ValueError
        """
        with self.assertRaises(ValueError) as ctx:
            deep_find({'a': 1}, 'a', path_token='')
        self.assertIn('path_token', str(ctx.exception))

    def test_non_string_path_is_rejected(self) -> None:
        """
        Test that a non-string path raises TypeError rather than AttributeError.

        Expected: deep_find({'a': 1}, 1) -> TypeError
        """
        with self.assertRaises(TypeError) as ctx:
            deep_find({'a': 1}, 1)  # type: ignore[arg-type]
        self.assertIn('path must be a str', str(ctx.exception))

    def test_none_path_is_rejected(self) -> None:
        """
        Test that None is rejected as a path.

        Expected: deep_find({'a': 1}, None) -> TypeError
        """
        with self.assertRaises(TypeError):
            deep_find({'a': 1}, None)  # type: ignore[arg-type]

    def test_missing_intermediate_segment_stops_the_walk(self) -> None:
        """
        Test that a miss halfway through the path resolves to the default.

        Expected: deep_find({'a': {'b': 1}}, 'a.x.b.c.d', default='d') -> 'd'
        """
        self.assertEqual(deep_find({'a': {'b': 1}}, 'a.x.b.c.d', default='d'), 'd')

    def test_lookup_on_none_never_raises(self) -> None:
        """
        Test that traversing into None resolves to the default.

        Expected: deep_find(None, 'a.b.c', default='d') -> 'd'
        """
        self.assertEqual(deep_find(None, 'a.b.c', default='d'), 'd')

    def test_integer_dictionary_keys_are_unreachable(self) -> None:
        """
        Test that non-string dictionary keys cannot be addressed.

        Segments are always strings, and the mapping branch looks them up verbatim,
        so an integer key never matches.

        Expected: deep_find({0: 'zero'}, '0') -> None
        """
        self.assertIsNone(deep_find({0: 'zero'}, '0'))


class TestDefaultSubstitution(unittest.TestCase):
    def test_falsy_values_are_returned_as_is(self) -> None:
        """
        Test that falsy results are not replaced by the default.

        Substitution keys off None specifically, not off truthiness.

        Expected: False, 0, '' and [] all survive default substitution
        """
        values: tuple[Any, ...] = (False, 0, '', [])
        for value in values:
            with self.subTest(value=value):
                self.assertEqual(deep_find({'a': value}, 'a', default='d'), value)

    def test_stored_none_yields_the_default(self) -> None:
        """
        Test that a stored None is indistinguishable from a miss.

        deep_find cannot tell "resolved to None" from "did not resolve", so a key
        whose value is genuinely None also yields the default. This is documented
        rather than changed, because changing it would alter working lookups.

        Expected: deep_find({'a': None}, 'a', default='d') -> 'd'
        """
        self.assertEqual(deep_find({'a': None}, 'a', default='d'), 'd')


if __name__ == '__main__':
    unittest.main()
