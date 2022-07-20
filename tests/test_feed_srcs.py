from feedbot import feed_getters


def test_get_feeds():
    # Test with src
    feed = feed_getters.get_feeds("https://stackabuse.com/rss/", "stackabuse")
    # Feeds result must have two elements
    assert len(feed) == 2

    # Title and image should be pressed
    assert len(feed[0]) == 2
    # Feed results
    if len(feed[1]) > 0:
        assert len(feed[1][0]) == 5

    # Test without src
    feed = feed_getters.get_feeds(
        "https://stackabuse.com/rss/",
    )
    # Feeds result must have two elements
    assert len(feed) == 2

    # Title and image should be pressed
    assert len(feed[0]) == 2

    # Feed results
    if len(feed[1]) > 0:
        assert len(feed[1][0]) == 5

