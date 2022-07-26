"""
    All feed functions should start with get_ and should return a list
    in the format: [[title, image_link], [entries...]]
    Each entry should be like: [title, link, author, dt, summary].
"""

import logging
import os
import time
from datetime import datetime as dt
from typing import Dict, List

import feedparser
from sqlalchemy import and_

from feedbot import feed_getters
from feedbot.database import Feed, FeedSource, User, session

logger = logging.getLogger()

logger = logging.getLogger()


def get_feeds(url: str, src: str = None) -> List[List[str]]:
    """
    Get feeds using feedparser from url.
    Notifications are appended to queue if
    specified.
    :param url: RSS feed url to get feed from.
    :param src: Source name.
    """

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        logger.exception(e)
        return [[], []]
    feed_data = feed["feed"]
    if not feed_data:
        feed_data = {}
    feed_title = feed_data.get("title")
    if src is None:
        src = feed_title
    try:
        feed_img = feed_data.get("image").get("href")
    except AttributeError:
        feed_img = ""
    entries = []
    for feed_entry in feed["entries"]:
        # date_published = feed_entry.get("published_parsed")
        try:
            entry_published = time.asctime(feed_entry.get("published_parsed"))
        except AttributeError:
            logger.debug(feed_entry.get("published_parsed"))
            entry_published = ""
        entries.append(
            {
                "title": feed_entry.get("title"),
                "link": feed_entry.get("link"),
                "author": feed_entry.get("author"),
                "published": entry_published,
                "published_parsed": feed_entry.get("published_parsed"),
                "summary": feed_entry.get("summary"),
            }
        )
    return [[feed_title, feed_img], entries]


def parse_feed_content(feed: list) -> List[str]:
    """
    Get (and filter) data from feed entries.
    """
    filtered_feeds = []
    for entry in feed[1]:
        src, img_src = feed[0]
        header = entry[0]
        url = entry[1]
        summary = entry[-1]
        date = entry[-2]
        try:
            # feeds with ://feeds.feedburner are incomprehensible
            #  so remove them
            if "://feeds.feedburner" not in summary:
                filtered_feeds.append([img_src, header, summary, url, date, src])
        except Exception as e:
            logger.exception(e)
    return filtered_feeds


def gather_feeds(user: User, only_new: bool = False) -> Dict[str, List]:
    """
    This function check gathers feeds.
    It checks if feed sources were changed
    or feeds haven't been gathered that day
    and gathers and caches the feeds else it
    uses the stored feeds.
    """

    feeds = Feed.query.filter_by(user_id=user.user_id).all()
    if bool(int(os.getenv("TESTING", 0))) or not feeds:
        date_obj = dt.fromtimestamp(0)
    else:
        date_obj = feeds[-1].date_checked
    feeds_srcs: List[FeedSource] = user.feeds
    feeds_gotten = dict()
    if dt.utcnow().date() != date_obj:
        # User.query.filter_by(user_id=user.user_id).delete()
        date_chk = dt.today().date()
        for src in feeds_srcs:
            try:
                feed = feed_getters.get_feeds(src.url, src.title)
                if not feed[1]:
                    continue
                # feed[1] = parse_feed_content(feed)
                if not bool(int(os.getenv("TESTING", 0))):
                    for fd in feed[1]:
                        if Feed.query.filter_by(link=fd["link"]).first():
                            continue
                        cached_feed = Feed(
                            user_id=user.user_id,
                            date_checked=date_chk,
                            feed_title=feed[0][0],
                            img_link=feed[0][1],
                            title=fd["title"],
                            link=fd["link"],
                            author=fd["author"],
                            published=fd["published"],
                            summary=fd["summary"],
                            src=src.title,
                        )
                        session.add(cached_feed)
                feeds_gotten[src.title] = feed
            except Exception as e:
                session.rollback()
                logging.exception(str(e))
        # Store fields
    else:
        if not only_new:
            for src in feeds_srcs:
                feeds = Feed.query.filter(
                    and_(Feed.src == src, Feed.user_id == user.user_id)
                ).all()
                feed = [
                    [feeds[0].feed_title, feeds[0].img_link],
                    [
                        [fd.title, fd.link, fd.author, fd.published, fd.summary]
                        for fd in feeds
                    ],
                ]
                feeds_gotten[src.title] = feed
    session.commit()
    return feeds_gotten
