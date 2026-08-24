"""The never-raises contract, and how much of a lazy source a lookup consumes."""

import itertools
import pathlib
import unittest
from collections.abc import Iterator, Sequence
from typing import Any

from deepfinder import deep_find
from deepfinder.deep_find import _resolve_item


class Exploding:
    """An object whose iteration always fails."""

    def __iter__(self) -> Iterator[Any]:
        """Raise instead of yielding."""
        msg = 'iteration blew up'
        raise RuntimeError(msg)


class BrokenSequence(Sequence[Any]):
    """A sequence whose length cannot be determined."""

    def __len__(self) -> int:
        """Raise, which is the one thing a Sequence is not supposed to do."""
        msg = 'no length here'
        raise RuntimeError(msg)

    def __getitem__(self, item: Any) -> Any:
        """Never reached; present to satisfy the Sequence protocol."""
        raise NotImplementedError


def _exploding_generator() -> Iterator[int]:
    """Yield once, then fail."""
    yield 1
    msg = 'generator blew up'
    raise RuntimeError(msg)


class TestNeverRaises(unittest.TestCase):
    def test_iteration_failure(self) -> None:
        """
        Test that an __iter__ that raises yields the default.

        A closed file handle or an exhausted cursor is an ordinary thing to hand a
        generic lookup helper, and the contract says a lookup never raises.

        Expected: deep_find(Exploding(), '0', default='d') -> 'd'
        """
        self.assertEqual(deep_find(Exploding(), '0', default='d'), 'd')

    def test_generator_failing_mid_iteration(self) -> None:
        """
        Test that a generator raising part way through yields the default.

        Expected: deep_find(_exploding_generator(), '5', default='d') -> 'd'
        """
        self.assertEqual(deep_find(_exploding_generator(), '5', default='d'), 'd')

    def test_closed_file_handle(self) -> None:
        """
        Test that iterating a closed file cannot escape the lookup.

        Expected: deep_find(closed_file, '0', default='d') -> 'd'
        """
        handle = pathlib.Path(__file__).open(encoding='utf-8')  # noqa: SIM115
        handle.close()
        self.assertEqual(deep_find(handle, '0', default='d'), 'd')

    def test_broken_sequence(self) -> None:
        """
        Test that a sequence with a failing __len__ yields the default.

        Sequences are indexed in place rather than copied, so their own protocol
        methods run inside the traversal and need the outer safety net.

        Expected: deep_find(BrokenSequence(), '0', default='d') -> 'd'
        """
        self.assertEqual(deep_find(BrokenSequence(), '0', default='d'), 'd')

    def test_absurdly_deep_path(self) -> None:
        """
        Test that a path deep enough to exhaust the stack yields the default.

        Expected: a 100000-segment path -> 'd'
        """
        data: dict[str, Any] = {'a': None}
        data['a'] = data
        self.assertEqual(deep_find(data, '.'.join(['a'] * 100000), default='d'), 'd')


class TestLazyConsumption(unittest.TestCase):
    def test_infinite_iterator_is_not_drained(self) -> None:
        """
        Test that indexing an endless iterator returns instead of hanging.

        Materialising the whole iterable before parsing the index made this run
        forever; only as much as the index needs is read now.

        Expected: deep_find(itertools.count(), '3') -> 3
        """
        self.assertEqual(deep_find(itertools.count(), '3'), 3)

    def test_huge_range_is_not_materialised(self) -> None:
        """
        Test that indexing a huge range does not build it.

        Copying a range of ten billion elements exhausted memory and killed the
        process; sequences are now indexed where they stand.

        Expected: deep_find(range(10 ** 10), '3') -> 3
        """
        self.assertEqual(deep_find(range(10**10), '3'), 3)

    def test_only_the_requested_prefix_is_consumed(self) -> None:
        """
        Test that a lookup reads no further into a generator than it must.

        Expected: after resolving index 1, the generator still yields from 2
        """
        values = (i for i in range(10))
        self.assertEqual(deep_find(values, '1'), 1)
        self.assertEqual(next(values), 2)

    def test_fan_out_still_reads_everything(self) -> None:
        """
        Test that the fan-out operators do consume the whole iterable.

        Expected: deep_find((i for i in range(4)), '*') -> [0, 1, 2, 3]
        """
        self.assertEqual(deep_find((i for i in range(4)), '*'), [0, 1, 2, 3])


