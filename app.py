from asyncio.log import logger
import json
import asyncio
from feedbot.database import create_all, FeedSource, session
from feedbot.bot import create_bot
import config


async def main():
    try:
        create_all()
        json_data = json.load(open(config.FEED_SRC_FILE))
        for title, (url, desc) in json_data.items():
            fd_src = FeedSource(public=True, url=url, title=title, description=desc)
            session.add(fd_src)
        session.commit()
        bot = await create_bot()
        await bot.run_until_disconnected()
    except Exception as e:
        logger.exception(e)
        session.rollback()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
