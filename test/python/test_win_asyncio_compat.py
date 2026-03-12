# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Nominatim. (https://nominatim.org)
#
# Copyright (C) 2026 by the Nominatim developer community.
# For a full list of authors see the git log.
"""
Tests for the Windows asyncio compatibility shim in conftest.py.
"""
import asyncio
import sys
import warnings

import pytest


def _apply_win_asyncio_compat():
    """Re-implementation of the compatibility logic from conftest.py."""
    if sys.platform == 'win32':
        if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                asyncio.set_event_loop_policy(
                    asyncio.WindowsSelectorEventLoopPolicy()
                )
        elif hasattr(asyncio, 'SelectorEventLoop'):
            _original_asyncio_run = asyncio.run

            def _win_asyncio_run(main, **kwargs):
                kwargs.setdefault('loop_factory', asyncio.SelectorEventLoop)
                return _original_asyncio_run(main, **kwargs)

            asyncio.run = _win_asyncio_run


@pytest.mark.skipif(sys.platform != 'win32', reason="Windows-only test")
def test_elif_branch_wraps_asyncio_run(monkeypatch):
    """Simulate Python 3.16+: no WindowsSelectorEventLoopPolicy,
       but SelectorEventLoop still exists.
       The elif branch should monkeypatch asyncio.run.
    """
    original_run = asyncio.run

    # Remove WindowsSelectorEventLoopPolicy to simulate Python 3.16+
    monkeypatch.delattr(asyncio, 'WindowsSelectorEventLoopPolicy')
    monkeypatch.setattr(asyncio, 'run', original_run)

    # Re-run the compatibility logic — should now take the elif path
    _apply_win_asyncio_compat()

    # asyncio.run should have been replaced by our wrapper
    assert asyncio.run is not original_run

    # The wrapped version should still work correctly
    async def dummy():
        return 42

    result = asyncio.run(dummy())
    assert result == 42
