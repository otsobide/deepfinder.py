# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0]

Backward compatible: every lookup that resolved in 1.5.1 resolves to the same value,
except where noted under Security.

### Security

- Attribute traversal no longer walks the interpreter. Dunder segments never resolve,
  and attributes are never read off modules, functions, methods, frames, tracebacks,
  code objects, generators or coroutines. Without this, a path built from user input
  could reach module globals and frame locals, for example
  `'error.tb_frame.f_globals.SECRET'` or, via any reachable module,
  `'helper.sys.modules.settings.SECRET_KEY'`. The module pivot was reachable in 1.5.1
  and earlier; the frame chains would have been introduced by the wider attribute
  support added in this release. Objects of these types are still returned as values
  when a path ends on one — only traversing *through* them is refused.

### Added

- Attribute lookups now reach `@property`, class attributes and `__slots__`, which
  the README already advertised but the implementation never supported. Methods are
  deliberately excluded unless they are stored on the instance, so a segment that
  collides with a method name (`'count'`, `'items'`, `'title'`) still yields `default`
  instead of a truthy bound method.
- Mappings that are not `dict` subclasses resolve by key: `os.environ`, `ChainMap`,
  `MappingProxyType`, `UserDict` and any third-party `Mapping`. A missing key falls
  back to the previous behaviour, so nothing that resolved before changes.
- Objects that merely happen to be iterable resolve attributes when a segment is not
  an index, which makes named tuple fields and iterable model classes reachable.
  Built-in containers are unaffected: `deep_find([1], 'append')` is still a miss.
- `DeepFinderList.deep_find` and `DeepFinderDict.deep_find` accept `path_token` and
  `default`, matching `deep_find`.
- A `py.typed` marker, so installed copies expose their type hints, and
  `DeepFinderList` / `DeepFinderDict` are generic, so element types survive.
- `__version__` and `__all__` on the package.

### Fixed

- An out-of-range *negative* index raised `IndexError` instead of returning the
  default: `deep_find([1, 2, 3], '-5')`. The bounds check only compared against
  `len`, so negative indices below `-len` escaped it.
- `nativify()` broke the library. Rebinding `builtins.dict` and `builtins.list` also
  rebound the names the traversal used for its `isinstance` checks, so plain dicts
  stopped being recognised as mappings and were walked as lists of their keys. After
  calling it, `list([{'name': 'pikachu'}]).deep_find('0.name')` returned `None`. The
  traversal now holds the real types, captured at import time.
- `path_token=''` surfaced an opaque `ValueError: empty separator` from `str.split`,
  and a non-string `path` an `AttributeError`. Both now raise with a clear message.
- `deepfinder.entity` imported `deep_find` from the package rather than the module,
  which made the import order inside `__init__.py` load-bearing: swapping its two
  lines bound the name to the module and every `.deep_find()` call raised
  `TypeError: 'module' object is not callable`.
- Exceptions raised while iterating the target escaped the lookup: a closed file
  handle, an exhausted cursor or any `__iter__` that raised propagated out instead of
  yielding `default`, contradicting the documented contract. A lookup now genuinely
  never raises; only misuse of the API itself does.
- Every iterable was fully materialised before the segment was even parsed, so
  indexing a lazy or large source was O(n) in the source rather than the lookup:
  `deep_find(range(10 ** 10), '3')` exhausted memory and `deep_find(count(), '3')`
  never returned. Sequences are now indexed where they stand, and a lazy iterable is
  read only as far as the requested index.
- An object whose `__iter__` raised lost access to its own attributes.
- Traversal no longer mutates the path list it is given, and no longer copies it per
  branch, so a fan-out over a wide sequence stops being quadratic in path length.

### Deprecated

- `nativify()` now emits a `DeprecationWarning`. It mutates the interpreter for every
  library in the process, and it never affected `list` and `dict` **literals**, which
  are built by bytecode that does not consult `builtins` — contradicting its own
  documented example. Use `DeepFinderList` / `DeepFinderDict`, or call `deep_find`.

### Changed

- Packaging moved to PEP 621 `pyproject.toml`; `setup.cfg` is gone. The build backend
  is now declared explicitly, so builds no longer fall back to setuptools'
  deprecated `__legacy__` backend.
- Every README example and docstring example is executed by the test suite.
- The test suite grew from 43 to 160 tests at 100% line and branch coverage, and the
  project is now checked with `ruff` (all rules) and `mypy --strict`.
- CI runs on Python 3.9 through 3.14, on Linux plus macOS and Windows spot checks.
  The release workflow now publishes the exact artefacts it tested, and verifies that
  the release tag matches `deepfinder.__version__`.

### Documented

Behaviour that is surprising but unchanged, now stated explicitly and covered by
tests: a stored `None` is indistinguishable from a miss and yields `default`; `*` and
`*?` always build a list, so `default` never applies to them; index parsing is
`int()`-lenient (`'01'`, `' 1 '`, `'1_0'`); strings are never indexed but `bytes` are;
generators are consumed by a lookup; keys containing the separator need a different
`path_token`.

## [1.5.1] and earlier

See the [release history](https://github.com/otsobide/deepfinder.py/releases).

[1.6.0]: https://github.com/otsobide/deepfinder.py/releases/tag/v1.6.0
