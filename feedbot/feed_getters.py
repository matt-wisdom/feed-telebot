"""
    All feed functions should start with get_ and should return a list
    in the format: [[title, image_link], [entries...]]
    Each entry should be like: [title, link, author, dt, summary].
"""

import json
import os
import time
import logging
from typing import List

import dotenv
import requests
import bs4
import feedparser

from config import LAST_LATEST_FEEDS

dotenv.load_dotenv(".env")

feed_outputs = List[List[str]]
logger = logging.getLogger()


def get_feeds(url: str, src: str = None) -> feed_outputs:
    """
    Get feeds using feedparser from url.
    Notifications are appended to queue if
    specified.
    :param url: RSS feed url to get feed from.
    :param src: Source name.
    """
    last = {}
    try:

        with open(LAST_LATEST_FEEDS) as f:
            last = json.load(f)
    except Exception as e:
        logger.debug(e)
    try:
        tm = time.strptime(last[src])
    except KeyError:
        tm = time.gmtime(0)

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
        src = feed_title.lower().replace(" ", "_")
    try:
        feed_img = feed_data.get("image").get("href")
    except AttributeError:
        feed_img = ""
    entries = []
    for feed_entry in feed["entries"]:
        date_published = feed_entry.get("published_parsed")
        if not bool(int(os.getenv("TESTING"))):
            if date_published > tm:
                # If feed is newer
                last[src] = time.asctime(date_published)
            else:
                continue
        try:
            entry_published = time.asctime(feed_entry.get("published_parsed"))
        except AttributeError:
            logger.debug(feed_entry.get("published_parsed"))
            entry_published = ""
        entries.append(
            [
                feed_entry.get("title"),
                feed_entry.get("link"),
                feed_entry.get("author"),
                entry_published,
                feed_entry.get("summary"),
            ]
        )
    if not bool(int(os.getenv("TESTING"))):
        with open(LAST_LATEST_FEEDS, "w") as f:
            json.dump(last, f)
    return [[feed_title, feed_img], entries]


def get_thn() -> feed_outputs:
    """
    Gather articles from the first page of https://thehackernews.com
    """
    r = requests.get("https://thehackernews.com").text
    b = bs4.BeautifulSoup(r, 'lxml')
    posts = b.find_all(class_="body-post")
    entries = []
    for i in posts:
        story = i.find(class_="story-link")
        lnk = story.get("href")
        title = story.find(class_="home-title").text
        author = story.find(class_="item-label").find("span").text.strip()[1:]
        summary = story.find(class_="home-desc").text
        dt = story.find(class_="item-label").text.split("\ue804")[0][1:]
        entries.append([title, lnk, author, dt, summary])
    return [
        [
            "The Hacker News",
            "./asset/thn.jpg",
        ],
        entries,
    ]
