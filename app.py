import asyncio
import json
import os
from asyncio.log import logger

import httpx
from aiohttp import web

import config
from feedbot.bot import create_bot
from feedbot.database import FeedSource, create_all, session


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


async def server():
    async def backup(request):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                os.getenv("BACKUP_URL"),
                headers={"Authorization": f"Bearer {os.getenv('BACKUP_KEY')}"},
                files={"file": open("dev.db", "rb")},
            )
            if r.status_code != 200:
                return web.Response(text=f"Error {r.status_code}")
        return web.Response(text="Running")
    
    async def status(request):
        return web.Response(text="Running")


    asyncio.create_task(main())
    app = web.Application()
    app.add_routes([web.get("/", status), web.get("/backup", backup)])
    return app


if __name__ == "__main__":
    web.run_app(server())
