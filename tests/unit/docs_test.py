"""Executable documentation: every docstring and README example is run."""

from __future__ import annotations

import doctest
import importlib
import pathlib
import unittest

# deepfinder.deep_find the *name* is the function; doctest needs the module object.
deep_find_module = importlib.import_module('deepfinder.deep_find')
entity_module = importlib.import_module('deepfinder.entity')

README = pathlib.Path(__file__).resolve().parents[2] / 'README.md'
OPTIONS = doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL


def load_tests(
    loader: unittest.TestLoader,  # noqa: ARG001
    tests: unittest.TestSuite,
    ignore: str | None = None,  # noqa: ARG001
) -> unittest.TestSuite:
    """
    Register the doctests of the package and of the README with the suite.

    Args:
        loader: Supplied by unittest; unused.
        tests: The suite collected so far.
        ignore: Supplied by unittest; unused.

    Returns:
        The suite with every doctest appended.
    """
    tests.addTests(doctest.DocTestSuite(deep_find_module, optionflags=OPTIONS))
    tests.addTests(doctest.DocTestSuite(entity_module, optionflags=OPTIONS))
    tests.addTests(
        doctest.DocFileSuite(
            str(README),
            module_relative=False,
            optionflags=OPTIONS,
        ),
    )
    return tests


class TestDocumentationIsPresent(unittest.TestCase):
    def test_readme_exists(self) -> None:
        """
        Test that the README the doctests read is actually there.

        Without this, a missing README would silently register zero doctests instead
        of failing.

        Expected: README.md exists and mentions deep_find
        """
        self.assertTrue(README.is_file())
        self.assertIn('deep_find', README.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
