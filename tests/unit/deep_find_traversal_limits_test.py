"""Refusals that keep a user-supplied path from reading interpreter state."""

import sys
import types
import unittest

from deepfinder import deep_find

SECRET = 'module-level-secret'


class Holder:
    """A plain object used to hand deep_find a runtime object as data."""

    def __init__(self) -> None:
        """Start with nothing attached."""
        self.payload: object = None


def _raise() -> None:
    """Raise so the caller can capture a real traceback with locals in it."""
    credentials = 'credentials-in-frame-locals'
    msg = f'boom ({len(credentials)} chars hidden)'
    raise ValueError(msg)


class TestTraversalLimits(unittest.TestCase):
    def test_traceback_cannot_reach_frame_globals(self) -> None:
        """
        Test that a stored traceback is not a door into module globals.

        Applications routinely attach a traceback to an error record. Reading
        tb_frame would hand a user-supplied path every global of the raising module.

        Expected: deep_find(holder, 'payload.tb_frame.f_globals.SECRET') -> None
        """
        holder = Holder()
        try:
            _raise()
        except ValueError as error:
            holder.payload = error.__traceback__

        self.assertIsNone(deep_find(holder, 'payload.tb_frame.f_globals.SECRET'))

    def test_traceback_cannot_reach_frame_locals(self) -> None:
        """
        Test that walking tb_next does not expose local variables either.

        Expected: deep_find(holder, 'payload.tb_next.tb_frame.f_locals.credentials') -> None
        """
        holder = Holder()
        try:
            _raise()
        except ValueError as error:
            holder.payload = error.__traceback__

        path = 'payload.tb_next.tb_frame.f_locals.credentials'
        self.assertIsNone(deep_find(holder, path))

    def test_coroutine_cannot_reach_frame_globals(self) -> None:
        """
        Test that a pending coroutine does not expose its frame.

        Expected: deep_find(holder, 'payload.cr_frame.f_globals.SECRET') -> None
        """

        async def pending() -> None:
            """Never awaited; only used for its cr_frame."""

        holder = Holder()
        coroutine = pending()
        try:
            self.assertIsNone(deep_find(holder, 'payload.cr_frame.f_globals.SECRET'))
            holder.payload = coroutine
            self.assertIsNone(deep_find(holder, 'payload.cr_frame.f_globals.SECRET'))
        finally:
            coroutine.close()

    def test_module_cannot_be_traversed(self) -> None:
        """
        Test that a module attribute is a dead end rather than a pivot.

        This one is not a regression but a pre-existing hole: v1.5.1 read modules
        through vars(), so any reachable module let a path walk sys.modules into every
        other loaded module's globals.

        Expected: deep_find(holder, 'payload.sys.modules.deepfinder.__name__') -> None
        """
        helper = types.ModuleType('helper')
        helper.sys = sys  # type: ignore[attr-defined]
        holder = Holder()
        holder.payload = helper

        self.assertIsNone(deep_find(holder, 'payload.sys.modules.deepfinder'))

    def test_frame_cannot_be_traversed(self) -> None:
        """
        Test that a frame handed over directly is still refused.

        Expected: deep_find(holder, 'payload.f_globals.SECRET') -> None
        """
        holder = Holder()
        holder.payload = sys._getframe()

        self.assertIsNone(deep_find(holder, 'payload.f_globals.SECRET'))

    def test_function_cannot_be_traversed(self) -> None:
        """
        Test that a function is returned as a value but never walked into.

        Expected: deep_find(holder, 'payload') is the function, but
                  deep_find(holder, 'payload.__globals__.SECRET') -> None
        """
        holder = Holder()
        holder.payload = _raise

        self.assertIs(deep_find(holder, 'payload'), _raise)
        self.assertIsNone(deep_find(holder, 'payload.__globals__.SECRET'))

    def test_classic_dunder_chain(self) -> None:
        """
        Test that the textbook __class__/__globals__ chain resolves to nothing.

        Expected: deep_find(holder, '__class__.__init__.__globals__.SECRET') -> None
        """
        self.assertIsNone(deep_find(Holder(), '__class__.__init__.__globals__.SECRET'))

    def test_ordinary_data_is_unaffected(self) -> None:
        """
        Test that the refusals do not get in the way of ordinary lookups.

        Expected: a normal nested lookup still resolves
        """
        holder = Holder()
        holder.payload = {'users': [{'name': 'ash'}]}
        self.assertEqual(deep_find(holder, 'payload.users.0.name'), 'ash')


if __name__ == '__main__':
    unittest.main()
