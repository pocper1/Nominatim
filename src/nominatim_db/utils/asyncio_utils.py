# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Nominatim. (https://nominatim.org)
#
# Copyright (C) 2026 by the Nominatim developer community.
# For a full list of authors see the git log.
"""
Cross-platform asyncio helper.

The implementation avoids the deprecated ``set_event_loop_policy`` API
(removed in Python 3.16) and instead uses the ``loop_factory`` parameter
that was added to :func:`asyncio.run` in Python 3.12.
"""
import asyncio
import sys
from typing import Any, TypeVar, Coroutine

T = TypeVar('T')


def run_coroutine(coro: Coroutine[Any, Any, T], **kwargs: Any) -> T:
    """Run *coro* with a platform-appropriate event loop.

    On Windows the *SelectorEventLoop* is used so that psycopg's async
    connections work correctly.  On other platforms this is a plain
    :func:`asyncio.run` call.

    Any extra *kwargs* are forwarded to :func:`asyncio.run`.
    """
    if sys.platform == 'win32':
        kwargs.setdefault('loop_factory', asyncio.SelectorEventLoop)
    return asyncio.run(coro, **kwargs)
