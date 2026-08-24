"""Dot-notation lookups into nested dictionaries, sequences and objects."""

from __future__ import annotations

import inspect
import types
from collections.abc import Iterable, Mapping, Sequence
from itertools import islice
from typing import Any, Final

__all__ = ['deep_find']

#: Captured at import time so that :func:`deepfinder.entity.nativify`, which rebinds
#: ``builtins.dict`` and ``builtins.list``, cannot make the ``isinstance`` checks below
#: start testing against the ``DeepFinder*`` subclasses and stop recognising plain
#: dicts and lists.
_DICT: Final = dict
_LIST: Final = list

#: Return every item of the sequence.
_ALL: Final = '*'
#: Return the first item that resolves to a non-``None`` value.
_FIRST: Final = '?'
#: Return every item that resolves to a non-``None`` value. Both spellings are accepted.
_ALL_NOT_NONE: Final = frozenset({'*?', '?*'})

#: Distinguishes "no such key" from "the key holds None".
_MISS: Final = object()

#: Types whose attributes expose the interpreter rather than the caller's data.
#: Reading attributes off these is refused so that a user-supplied path cannot walk
#: from a stored traceback, coroutine or module into frame locals, module globals and
#: the rest of the introspection graph. Holding one as a *result* is still fine; only
#: traversing *through* one is refused.
_OPAQUE: Final = (
    types.ModuleType,
    types.FrameType,
    types.TracebackType,
    types.CodeType,
    types.FunctionType,
    types.MethodType,
    types.BuiltinFunctionType,
    types.MethodWrapperType,
    types.WrapperDescriptorType,
    types.MethodDescriptorType,
    types.GetSetDescriptorType,
    types.MemberDescriptorType,
    types.GeneratorType,
    types.CoroutineType,
    types.AsyncGeneratorType,
)


def deep_find(
    obj: Any,
    path: str,
    path_token: str = '.',
    default: Any = None,
) -> Any:
    """
    Find a value in a nested structure using a dot-notation path.

    Traverses dictionaries, mappings, sequences and objects following ``path``. A
    lookup never raises: anything that cannot be resolved yields ``default``.

    Args:
        obj: The object to search in. Dictionaries, any mapping, any non-string
            iterable (lists, tuples, sets, frozen sets, generators) and objects with
            attributes are all supported.
        path: The path to the desired value, e.g. ``'users.0.name'``. An empty
            path returns ``obj`` itself.
        path_token: The separator between path segments (default: ``'.'``).
        default: Returned when the path resolves to ``None`` (default: ``None``).

    Returns:
        The found value, or ``default`` when the path resolves to ``None``.

    Raises:
        TypeError: If ``path`` is not a string.
        ValueError: If ``path_token`` is empty.

    Note:
        ``default`` is substituted whenever the result *is* ``None``, so a key whose
        stored value is genuinely ``None`` also yields ``default``. The ``'*'`` and
        ``'*?'`` operators always build a list, which is never ``None``, so
        ``default`` never applies to them.

    Examples:
        >>> data = {'users': [{'name': 'John'}, {'name': 'Jane'}]}
        >>> deep_find(data, 'users.0.name')
        'John'
        >>> deep_find(data, 'users.*.name')
        ['John', 'Jane']
        >>> deep_find(data, 'users.0.email', default='none@example.com')
        'none@example.com'
    """
    if not isinstance(path, str):
        # Unreachable for a type-checked caller, which is the point: untyped callers
        # get a clear TypeError instead of an AttributeError from str.split.
        msg = f'path must be a str, got {type(path).__name__}'  # type: ignore[unreachable]
        raise TypeError(msg)
    if not path_token:
        msg = 'path_token must not be empty'
        raise ValueError(msg)

    segments = path.split(path_token)
    if segments == ['']:
        segments = []

    try:
        result = _resolve(obj, segments, 0)
    except Exception:  # noqa: BLE001 - the contract is that a lookup never raises
        return default

    if result is not None:
        return result

    return default


def _resolve(obj: Any, segments: Sequence[str], index: int) -> Any:
    """
    Resolve ``segments[index:]`` against ``obj``.

    Dispatch order is part of the public semantics: mappings first, then sequences,
    then attributes. ``index`` is carried instead of consuming the segment list so
    that the fan-out branches need no copies.

    Args:
        obj: The current object being traversed.
        segments: Every segment of the original path.
        index: Position of the segment to resolve; ``len(segments)`` means "done".

    Returns:
        The found value, or ``None`` if this segment cannot be resolved.
    """
    if index >= len(segments):
        return obj

    if isinstance(obj, _DICT):
        return _resolve(obj.get(segments[index]), segments, index + 1)

    if isinstance(obj, Mapping):
        resolved = _resolve_key(obj, segments, index)
        if resolved is not _MISS:
            return resolved

    if isinstance(obj, Iterable) and not isinstance(obj, str):
        items = _materialise(obj, segments[index])
        if items is not _MISS:
            resolved = _resolve_item(items, segments, index)
            if resolved is not None:
                return resolved
        # A segment that is not an index still gets a chance as an attribute, which
        # is what makes named tuple fields and iterable model classes reachable, and
        # what keeps a broken __iter__ from hiding the object's own attributes.

    return _resolve_attribute(obj, segments, index)


