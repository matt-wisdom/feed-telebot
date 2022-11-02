import asyncio
import os
import logging
from random import randrange
from typing import List, Tuple

import async_timeout
from telethon import TelegramClient, events

from feedbot.handlers import start_handler, new_message_handler, callback_handler
from feedbot.database import User
from feedbot.utils import send_feeds

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING
)


async def create_bot() ->  Tuple[TelegramClient, asyncio.Task]:
    """
    Create bot and register handlers
    """
    bot = await TelegramClient("bot", os.getenv("API_ID"), os.getenv("API_HASH")).start(
        bot_token=os.getenv("BOT_TOKEN")
    )
    await register_handlers(bot)
    task = asyncio.create_task(send_updates(bot))

    return bot, task


async def register_handlers(bot: TelegramClient) -> None:
    """
    Register handlers for events.
    """

    @bot.on(events.NewMessage)
    async def message(event):
        await new_message_handler(event, bot)

    @bot.on(events.NewMessage(pattern="/start"))
    async def start(event):
        await start_handler(event, bot)

    @bot.on(events.CallbackQuery)
    async def callback(event):
        await callback_handler(event, bot)

async def send_updates(bot: TelegramClient):
    """
        Send users that subscribed daily updates
    """
    while True:
        await asyncio.sleep(randrange(86400, 91200))
        queue = asyncio.Queue(1000)
        async def add_queue(queue: asyncio.Queue):
            while True:
                users = await asyncio.to_thread(lambda: User.query.filter_by(daily_updates=True).all())
                print("USers", users)
                for user in users:
                    await asyncio.sleep(1)
                    await queue.put(user)

        async def send(queue: asyncio.Queue):
            while True:
                with async_timeout.timeout(3) as tm:
                    user = await queue.get()
                if tm.expired:
                    await asyncio.sleep(10)
                    continue

                await asyncio.sleep(5)
                await send_feeds(user, bot, only_new=True)
        
        tasks = [*[send(queue) for _ in range(3)]] + [add_queue(queue)]
        await asyncio.gather(*tasks)



            