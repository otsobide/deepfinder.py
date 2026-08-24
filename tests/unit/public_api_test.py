"""The package's public surface and distribution metadata."""

import pathlib
import unittest

import deepfinder
from deepfinder import entity


class TestPublicApi(unittest.TestCase):
    def test_exported_names(self) -> None:
        """
        Test that the documented names are exported and importable.

        Expected: deepfinder.__all__ == ['DeepFinderDict', 'DeepFinderList', 'deep_find']
        """
        self.assertEqual(
            deepfinder.__all__,
            ['DeepFinderDict', 'DeepFinderList', 'deep_find'],
        )
        for name in deepfinder.__all__:
            with self.subTest(name=name):
                self.assertTrue(hasattr(deepfinder, name))

    def test_deprecated_helper_is_not_promoted(self) -> None:
        """
        Test that nativify stays in deepfinder.entity and is not re-exported.

        Expected: 'nativify' not in deepfinder.__all__, but present on the submodule
        """
        self.assertNotIn('nativify', deepfinder.__all__)
        self.assertIn('nativify', entity.__all__)

    def test_version_is_declared(self) -> None:
        """
        Test that __version__ exists and is a dotted string.

        The build reads this attribute for the distribution version, so it has to
        stay a plain literal.

        Expected: deepfinder.__version__ looks like 'X.Y.Z'
        """
        parts = deepfinder.__version__.split('.')
        self.assertEqual(len(parts), 3)
        for part in parts:
            with self.subTest(part=part):
                self.assertTrue(part.isdigit())

    def test_typing_marker_is_shipped(self) -> None:
        """
        Test that the py.typed marker sits inside the package.

        Without it, type checkers ignore the annotations in installed copies.

        Expected: deepfinder/py.typed exists
        """
        marker = pathlib.Path(deepfinder.__file__).parent / 'py.typed'
        self.assertTrue(marker.is_file())

    def test_deep_find_is_the_function_not_the_module(self) -> None:
        """
        Test that the package exports the function, shadowing the submodule name.

        deepfinder.entity imports deep_find from deepfinder.deep_find directly, so
        the order of imports in __init__ can no longer decide whether the name binds
        to the function or to the module.

        Expected: deepfinder.deep_find is callable
        """
        self.assertTrue(callable(deepfinder.deep_find))


if __name__ == '__main__':
    unittest.main()
