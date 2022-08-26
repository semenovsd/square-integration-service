import asyncio
import logging
import time
from contextlib import suppress
from functools import wraps
from typing import Any, Callable, Iterable, Type, Union

from async_timeout import timeout
from loguru import logger


class RetryError(RuntimeError):
    pass


def async_retry(
        exceptions_to_check: Union[Type[Exception], Iterable[Type[Exception]]],
        tries: int = 2,
        tries_interval: float = 2,
        increase_interval: float = 0,
        show_logs: bool = False,
        _logger: Union[Callable, Type[logging.Logger]] = print,
        raise_exception: bool = False,
        total_timeout: float | int | None = None,
) -> Any | None:
    """Retry calling the decorated function with timeout.

    For e.g:
    @retry((ConnectionError, OSError),
            tries=3,
            tries_interval=5,
            total_timeout=15,
            show_logs=True,
            _logger=logger.debug)
    async def func(*args, **kwargs):
        do something ...
    """

    def deco_retry(func: Callable) -> Any | None:
        @wraps(func)
        async def func_retry(*args, **kwargs) -> Any | None:
            mtries, mdelay = tries, tries_interval
            for r in range(1, mtries + 1):
                try:
                    if total_timeout:
                        with suppress(asyncio.exceptions.TimeoutError):
                            async with timeout(total_timeout):
                                return await func(*args, **kwargs)
                        msg = f'Timeout error, try {r} times.'
                        if show_logs:
                            _logger(msg)
                        if raise_exception:
                            raise asyncio.exceptions.TimeoutError(msg)
                    else:
                        return await func(*args, **kwargs)
                except exceptions_to_check as e:
                    if show_logs:
                        _logger(f'Error: {e}, Retrying # {r} in {mdelay} seconds...')
                # don`t sleep on the last try
                if r < mtries:
                    time.sleep(mdelay)
                    mdelay += increase_interval
                    continue
                return None

        return func_retry  # true decorator

    return deco_retry


def execution_time(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            return await func(*args, **kwargs)
        finally:
            ex_time = time.time() - start_time
            logger.info(f'Execution time {ex_time:.2f} seconds')

    return wrapper
