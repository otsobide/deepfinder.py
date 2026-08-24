"""The fan-out operators: ``*``, ``?``, ``*?`` and its ``?*`` alias."""

import unittest
from typing import Any

from deepfinder import deep_find


class TestOperators(unittest.TestCase):
    def setUp(self) -> None:
        """Build a fixture where only some items resolve, so filtering is observable."""
        self.data: dict[str, Any] = {
            'pokemons': [
                {'name': 'pikachu'},
                {'name': 'charmander', 'ball': 'superball'},
                {'name': 'lucario', 'ball': 'ultraball'},
            ],
        }

    def test_all_keeps_position_and_length(self) -> None:
        """
        Test that '*' resolves every item, padding misses with None.

        The wildcard is positional: the result has one entry per item in the source
        sequence, so items that do not resolve leave a None behind rather than
        collapsing the list.

        Expected: deep_find(data, 'pokemons.*.ball') -> [None, 'superball', 'ultraball']
        """
        result = deep_find(self.data, 'pokemons.*.ball')
        self.assertEqual(result, [None, 'superball', 'ultraball'])

    def test_first_returns_first_non_none(self) -> None:
        """
        Test that '?' returns the first item that resolves to a non-None value.

        Expected: deep_find(data, 'pokemons.?.ball') -> 'superball'
        """
        result = deep_find(self.data, 'pokemons.?.ball')
        self.assertEqual(result, 'superball')

    def test_all_not_none_drops_misses(self) -> None:
        """
        Test that '*?' resolves every item and drops the Nones.

        Expected: deep_find(data, 'pokemons.*?.ball') -> ['superball', 'ultraball']
        """
        result = deep_find(self.data, 'pokemons.*?.ball')
        self.assertEqual(result, ['superball', 'ultraball'])

    def test_reversed_spelling_is_an_alias(self) -> None:
        """
        Test that '?*' is accepted as an alias of '*?'.

        Expected: deep_find(data, 'pokemons.?*.ball') == deep_find(data, 'pokemons.*?.ball')
        """
        self.assertEqual(
            deep_find(self.data, 'pokemons.?*.ball'),
            deep_find(self.data, 'pokemons.*?.ball'),
        )

    def test_all_on_empty_sequence(self) -> None:
        """
        Test that '*' over an empty sequence yields an empty list.

        Expected: deep_find({'values': []}, 'values.*.name') -> []
        """
        result = deep_find({'values': []}, 'values.*.name')
        self.assertEqual(result, [])

    def test_first_on_empty_sequence_falls_back_to_default(self) -> None:
        """
        Test that '?' over an empty sequence resolves to None and takes the default.

        Expected: deep_find({'values': []}, 'values.?.name', default='d') -> 'd'
        """
        result = deep_find({'values': []}, 'values.?.name', default='d')
        self.assertEqual(result, 'd')

    def test_all_never_takes_the_default(self) -> None:
        """
        Test that '*' returns a list of Nones rather than the default.

        A list is never None, so the default substitution in deep_find cannot fire
        for '*' no matter how many items fail to resolve.

        Expected: deep_find([{'a': 1}], '*.missing', default='d') -> [None]
        """
        result = deep_find([{'a': 1}], '*.missing', default='d')
        self.assertEqual(result, [None])

    def test_all_not_none_never_takes_the_default(self) -> None:
        """
        Test that '*?' returns an empty list rather than the default.

        Expected: deep_find([{'a': 1}], '*?.missing', default='d') -> []
        """
        result = deep_find([{'a': 1}], '*?.missing', default='d')
        self.assertEqual(result, [])

    def test_nested_wildcards_do_not_share_state(self) -> None:
        """
        Test that a wildcard inside a wildcard resolves each branch independently.

        Every branch consumes the same remaining path, so a traversal that mutated
        shared state would return results only for the first branch.

        Expected: deep_find({'g': [{'p': [{'n': 'a'}]}, {'p': [{'n': 'b'}, {'n': 'c'}]}]},
                            'g.*.p.*.n') -> [['a'], ['b', 'c']]
        """
        data: dict[str, Any] = {
            'g': [
                {'p': [{'n': 'a'}]},
                {'p': [{'n': 'b'}, {'n': 'c'}]},
            ],
        }
        result = deep_find(data, 'g.*.p.*.n')
        self.assertEqual(result, [['a'], ['b', 'c']])

    def test_first_does_not_consume_the_path_for_later_items(self) -> None:
        """
        Test that '?' can inspect every item, not just the first one.

        The first two items miss, so the operator must still hold an intact path
        when it reaches the third.

        Expected: deep_find({'v': [{'a': 1}, {'b': 2}, {'c': 3}]}, 'v.?.c') -> 3
        """
        data: dict[str, Any] = {'v': [{'a': 1}, {'b': 2}, {'c': 3}]}
        result = deep_find(data, 'v.?.c')
        self.assertEqual(result, 3)

    def test_operator_combined_with_negative_index(self) -> None:
        """
        Test that a fan-out operator composes with a negative index.

        Expected: deep_find({'v': [['a', 'b'], ['c', 'd']]}, 'v.*.-1') -> ['b', 'd']
        """
        data: dict[str, Any] = {'v': [['a', 'b'], ['c', 'd']]}
        result = deep_find(data, 'v.*.-1')
        self.assertEqual(result, ['b', 'd'])

    def test_trailing_all_returns_the_items_themselves(self) -> None:
        """
        Test that a path ending in '*' returns the sequence items unchanged.

        Expected: deep_find({'v': [1, 2, 3]}, 'v.*') -> [1, 2, 3]
        """
        result = deep_find({'v': [1, 2, 3]}, 'v.*')
        self.assertEqual(result, [1, 2, 3])

    def test_operators_are_inert_outside_a_sequence(self) -> None:
        """
        Test that '*' against a dictionary is treated as an ordinary key.

        The mapping branch wins over the sequence branch, so the operator is looked
        up as a literal key and misses.

        Expected: deep_find({'a': 1}, '*') -> None
        """
        self.assertIsNone(deep_find({'a': 1}, '*'))


if __name__ == '__main__':
    unittest.main()
