import asyncio
import functools
from asyncio.log import logger
from telethon import errors


def catch_errors():
    """
    Catch and handle errors if any.
    """

    def _inner_catch(func):
        async def _innest_catch(*args, **kwargs):
            try:
                out = await func(*args, **kwargs)
                return out
            except errors.FloodWaitError as e:
                logger.exception(e)
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.exception(e)

        return _innest_catch

    return _inner_catch
