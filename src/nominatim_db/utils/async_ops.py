import sys
import asyncio
from typing import Coroutine, Any, TypeVar

T = TypeVar('T')

def run_legacy_asyncio(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run an async coroutine with appropriate event loop for the platform.
    
    Due to asyncio in windows not supporting, we need to use WindowsSelectorEventLoopPolicy.

    loop_factory is for python 3.12+.
    """
    if sys.platform == 'win32':
        if sys.version_info >= (3, 12):
            return asyncio.run(coro, loop_factory=asyncio.WindowsSelectorEventLoopPolicy().new_event_loop)
        else:
            old_policy = asyncio.get_event_loop_policy()
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            try:
                return asyncio.run(coro)
            finally:
                asyncio.set_event_loop_policy(old_policy)
    
    return asyncio.run(coro)