def _resolve_key(obj: Mapping[Any, Any], segments: Sequence[str], index: int) -> Any:
    """
    Resolve one segment as a key of a mapping that is not a ``dict`` subclass.

    Covers ``os.environ``, ``ChainMap``, ``MappingProxyType``, ``UserDict`` and any
    third-party ``Mapping``, which used to be walked as a plain list of their keys.

    Args:
        obj: The mapping to read the key from.
        segments: Every segment of the original path.
        index: Position of the segment to resolve.

    Returns:
        The resolved value, or :data:`_MISS` when the key is absent, so that the
        caller can fall back to the sequence branch and keep older lookups working.
    """
    try:
        value = obj[segments[index]]
    except Exception:  # noqa: BLE001 - third-party mappings raise anything; a lookup must never raise
        return _MISS

    return _resolve(value, segments, index + 1)


def _materialise(obj: Iterable[Any], segment: str) -> Any:
    """
    Turn an iterable into something indexable, reading no more of it than needed.

    Sequences are used as they are, so indexing ``range(10 ** 10)`` stays O(1) instead
    of building ten billion elements. A lazy iterable is drained only up to the
    requested position, so ``deep_find(itertools.count(), '3')`` returns instead of
    hanging. The fan-out operators and negative indices still need every item.

    Args:
        obj: The iterable being traversed.
        segment: The segment about to be resolved against it.

    Returns:
        A sequence to index into, or :data:`_MISS` if iterating raised.
    """
    if isinstance(obj, Sequence):
        return obj

    position = _as_index(segment)

    try:
        if position is not None and position >= 0:
            return _LIST(islice(obj, position + 1))
        return _LIST(obj)
    except Exception:  # noqa: BLE001 - __iter__ runs arbitrary code; a lookup must never raise
        return _MISS


def _as_index(segment: str) -> int | None:
    """
    Parse a segment as a sequence index.

    Parsing goes through ``int()``, which tolerates surrounding whitespace, a leading
    sign, redundant zeros and PEP 515 underscores. That leniency is long-standing
    behaviour, so it is kept and documented rather than tightened.

    Args:
        segment: The path segment to parse.

    Returns:
        The index, or ``None`` if the segment is not an integer.
    """
    try:
        return int(segment)
    except ValueError:
        return None


def _resolve_item(items: Sequence[Any], segments: Sequence[str], index: int) -> Any:
    """
    Resolve one segment against a sequence.

    Handles the fan-out operators and integer indexing:

    - ``'*'``: resolve the remaining path against every item.
    - ``'?'``: resolve against each item, returning the first non-``None`` result.
    - ``'*?'`` (or ``'?*'``): like ``'*'``, with ``None`` results dropped.
    - anything else: parsed as an index, negative values included.

    Args:
        items: The sequence to index into.
        segments: Every segment of the original path.
        index: Position of the segment to resolve.

    Returns:
        The found value(s), or ``None`` if this segment cannot be resolved.

    Examples:
        >>> _resolve_item([{'name': 'John'}, {'name': 'Jane'}], ['*', 'name'], 0)
        ['John', 'Jane']
        >>> _resolve_item([{'name': 'John'}, {'name': 'Jane'}], ['?', 'age'], 0)
    """
    segment = segments[index]
    remaining = index + 1

    if segment == _ALL:
        return [_resolve(item, segments, remaining) for item in items]

    if segment in _ALL_NOT_NONE:
        found = (_resolve(item, segments, remaining) for item in items)
        return [result for result in found if result is not None]

    if segment == _FIRST:
        for item in items:
            result = _resolve(item, segments, remaining)
            if result is not None:
                return result
        return None

    position = _as_index(segment)

    if position is None or not -len(items) <= position < len(items):
        return None

    return _resolve(items[position], segments, remaining)


def _resolve_attribute(obj: Any, segments: Sequence[str], index: int) -> Any:
    """
    Resolve one segment as an attribute of ``obj``.

    Reaches instance attributes, ``__slots__`` entries, class attributes and
    properties. Three refusals keep it honest:

    - Dunder segments never resolve.
    - Attributes are never read off the interpreter's own runtime objects
      (see :data:`_OPAQUE`), which closes the ``traceback -> frame -> f_globals`` and
      ``module -> sys.modules`` chains a user-supplied path could otherwise walk.
    - Methods do not resolve unless they are stored on the instance itself, so that a
      segment like ``'count'`` or ``'items'`` yields ``default`` rather than a bound
      method that happens to be truthy.

    Args:
        obj: The object to read the attribute from.
        segments: Every segment of the original path.
        index: Position of the segment to resolve.

    Returns:
        The found value, or ``None`` if the attribute is missing, refused, or raises.
    """
    segment = segments[index]

    if isinstance(obj, _OPAQUE):
        return None

    if segment.startswith('__') and segment.endswith('__'):
        return None

    try:
        attribute = getattr(obj, segment)
    except Exception:  # noqa: BLE001 - properties run arbitrary code; a lookup must never raise
        return None

    if inspect.isroutine(attribute) and segment not in getattr(obj, '__dict__', ()):
        return None

    return _resolve(attribute, segments, index + 1)
