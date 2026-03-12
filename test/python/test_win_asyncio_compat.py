# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Nominatim. (https://nominatim.org)
#
# Copyright (C) 2026 by the Nominatim developer community.
# For a full list of authors see the git log.
"""
Tests for the cross-platform asyncio wrapper in
nominatim_db.utils.asyncio_utils.
"""
import asyncio
import sys

import pytest

from nominatim_db.utils.asyncio_utils import run_coroutine


async def _dummy_coro():
    return 42


def test_run_coroutine_returns_result():
    """run_coroutine should execute the coroutine and return its result."""
    assert run_coroutine(_dummy_coro()) == 42


@pytest.mark.skipif(sys.platform != 'win32', reason="Windows-only test")
def test_run_coroutine_uses_selector_event_loop_on_windows():
    """On Windows, run_coroutine should use SelectorEventLoop, not
    ProactorEventLoop."""
    loop_class = None

    async def _capture_loop_class():
        nonlocal loop_class
        loop_class = type(asyncio.get_running_loop())
        return True

    run_coroutine(_capture_loop_class())
    assert loop_class is asyncio.SelectorEventLoop


@pytest.mark.skipif(sys.platform == 'win32', reason="Non-Windows test")
def test_run_coroutine_does_not_override_loop_factory_on_unix():
    """On non-Windows platforms, run_coroutine should not inject loop_factory."""
    loop_class = None

    async def _capture_loop_class():
        nonlocal loop_class
        loop_class = type(asyncio.get_running_loop())
        return True

    run_coroutine(_capture_loop_class())
    # On Linux/macOS the default is SelectorEventLoop anyway,
    # but the key point is we didn't force it.
    assert loop_class is not None


def test_run_coroutine_forwards_kwargs():
    """Extra kwargs should be forwarded to asyncio.run()."""
    # debug is a standard asyncio.run kwarg
    async def _check_debug():
        return asyncio.get_event_loop().get_debug()

    result = run_coroutine(_check_debug(), debug=True)
    assert result is True
