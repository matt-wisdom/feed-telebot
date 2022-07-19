from feedbot import feed_getters

def test_get_feeds():
    # Test with src
    feed = feed_getters.get_feeds("https://stackabuse.com/rss/",
            "stackabuse")
    # Feeds result must have two elements
    assert len(feed) == 2

    # Title and image should be pressed
    assert len(feed[0]) == 2
    # Feed results 
    if len(feed[1]) > 0:
        assert len(feed[1][0]) == 5
    
    # Test without src
    feed = feed_getters.get_feeds("https://stackabuse.com/rss/",)
    # Feeds result must have two elements
    assert len(feed) == 2

    # Title and image should be pressed
    assert len(feed[0]) == 2

    # Feed results 
    if len(feed[1]) > 0:
        assert len(feed[1][0]) == 5
                        

def test_extra_sources():
    """
         Test getter for other sources
    """
    getter_fns = dir(feed_getters)
    extra_fds = filter(lambda x: x.startswith("get") and x != 'get_feeds'\
                and callable(getattr(feed_getters, x)), getter_fns)
    xtra_fds = []
    for i in extra_fds:
        xtra_fds.append(getattr(feed_getters, i))
    assert len(xtra_fds) > 0
    for src in xtra_fds:
        print("Trying ", src)
        # src should be callable
        feed = src()
        # Feeds result must have two elements
        assert len(feed) == 2

        # Title and image should be pressed
        assert len(feed[0]) == 2

        # Feed results 
        if len(feed[1]) > 0:
            assert len(feed[1][0]) == 5