"""Container subclasses that carry :func:`deep_find` as a method."""

from __future__ import annotations

import builtins
import warnings
from typing import Any, TypeVar

from deepfinder.deep_find import deep_find

__all__ = ['DeepFinderDict', 'DeepFinderList', 'nativify']

_T = TypeVar('_T')
_K = TypeVar('_K')
_V = TypeVar('_V')


class DeepFinderList(list[_T]):
    """
    A list subclass that adds deep finding capabilities.

    Extends the built-in list with :meth:`deep_find`, inheriting every other list
    behaviour unchanged.

    Examples:
        >>> pokemons = DeepFinderList(
        ...     [
        ...         {'name': 'pikachu', 'type': 'electric'},
        ...         {'name': 'charmander', 'type': 'fire'},
        ...     ]
        ... )
        >>> pokemons.deep_find('*.name')
        ['pikachu', 'charmander']
    """

    def deep_find(
        self,
        path: str,
        path_token: str = '.',
        default: Any = None,
    ) -> Any:
        """
        Find a value in the list using dot notation.

        Args:
            path: The path to search for, e.g. ``'*.name'``.
            path_token: The separator between path segments (default: ``'.'``).
            default: Returned when the path resolves to ``None`` (default: ``None``).

        Returns:
            The found value, or ``default`` when the path resolves to ``None``.

        Examples:
            >>> DeepFinderList([{'name': 'pikachu'}]).deep_find('0.name')
            'pikachu'
        """
        return deep_find(self, path, path_token, default)


class DeepFinderDict(dict[_K, _V]):
    """
    A dictionary subclass that adds deep finding capabilities.

    Extends the built-in dict with :meth:`deep_find`, inheriting every other dict
    behaviour unchanged.

    Examples:
        >>> user = DeepFinderDict(
        ...     {
        ...         'name': 'ash',
        ...         'pokemons': [{'name': 'pikachu'}, {'name': 'charmander'}],
        ...     }
        ... )
        >>> user.deep_find('pokemons.*.name')
        ['pikachu', 'charmander']
    """

    def deep_find(
        self,
        path: str,
        path_token: str = '.',
        default: Any = None,
    ) -> Any:
        """
        Find a value in the dictionary using dot notation.

        Args:
            path: The path to search for, e.g. ``'user.profile.name'``.
            path_token: The separator between path segments (default: ``'.'``).
            default: Returned when the path resolves to ``None`` (default: ``None``).

        Returns:
            The found value, or ``default`` when the path resolves to ``None``.

        Examples:
            >>> DeepFinderDict({'name': 'ash'}).deep_find('name')
            'ash'
        """
        return deep_find(self, path, path_token, default)


def nativify() -> None:
    """
    Point ``builtins.list`` and ``builtins.dict`` at the DeepFinder subclasses.

    .. deprecated:: 1.6.0
        Rebinding builtins affects every library in the process and does not do what
        it looks like it does. Construct :class:`DeepFinderList` and
        :class:`DeepFinderDict` explicitly, or just call :func:`deep_find`.

    After this call, values built through the ``list(...)`` and ``dict(...)``
    *constructors* gain a ``deep_find`` method.

    Warning:
        List and dict **literals** are unaffected. ``[1, 2]`` and ``{'a': 1}`` are
        built by dedicated bytecode that never consults ``builtins``, so they remain
        plain containers with no ``deep_find`` method. Only the constructor calls
        change. This is a process-wide mutation that other libraries may not expect.

    Examples:
        >>> nativify()  # doctest: +SKIP
        >>> list([{'name': 'pikachu'}]).deep_find('0.name')  # doctest: +SKIP
        'pikachu'
    """
    warnings.warn(
        'nativify() is deprecated and will be removed in a future release: it mutates '
        'builtins process-wide and does not affect list/dict literals. Use '
        'DeepFinderList/DeepFinderDict or deep_find() directly.',
        DeprecationWarning,
        stacklevel=2,
    )
    builtins.list = DeepFinderList  # type: ignore[misc]
    builtins.dict = DeepFinderDict  # type: ignore[misc]
