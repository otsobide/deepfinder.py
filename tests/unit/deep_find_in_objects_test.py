"""Attribute traversal: instance state, slots, class attributes and properties."""

import unittest
from collections.abc import Iterator
from typing import Any, NamedTuple

from deepfinder import deep_find


class Point(NamedTuple):
    """A named tuple fixture: a tuple that also has fields."""

    x: int
    y: int


class Address:
    """A leaf object used as a nested attribute."""

    def __init__(self, city: str) -> None:
        """Store the city."""
        self.city = city


class User:
    """An object exercising every attribute flavour deep_find can reach."""

    species = 'human'

    def __init__(self, name: str, address: Address) -> None:
        """Store the name and the nested address."""
        self.name = name
        self.address = address
        self._secret = 'hidden'
        self.callback: Any = None

    @property
    def display_name(self) -> str:
        """Return a computed name, proving properties are evaluated."""
        return self.name.title()

    @property
    def broken(self) -> str:
        """Raise, proving a failing property cannot escape deep_find."""
        msg = 'this property always fails'
        raise RuntimeError(msg)

    def greet(self) -> str:
        """Return a greeting; used to check that methods resolve as bound methods."""
        return f'hi {self.name}'


class Slotted:
    """An object without a __dict__, reachable only through __slots__."""

    __slots__ = ('value',)

    def __init__(self, value: str) -> None:
        """Store the single slot."""
        self.value = value


class Dynamic:
    """An object answering every attribute through __getattr__."""

    def __getattr__(self, name: str) -> str:
        """Return the attribute name back, whatever is asked for."""
        return f'dynamic:{name}'


class IterableWithAttributes:
    """An iterable object that also carries attributes."""

    def __init__(self) -> None:
        """Store an attribute that the sequence branch will shadow."""
        self.name = 'shadowed'

    def __iter__(self) -> Iterator[str]:
        """Yield two items so the object is materialised as a sequence."""
        return iter(['first', 'second'])


