from typing import List

from sqlalchemy import or_
from telethon import TelegramClient
from telethon.tl.custom import Button, Conversation

from feedbot import messages
from feedbot.database import User, FeedSource


def get_action_buttons(sender: User) -> List[List[Button]]:
    """
    Get buttons for main bot actions

    :param sender: sender's data
    """
    action = messages.subscribe if sender.daily_updates else messages.unsubscribe
    registered_buttons = [
        [Button.inline(messages.get_feeds), Button.inline(action)],
        [Button.inline(messages.help), Button.inline(messages.add_source)],
        [Button.inline(messages.sub_feed)]
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
        button = [[Button(f"Subscribe: {feed.id}")]]
        if feed not in user.feeds:
            button = [[Button(f"Unsubscribe: {feed.id}")]]
        
        feeds_msg.append(
            [f"<b>{feed.title}</b>\nurl: {feed.url}\npublic: {feed.public}",
            bot.build_reply_markup(button)])
    return feeds_msg

async def get_resp_msg(conv: Conversation, msg: str) -> str:
    await conv.send_message(msg)
    response = await conv.get_response()
    return response.text

async def send_feeds(feeds: List[FeedSource], user: User):
    pass