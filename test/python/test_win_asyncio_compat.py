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

import pytest

from conftest import apply_win_asyncio_compat


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
    apply_win_asyncio_compat()

    # asyncio.run should have been replaced by our wrapper
    assert asyncio.run is not original_run

    # The wrapped version should still work correctly
    async def dummy():
        return 42

    result = asyncio.run(dummy())
    assert result == 42
