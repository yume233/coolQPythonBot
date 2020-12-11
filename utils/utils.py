import asyncio
from asyncio import get_event_loop, run_coroutine_threadsafe
from datetime import datetime
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union

import httpx
from nonebot.utils import run_sync

from .log import logger

_AnyCallable = Callable[..., Any]
_AsyncCallable = Callable[..., Awaitable]


def TimeIt(function: _AnyCallable) -> _AnyCallable:
    @wraps(function)
    async def asyncWrapper(*args, **kwargs):
        start = datetime.now()
        try:
            return await function(*args, **kwargs)
        finally:
            delta = datetime.now() - start
            logger.trace(
                f"Async function <y>{function.__name__}</y> "
                f"cost <e>{delta.seconds}s{(delta.microseconds)}ms</e>"
            )

    @wraps(function)
    def syncWrapper(*args, **kwargs):
        start = datetime.now()
        try:
            return function(*args, **kwargs)
        finally:
            delta = datetime.now() - start
            logger.trace(
                f"Sync function <y>{function.__name__}</y> "
                f"cost <e>{delta.seconds}s{(delta.microseconds)}ms</e>"
            )

    return asyncWrapper if iscoroutinefunction(function) else syncWrapper


async def batchDownload(
    urls: List[str], headers: Optional[Dict[str, Any]] = None, parallel: int = 16
) -> Dict[str, bytes]:
    async def request(client: httpx.AsyncClient, url: str, sem: asyncio.Semaphore):
        async with sem:
            logger.trace(f"Bulk Requesting <e>{url}</e>.")
            response = await client.get(url)
            response.raise_for_status()
        return url, response.content

    async with httpx.AsyncClient(headers=headers) as client:
        sem = asyncio.Semaphore(parallel)
        results: List[Union[Tuple[str, bytes], Exception]] = await asyncio.gather(
            *map(lambda url: request(client, url, sem), urls), return_exceptions=True
        )
    data = {
        url: result
        for url, result in (i for i in results if not isinstance(i, Exception))
    }
    succeed, failed = len(results), len(results) - len(data)
    logger.debug(f"Bulk download finished, succeed={succeed} failed={failed}.")
    return data


class SyncUtil:
    @staticmethod
    def ToAsync(function: _AnyCallable) -> _AsyncCallable:
        return TimeIt(run_sync(function))

    @staticmethod
    def ToSync(function: _AsyncCallable) -> _AnyCallable:
        @TimeIt
        @wraps(function)
        def wrapper(*args, **kwargs):
            return run_coroutine_threadsafe(
                function(*args, **kwargs), loop=get_event_loop()
            ).result()

        return wrapper