class TestFindInObjects(unittest.TestCase):
    def setUp(self) -> None:
        """Build a user with a nested address."""
        self.user = User('ash', Address('Pallet Town'))

    def test_instance_attribute(self) -> None:
        """
        Test that an instance attribute resolves.

        Expected: deep_find(user, 'name') -> 'ash'
        """
        self.assertEqual(deep_find(self.user, 'name'), 'ash')

    def test_nested_object_attribute(self) -> None:
        """
        Test that attribute access chains across nested objects.

        Expected: deep_find(user, 'address.city') -> 'Pallet Town'
        """
        self.assertEqual(deep_find(self.user, 'address.city'), 'Pallet Town')

    def test_property_is_evaluated(self) -> None:
        """
        Test that a property is evaluated rather than skipped.

        The traversal used to read vars(obj), which sees only the instance __dict__,
        so properties were unreachable despite being advertised as supported.

        Expected: deep_find(user, 'display_name') -> 'Ash'
        """
        self.assertEqual(deep_find(self.user, 'display_name'), 'Ash')

    def test_class_attribute(self) -> None:
        """
        Test that an attribute defined on the class resolves.

        Expected: deep_find(user, 'species') -> 'human'
        """
        self.assertEqual(deep_find(self.user, 'species'), 'human')

    def test_slots_attribute(self) -> None:
        """
        Test that a __slots__ attribute resolves on an object with no __dict__.

        Expected: deep_find(Slotted('x'), 'value') -> 'x'
        """
        self.assertEqual(deep_find(Slotted('x'), 'value'), 'x')

    def test_underscore_prefixed_attribute(self) -> None:
        """
        Test that a single-underscore attribute is still reachable.

        Expected: deep_find(user, '_secret') -> 'hidden'
        """
        self.assertEqual(deep_find(self.user, '_secret'), 'hidden')

    def test_raising_property_falls_back_to_default(self) -> None:
        """
        Test that an exception raised inside a property cannot escape deep_find.

        Expected: deep_find(user, 'broken', default='d') -> 'd'
        """
        self.assertEqual(deep_find(self.user, 'broken', default='d'), 'd')

    def test_methods_do_not_resolve(self) -> None:
        """
        Test that a method name resolves to the default, not to a bound method.

        Widening attribute access to getattr would otherwise make any segment that
        collides with a method name ('count', 'items', 'index', 'title') return a
        truthy callable and silently defeat default=. The pre-1.6 implementation read
        the instance __dict__, which never saw methods, so this keeps that result.

        Expected: deep_find(user, 'greet', default='d') -> 'd'
        """
        self.assertEqual(deep_find(self.user, 'greet', default='d'), 'd')

    def test_leaf_method_names_do_not_resolve(self) -> None:
        """
        Test that the same holds for methods of built-in leaf values.

        Expected: deep_find({'a': 'hello'}, 'a.title', default='d') -> 'd'
        """
        self.assertEqual(deep_find({'a': 'hello'}, 'a.title', default='d'), 'd')
        self.assertEqual(deep_find({'n': 5}, 'n.bit_length', default='d'), 'd')

    def test_callables_stored_on_the_instance_do_resolve(self) -> None:
        """
        Test that a callable held as instance state is still a value.

        This is the escape hatch the guard needs: the instance __dict__ did return
        callables before 1.6, so dropping every callable would itself break lookups.

        Expected: deep_find(user, 'callback')() -> 'called'
        """
        self.user.callback = lambda: 'called'
        callback = deep_find(self.user, 'callback')
        self.assertTrue(callable(callback))
        self.assertEqual(callback(), 'called')

    def test_dynamic_attribute(self) -> None:
        """
        Test that __getattr__ is honoured.

        Expected: deep_find(Dynamic(), 'anything') -> 'dynamic:anything'
        """
        self.assertEqual(deep_find(Dynamic(), 'anything'), 'dynamic:anything')

    def test_missing_attribute(self) -> None:
        """
        Test that a missing attribute resolves to None.

        Expected: deep_find(user, 'nope') -> None
        """
        self.assertIsNone(deep_find(self.user, 'nope'))

    def test_dunder_segments_are_refused(self) -> None:
        """
        Test that dunder segments never resolve.

        A path is often built from user input. Allowing dunders would turn deep_find
        into an introspection gadget: '__class__', '__globals__' and '__subclasses__'
        chain straight into module state and builtins.

        Expected: '__class__', '__dict__', '__init__' and '__module__' all -> None
        """
        for segment in ('__class__', '__dict__', '__init__', '__module__'):
            with self.subTest(segment=segment):
                self.assertIsNone(deep_find(self.user, segment))

    def test_dunder_refusal_blocks_the_globals_chain(self) -> None:
        """
        Test that the classic escape chain is cut at its first link.

        Expected: deep_find(user, 'greet.__globals__') -> None
        """
        self.assertIsNone(deep_find(self.user, 'greet.__globals__'))

    def test_sequence_branch_wins_but_attributes_remain_reachable(self) -> None:
        """
        Test that an iterable object is indexed first and read as an object second.

        Dispatch order is part of the public semantics: the sequence branch runs
        first, so an index resolves against the items. A segment that is not an index
        then falls back to attribute access, which is what makes named tuples and
        iterable model classes usable.

        Expected: deep_find(IterableWithAttributes(), '0')    -> 'first'
                  deep_find(IterableWithAttributes(), 'name') -> 'shadowed'
        """
        self.assertEqual(deep_find(IterableWithAttributes(), '0'), 'first')
        self.assertEqual(deep_find(IterableWithAttributes(), 'name'), 'shadowed')

    def test_builtin_containers_do_not_expose_their_methods(self) -> None:
        """
        Test that the attribute fallback does not apply to built-in containers.

        A built-in container is pure data, so a non-index segment stays a miss rather
        than handing back a bound method the caller never asked for.

        Expected: deep_find([1, 2], 'append') -> None
        """
        self.assertIsNone(deep_find([1, 2], 'append'))
        self.assertIsNone(deep_find((1, 2), 'count'))
        self.assertIsNone(deep_find({1, 2}, 'union'))

    def test_named_tuple_fields(self) -> None:
        """
        Test that named tuple fields resolve by name as well as by index.

        A named tuple is a tuple, so it used to be materialised as a sequence and its
        field names never resolved.

        Expected: deep_find(Point(1, 2), 'y') -> 2
        """
        point = Point(1, 2)
        self.assertEqual(deep_find(point, 'y'), 2)
        self.assertEqual(deep_find(point, '0'), 1)
        self.assertEqual(deep_find({'p': [point]}, 'p.*.x'), [1])

    def test_data_attributes_on_a_primitive(self) -> None:
        """
        Test that a primitive's data attributes are still ordinary attributes.

        Only methods are refused, so a data attribute such as int.real resolves.

        Expected: deep_find({'n': 3}, 'n.real') -> 3
        """
        self.assertEqual(deep_find({'n': 3}, 'n.real'), 3)

    def test_object_reached_through_a_container(self) -> None:
        """
        Test that objects nested inside containers are traversed.

        Expected: deep_find({'users': [user]}, 'users.0.address.city') -> 'Pallet Town'
        """
        data: dict[str, Any] = {'users': [self.user]}
        self.assertEqual(deep_find(data, 'users.0.address.city'), 'Pallet Town')

    def test_wildcard_over_objects(self) -> None:
        """
        Test that a fan-out operator works over a sequence of objects.

        Expected: deep_find({'users': [user, user]}, 'users.*.name') -> ['ash', 'ash']
        """
        data: dict[str, Any] = {'users': [self.user, self.user]}
        self.assertEqual(deep_find(data, 'users.*.name'), ['ash', 'ash'])


if __name__ == '__main__':
    unittest.main()
