from typing import List

from sqlalchemy import or_
from telethon import TelegramClient
from telethon.tl.custom import Button, Conversation

from feedbot import messages
from feedbot.database import User, FeedSource
from feedbot.feed_getters import gather_feeds


def get_action_buttons(sender: User) -> List[List[Button]]:
    """
    Get buttons for main bot actions

    :param sender: sender's data
    """
    action = messages.subscribe if sender.daily_updates else messages.unsubscribe
    kargs = dict(resize=False, single_use=False, selective=True)
    registered_buttons = [
        [Button.text(messages.get_feeds), Button.text(action)],
        [Button.text(messages.help), Button.text(messages.add_source)],
        [Button.text(messages.sub_feed)]
    ]
    return registered_buttons


async def send_with_action(sender: User, message: str, bot: TelegramClient):
    """
    Send a message with buttons for main bot actions.

    :param sender: sender's data
    :param message: message to send
    :param bot: telethon's TelegramClient for the bot
    """

    registered_buttons = get_action_buttons(sender)
    markup = bot.build_reply_markup(registered_buttons)
    await bot.send_message(sender.user_id, message, buttons=markup)


def list_feeds_sources(user: User, bot: TelegramClient) -> List[List]:
    """
        Get all feeds a user can subscribe to or unsubscribe from
        and return the messages to be sent for each feed.
    """
    available_feeds = FeedSource.query.filter(
        or_(FeedSource.public == True, FeedSource.creator == user.user_id)
    ).all()
    feeds_msg = []
    
    for feed in available_feeds:
        button = [[Button.inline(f"Subscribe: {feed.id}")]]
        if feed not in user.feeds:
            button = [[Button.inline(f"Unsubscribe: {feed.id}")]]
        
        feeds_msg.append(
            [f"<b>{feed.title}</b>\nurl: {feed.url}\npublic:"
             f"{feed.public}\n\nDescription:\n{feed.description}",
            bot.build_reply_markup(button)])
    return feeds_msg

async def get_resp_msg(conv: Conversation, msg: str) -> str:
    await conv.send_message(msg)
    response = await conv.get_response()
    return response.text

async def send_feeds(feeds: List[FeedSource], user: User, bot: TelegramClient):
    feed_contents = gather_feeds(user)
    for title, entries in feed_contents.items():
        msg = f"<b>Feeds from {title}</b>"
        bot.send_message(user.user_id, message=msg, parse_mode="html")
        for entry in entries[1]:
            article = f"<b>{entry[0].title()}</b>\n{entry[4]}\n\n"\
                      f"author: {entry[2]}\npublished: {entry[3]}\n"\
                      f"Link: {entry[1]}"
            bot.send_message(user.user_id, message=article, file=entry[0][1],
                            parse_mode="html")
        
    # bot.loop.run_in_executor()

