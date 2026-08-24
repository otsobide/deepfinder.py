# Contributing

Thanks for helping out. This is a small, dependency-free library, and the bar for
changes is mostly about keeping it that way.

## Getting set up

```bash
git clone https://github.com/otsobide/deepfinder.py
cd deepfinder.py
python -m venv .venv && source .venv/bin/activate
make install
```

`make help` lists every target. Before opening a pull request:

```bash
make check   # lint, format check, mypy --strict, tests, coverage
```

## Ground rules

- **The runtime stays dependency-free.** Everything in `[project.optional-dependencies].dev`
  is for development only; nothing may be imported by `deepfinder/`.
- **Coverage stays at 100%**, lines and branches. `make coverage` fails below that.
- **A lookup never raises.** Anything that cannot be resolved returns `default`.
  Misuse of the API itself (a non-string `path`, an empty `path_token`) does raise,
  with a message that says what is wrong.
- **Backward compatibility.** A path that resolves today must keep resolving to the
  same value. New capability is welcome; changing an existing result needs a major
  version and an entry in `CHANGELOG.md`.
- **`deep_find` walks data, not the interpreter.** If you touch `_resolve_attribute`,
  keep the dunder and `_OPAQUE` refusals intact and add a test in
  `tests/unit/deep_find_traversal_limits_test.py`.

## Tests

The suite is stdlib `unittest`, discovered by the `*_test.py` suffix — a file named
`test_*.py` is silently ignored. One `TestCase` per file, grouped by the behaviour
under test.

```bash
make test
python -m unittest tests.unit.deep_find_in_lists_test
python -m unittest tests.unit.deep_find_in_lists_test.TestFindInLists.test_all_values_of_list
```

Every test carries a docstring ending in an `Expected: <call> -> <result>` line.
These read as the specification for the edge cases, so please keep the convention.

Examples in `README.md` and in docstrings are executed by `tests/unit/docs_test.py`.
If you change documented behaviour, the docs fail before the code does.

For a bug fix, add the test that fails before your change and passes after it, and
say so in the pull request.

## Releasing

1. Bump `__version__` in `deepfinder/__init__.py` — the build reads it from there.
2. Add the release section to `CHANGELOG.md`.
3. Publish a GitHub Release tagged `vX.Y.Z`. The workflow checks that the tag matches
   `__version__`, runs `make check`, builds, and publishes those exact artefacts to
   PyPI through trusted publishing.
