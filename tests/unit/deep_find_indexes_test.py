"""Integer indexing into sequences, including the out-of-range regressions."""

import unittest

from deepfinder import deep_find


class TestIndexes(unittest.TestCase):
    def test_negative_index_counts_from_the_end(self) -> None:
        """
        Test that a negative index reads from the end of the sequence.

        Expected: deep_find([1, 2, 3], '-1') -> 3
        """
        self.assertEqual(deep_find([1, 2, 3], '-1'), 3)

    def test_most_negative_valid_index(self) -> None:
        """
        Test that the lowest in-range negative index resolves to the first item.

        Expected: deep_find([1, 2, 3], '-3') -> 1
        """
        self.assertEqual(deep_find([1, 2, 3], '-3'), 1)

    def test_negative_index_out_of_range_does_not_raise(self) -> None:
        """
        Test that an out-of-range negative index resolves to None instead of raising.

        Regression: the bounds check only compared against len(items), so a negative
        index below -len(items) escaped it and let IndexError propagate out of
        deep_find, breaking the "a lookup never raises" contract.

        Expected: deep_find([1, 2, 3], '-5') -> None
        """
        self.assertIsNone(deep_find([1, 2, 3], '-5'))

    def test_negative_index_out_of_range_takes_the_default(self) -> None:
        """
        Test that an out-of-range negative index falls back to the default.

        Expected: deep_find([1, 2, 3], '-5', default='d') -> 'd'
        """
        self.assertEqual(deep_find([1, 2, 3], '-5', default='d'), 'd')

    def test_nested_negative_index_out_of_range(self) -> None:
        """
        Test that the same regression is fixed below the top level.

        Expected: deep_find({'v': [1, 2]}, 'v.-9') -> None
        """
        self.assertIsNone(deep_find({'v': [1, 2]}, 'v.-9'))

    def test_negative_index_out_of_range_on_a_set(self) -> None:
        """
        Test that a materialised set is bounds-checked like a list.

        Expected: deep_find({1, 2, 3}, '-5') -> None
        """
        self.assertIsNone(deep_find({1, 2, 3}, '-5'))

    def test_positive_index_out_of_range(self) -> None:
        """
        Test that an index past the end resolves to None.

        Expected: deep_find([1, 2, 3], '3') -> None
        """
        self.assertIsNone(deep_find([1, 2, 3], '3'))

    def test_index_on_empty_sequence(self) -> None:
        """
        Test that any index into an empty sequence resolves to None.

        Expected: deep_find([], '0') -> None
        """
        self.assertIsNone(deep_find([], '0'))

    def test_non_numeric_index(self) -> None:
        """
        Test that a non-numeric segment against a sequence resolves to None.

        Expected: deep_find(['a', 'b'], 'x') -> None
        """
        self.assertIsNone(deep_find(['a', 'b'], 'x'))

    def test_float_like_index(self) -> None:
        """
        Test that a float-looking segment is not accepted as an index.

        Expected: deep_find([1, 2, 3], '1.5') -> None
        """
        self.assertIsNone(deep_find([1, 2, 3], '1.5'))

    def test_empty_segment_against_a_sequence(self) -> None:
        """
        Test that an empty segment against a sequence resolves to None.

        Expected: deep_find({'v': [1, 2]}, 'v.') -> None
        """
        self.assertIsNone(deep_find({'v': [1, 2]}, 'v.'))

    def test_lenient_index_parsing_is_preserved(self) -> None:
        """
        Test that int()'s leniency is part of the accepted behaviour.

        Indexes go through int(), which tolerates surrounding whitespace, a leading
        sign, redundant zeros and PEP 515 underscores. This is documented rather than
        tightened, because tightening it would change results that resolve today.

        Expected: '01', ' 1 ', '+1' and '1_0' all resolve as integers
        """
        items = list(range(20))
        self.assertEqual(deep_find(items, '01'), 1)
        self.assertEqual(deep_find(items, ' 1 '), 1)
        self.assertEqual(deep_find(items, '+1'), 1)
        self.assertEqual(deep_find(items, '1_0'), 10)


if __name__ == '__main__':
    unittest.main()
