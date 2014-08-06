Hack-fixed issues:
    1. you have to wait for story_fork to update before you can add depth to an existing story tree
        - added manual update button as short-term fix
    2. if two stories are created before story_fork has updated, at least one of the tweet's links will be wrong
        - added manual update button as short-term fix
Unsolved issues:
    3. story_fork only has access to the 200 most recent tweets (only has potential access to the last 800)
        - this means once 200 tweets have been created, initial stories will not be accessible
        - need a db on heroku to permanently store all tweets
    4. Tweeting lots of small things would be incredibly annoying to your twitter followers
Solutions:
    1/2/4. There's no way to know if a user has tweeted, and this is the major problem with updating, and annoyance.
        - Let the user tweet on @st_f_'s behalf. Clean out any '@'s in the tweets to avoid users who might try to spam.
        - Tweeting locally then means immediate updates, no incorrect links, and no clogging up the user's feed
        - But then what's the point of twitter being involved at all? None whatsoever.
            - And anyway, then the app itself wouldn't be advertised by being used, i.e. a link to it being tweeted
    3. If a db was set up, this would be fixed, AND I would finally gain some experience using a db with web stuff
    1/2. Streaming API -- but this might require two dynos and would then cost $$
        - since streaming API requires two separate processes: one for HTML requests, the other for the API connection
        - still probably requires a db