if __name__ == '__main__':
    unittest.main()


class IterableWithBrokenIteration:
    """An object that fails to iterate but still holds ordinary attributes."""

    def __init__(self) -> None:
        """Store an attribute that must stay reachable."""
        self.name = 'still here'

    def __iter__(self) -> Iterator[Any]:
        """Raise, standing in for a closed cursor or an exhausted stream."""
        msg = 'cannot iterate'
        raise RuntimeError(msg)


class CountingSequence(Sequence[int]):
    """A sequence that records whether anything iterated it."""

    def __init__(self, size: int) -> None:
        """Store the reported size and reset the iteration counter."""
        self.size = size
        self.iterations = 0

    def __len__(self) -> int:
        """Report the size without materialising anything."""
        return self.size

    def __getitem__(self, item: Any) -> Any:
        """Return the resolved position, normalising negatives like a real sequence."""
        return item if item >= 0 else self.size + item

    def __iter__(self) -> Iterator[int]:
        """Count the call, which a correct lookup never makes."""
        self.iterations += 1
        return iter(range(self.size))


class TestFallbacksWhenIterationFails(unittest.TestCase):
    def test_broken_iteration_does_not_hide_attributes(self) -> None:
        """
        Test that a failing __iter__ still lets attribute access through.

        The sequence branch runs first, so an object whose iteration explodes would
        otherwise lose access to its own attributes.

        Expected: deep_find(IterableWithBrokenIteration(), 'name') -> 'still here'
        """
        self.assertEqual(deep_find(IterableWithBrokenIteration(), 'name'), 'still here')

    def test_broken_iteration_falls_through_for_index_shaped_segments_too(self) -> None:
        """
        Test that the fall-through happens before the segment is read as an index.

        An object whose iteration fails is read as an object, whatever the segment
        looks like. Handing the failed materialisation on to the sequence branch
        would blow up there instead and lose the attribute.

        Expected: deep_find(obj_with_attribute_named_0, '0') -> 'attribute zero'
        """
        broken = IterableWithBrokenIteration()
        setattr(broken, '0', 'attribute zero')
        self.assertEqual(deep_find(broken, '0'), 'attribute zero')

    def test_sequences_are_indexed_without_being_iterated(self) -> None:
        """
        Test that a sequence is indexed where it stands rather than copied.

        Copying is what turned indexing a large range into an out-of-memory kill, and
        a negative index is the case that has to read the whole thing if copied.

        Expected: the sequence resolves both ends and is never iterated
        """
        sequence = CountingSequence(10**9)
        self.assertEqual(deep_find(sequence, '3'), 3)
        self.assertEqual(deep_find(sequence, '-1'), 10**9 - 1)
        self.assertEqual(sequence.iterations, 0)


class TestIndexBounds(unittest.TestCase):
    def test_out_of_range_indexes_return_a_miss_directly(self) -> None:
        """
        Test that the bounds check itself refuses out-of-range indexes.

        Checked against the private helper on purpose: at the public boundary the
        never-raises net would turn a missing bounds check into the same default, so
        only here can the check be shown to be the thing doing the work.

        Expected: _resolve_item returns None rather than raising IndexError
        """
        items = [1, 2, 3]
        self.assertIsNone(_resolve_item(items, ['3'], 0))
        self.assertIsNone(_resolve_item(items, ['-4'], 0))
        self.assertIsNone(_resolve_item([], ['0'], 0))
        self.assertIsNone(_resolve_item([], ['-1'], 0))
        self.assertEqual(_resolve_item(items, ['-3'], 0), 1)
        self.assertEqual(_resolve_item(items, ['2'], 0), 3)
