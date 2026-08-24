"""The deprecated nativify() builtins patch."""

import builtins
import unittest
import warnings
from typing import Any, cast

from deepfinder import deep_find
from deepfinder.entity import DeepFinderDict, DeepFinderList, nativify


class TestNativify(unittest.TestCase):
    def setUp(self) -> None:
        """Remember the real builtins so the patch cannot leak into other tests."""
        self._list = builtins.list
        self._dict = builtins.dict

    def tearDown(self) -> None:
        """Restore the real builtins."""
        builtins.list = self._list  # type: ignore[misc]
        builtins.dict = self._dict  # type: ignore[misc]

    @staticmethod
    def _nativify_quietly() -> None:
        """Apply the patch without letting the deprecation warning fail the run."""
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            nativify()

    def test_emits_a_deprecation_warning(self) -> None:
        """
        Test that calling nativify warns that it is deprecated.

        Expected: nativify() -> DeprecationWarning
        """
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            nativify()
        self.assertEqual(len(caught), 1)
        self.assertIs(caught[0].category, DeprecationWarning)
        self.assertIn('deprecated', str(caught[0].message))

    def test_rebinds_the_builtins(self) -> None:
        """
        Test that the builtin constructors are replaced by the DeepFinder subclasses.

        Expected: builtins.list is DeepFinderList and builtins.dict is DeepFinderDict
        """
        self._nativify_quietly()
        self.assertIs(builtins.list, DeepFinderList)
        self.assertIs(builtins.dict, DeepFinderDict)

    def test_constructed_containers_gain_the_method(self) -> None:
        """
        Test that containers built through the constructors can deep_find.

        Regression: this returned None. Rebinding builtins.dict also rebound the name
        that the traversal used for its isinstance checks, so a plain dict stopped
        being recognised as a mapping and fell through to the sequence branch, where
        it was materialised into its keys. The traversal now holds the real types,
        captured at import time.

        Expected: list([{'name': 'pikachu'}]).deep_find('0.name') -> 'pikachu'
        """
        self._nativify_quietly()
        built = cast('DeepFinderList[Any]', builtins.list([{'name': 'pikachu'}]))
        self.assertEqual(built.deep_find('0.name'), 'pikachu')

    def test_plain_dictionaries_are_still_recognised(self) -> None:
        """
        Test that the patch does not break traversal of ordinary dictionaries.

        Expected: deep_find still resolves a nested plain dict after nativify()
        """
        self._nativify_quietly()
        self.assertEqual(deep_find({'a': {'b': [{'c': 1}]}}, 'a.b.0.c'), 1)

    def test_plain_lists_are_still_recognised(self) -> None:
        """
        Test that the patch does not break traversal of ordinary lists.

        Expected: deep_find still resolves through a plain list after nativify()
        """
        self._nativify_quietly()
        self.assertEqual(deep_find({'v': [10, 20]}, 'v.1'), 20)

    def test_literals_are_left_alone(self) -> None:
        """
        Test that list and dict literals do not gain the method.

        Literals are built by dedicated bytecode that never consults builtins, so the
        docstring's original promise that they would work was impossible to keep.

        Expected: [1, 2] and {'a': 1} have no deep_find attribute
        """
        self._nativify_quietly()
        self.assertFalse(hasattr([1, 2], 'deep_find'))
        self.assertFalse(hasattr({'a': 1}, 'deep_find'))


if __name__ == '__main__':
    unittest.main()
