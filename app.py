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
            if FeedSource.query.filter_by(url=url, public=True).first():
                logger.info(f"{url} already exists in database. Not adding.")
                continue
            else:
                logger.info(f"{url} does not exists in database. Adding.")
            fd_src = FeedSource(public=True, url=url, title=title, description=desc)
            session.add(fd_src)
        session.commit()
        bot, task = await create_bot()
        await bot.run_until_disconnected()

        # Cancel task
        task.cancel()
        await asyncio.sleep(5)
    except Exception as e:
        logger.exception(e)
        session.rollback()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())