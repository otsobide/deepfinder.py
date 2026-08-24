"""Mappings that are not dict subclasses."""

import unittest
from collections import ChainMap, OrderedDict, UserDict, defaultdict
from types import MappingProxyType
from typing import Any

from deepfinder import deep_find


class TestFindInMappings(unittest.TestCase):
    def test_chain_map(self) -> None:
        """
        Test that a ChainMap resolves by key.

        ChainMap is a Mapping but not a dict subclass, so it used to fall through to
        the sequence branch and be walked as a list of its keys.

        Expected: deep_find(ChainMap({'a': 1}, {'b': 2}), 'b') -> 2
        """
        self.assertEqual(deep_find(ChainMap({'a': 1}, {'b': 2}), 'b'), 2)

    def test_mapping_proxy(self) -> None:
        """
        Test that a read-only mapping proxy resolves by key.

        Expected: deep_find(MappingProxyType({'n': 'ash'}), 'n') -> 'ash'
        """
        self.assertEqual(deep_find(MappingProxyType({'n': 'ash'}), 'n'), 'ash')

    def test_user_dict(self) -> None:
        """
        Test that a UserDict resolves by key.

        Expected: deep_find(UserDict({'n': 'ash'}), 'n') -> 'ash'
        """
        self.assertEqual(deep_find(UserDict({'n': 'ash'}), 'n'), 'ash')

    def test_nested_mapping(self) -> None:
        """
        Test that a mapping nested under a dictionary is traversed.

        Expected: deep_find({'env': MappingProxyType({'HOME': '/root'})}, 'env.HOME') -> '/root'
        """
        data: dict[str, Any] = {'env': MappingProxyType({'HOME': '/root'})}
        self.assertEqual(deep_find(data, 'env.HOME'), '/root')

    def test_missing_key_falls_back_to_index_semantics(self) -> None:
        """
        Test that a missing key keeps the pre-1.6 behaviour of indexing the keys.

        A miss falls through to the sequence branch, so numeric segments still return
        the key at that position and nothing that resolved before stops resolving.

        Expected: deep_find(ChainMap({'a': 1, 'b': 2}), '0') -> 'a'
        """
        self.assertEqual(deep_find(ChainMap({'a': 1, 'b': 2}), '0'), 'a')

    def test_dict_subclasses_are_unaffected(self) -> None:
        """
        Test that dict subclasses keep going through the fast mapping path.

        Expected: OrderedDict and defaultdict resolve by key
        """
        self.assertEqual(deep_find(OrderedDict([('a', 1)]), 'a'), 1)
        self.assertEqual(deep_find(defaultdict(int, {'a': 1}), 'a'), 1)

    def test_dict_miss_does_not_fall_back_to_indexing(self) -> None:
        """
        Test that a plain dict miss stays a miss.

        Falling through for dicts would make deep_find({'a': 1}, '0') return the key
        'a', which is not what a mapping lookup means.

        Expected: deep_find({'a': 1}, '0') -> None
        """
        self.assertIsNone(deep_find({'a': 1}, '0'))

    def test_mapping_with_a_raising_getitem(self) -> None:
        """
        Test that an exploding __getitem__ cannot escape the lookup.

        Expected: deep_find(Exploding(), 'anything', default='d') -> 'd'
        """

        class Exploding(UserDict[str, object]):
            def __getitem__(self, key: object) -> object:
                msg = 'nope'
                raise RuntimeError(msg)

        self.assertEqual(deep_find(Exploding(), 'anything', default='d'), 'd')


if __name__ == '__main__':
    unittest.main()
