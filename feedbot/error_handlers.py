import asyncio
from asyncio.log import logger
from telethon import errors

async def catch_errors(func):
    async def _inner_catch(*args, **kwargs):
        try:
            out = await func(*args, **kwargs)
            return out
        except errors.FloodWaitError as e:
            logger.exception(e)
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.exception(e)
    return _inner_catch