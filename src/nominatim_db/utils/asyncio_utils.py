# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Nominatim. (https://nominatim.org)
#
# Copyright (C) 2026 by the Nominatim developer community.
# For a full list of authors see the git log.
"""
Cross-platform asyncio helpers.

Provides two complementary mechanisms for Windows compatibility:

* :func:`run_coroutine` – uses the ``loop_factory`` parameter of
  :func:`asyncio.run` (Python 3.12+) so that each *individual* call
  uses ``SelectorEventLoop``.

* :func:`ensure_compatible_loop_policy` – sets the **global** event-loop
  policy so that third-party libraries (psycopg async, SQLAlchemy async,
  pytest-asyncio …) that create their own loops also get a compatible one.
  This is the right choice for process-wide configuration such as
  ``conftest.py``.
"""
import asyncio
import sys
import warnings
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


def ensure_compatible_loop_policy() -> None:
    """Set the global event-loop policy to use *SelectorEventLoop* on Windows.

    This must be called early (e.g. at module level in ``conftest.py``)
    so that **all** async code in the process — including third-party
    libraries that create their own event loops — uses a compatible loop.

    Version handling:

    * Python 3.8 – 3.13: ``set_event_loop_policy`` works without warnings.
    * Python 3.14 – 3.15: deprecated but functional; the deprecation
      warning is suppressed.
    * Python 3.16+: the policy API is removed.  This function is a no-op;
      callers should rely on :func:`run_coroutine` (``loop_factory``)
      instead.
    """
    if sys.platform != 'win32':
        return

    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy()
            )
