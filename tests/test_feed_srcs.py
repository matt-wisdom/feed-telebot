from feedbot import feed_getters


def test_get_feeds():
    # Test with src
    feed = feed_getters.get_feeds("https://stackabuse.com/rss/", "stackabuse")
    assert len(feed) == 2

    assert len(feed[0]) == 2
    # Feed results
    if len(feed[1]) > 0:
        assert len(feed[1][0]) == 5

    # Test without src
    feed = feed_getters.get_feeds(
        "https://stackabuse.com/rss/",
    )
    assert len(feed) == 2

    assert len(feed[0]) == 2

    # Feed results
    if len(feed[1]) > 0:
        assert len(feed[1][0]) == 5
