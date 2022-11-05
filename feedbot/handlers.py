from asyncio.log import logger

from rfc3986 import is_valid_uri
from sqlalchemy import and_, or_
from telethon import TelegramClient, events
from config import ADMIN_CONTACT

from feedbot import messages
from feedbot.database import FeedSource, User, session
from feedbot.error_handlers import catch_errors
from feedbot.utils import (get_resp_msg, list_feeds_sources, send_feeds,
                           send_with_action)


@catch_errors()
async def start_handler(event: events.NewMessage.Event, bot: TelegramClient):
    """
    First time users should first send the /start command.
    A user account will be created for them.

    NOTE: The first person to connect to the bot becomes the admin
    """
    sender_tg = await event.get_sender()
    sender_id = event.sender_id

    async with bot.conversation(await event.get_chat(), exclusive=False) as conv:
        await conv.cancel_all()
        # await event.respond("Conversations cancelled.")

    sender = User.query.filter_by(user_id=sender_id).first()
    if not sender:
        is_admin = False
        if not User.query.all():
            is_admin = True
            await event.respond(messages.made_admin)
        sender = User(user_id=sender_id, username=sender_tg.username, is_admin=is_admin)
        session.add(sender)
        session.commit()
        await event.respond(messages.welcome_new)
    else:
        await event.respond(messages.welcome_new)
    await send_with_action(sender, messages.registered, bot)

    raise events.StopPropagation


@catch_errors()
async def new_message_handler(event: events.NewMessage.Event, bot: TelegramClient):
    try:
        data = event.text
        if data.startswith("/"):
            return
        sender_id = event.sender_id
        sender: User = User.query.filter_by(user_id=sender_id).first()
        if not sender:
            await bot.send_message(sender_id, messages.not_registered)
        if data == messages.get_feeds:
            # Show available feeds
            if not sender.feeds:
                await send_with_action(sender, messages.no_feed, bot)
            await send_feeds(sender, bot, only_new=True)
        elif data in [messages.subscribe, messages.unsubscribe]:
            # User wants to subscribe/unsubscribe from daily updates
            what = True if data == messages.subscribe else False
            sender.daily_updates = what
            session.add(sender)
            session.commit()
            await send_with_action(sender, messages.success.format(what=data), bot)
        elif data == messages.help:
            # Help
            await send_with_action(
                sender, messages.help_msg.format(admin=ADMIN_CONTACT), bot
            )
        elif data == messages.add_source:
            # Add new feed source
            async with bot.conversation(sender_id) as conv:
                title = await get_resp_msg(conv, messages.ask_fd_title)
                description = await get_resp_msg(conv, messages.ask_fd_desc)
                url = await get_resp_msg(conv, messages.ask_fd_url)
                if not is_valid_uri(url):
                    await send_with_action(sender, messages.invalid_data, bot)
                    return
                is_public = False
                if sender.is_admin:
                    public = await get_resp_msg(conv, messages.ask_fd_public)
                    if public.lower() in ["yes", "y"]:
                        is_public = True
                new_source = FeedSource(
                    creator=sender_id,
                    url=url,
                    title=title,
                    public=is_public,
                    description=description,
                )
                session.add(new_source)
                session.commit()
        elif data == messages.sub_feed:
            # Subscribe to public or user provided feeds
            feed_sources = list_feeds_sources(sender, bot)
            for feed_src in feed_sources:
                await bot.send_message(
                    sender.user_id, feed_src[0], buttons=feed_src[1], parse_mode="html"
                )
            # await send_with_action(sender, messages.success.format(what=data[0]), bot)
        else:
            pass
            # await send_with_action(sender, messages.invalid, bot)
    except Exception as e:
        logger.exception(e)
        session.rollback()


@catch_errors()
async def callback_handler(event: events.NewMessage.Event, bot: TelegramClient):
    """
    Callbacks for inline buttons
    """
    try:
        sender_id = event.sender_id
        sender: User = User.query.filter_by(user_id=sender_id).first()
        if not sender:
            await bot.send_message(sender_id, messages.not_registered)
        data = event.data.decode("utf-8")
        if data.startswith("Subscribe:") or data.startswith("Unsubscribe:"):
            # Subscribe to a specific feed
            data = data.split(":")
            id = int(data[1])
            filter = or_(
                and_(FeedSource.id == id, FeedSource.public == True),
                and_(FeedSource.id == id, FeedSource.creator == sender.user_id),
            )
            feed = FeedSource.query.filter(filter).first()
            if not feed:
                await send_with_action(sender, messages.invalid_data, bot)
            if data[0].startswith("Subscribe"):
                sender.feeds.append(feed)
            else:
                sender.feeds.remove(feed)
            session.add(sender)
            session.commit()
            await send_with_action(sender, messages.success.format(what=data[0]), bot)
        else:
            await send_with_action(sender, messages.invalid, bot)
    except Exception as e:
        logger.exception(e)
        session.rollback()
