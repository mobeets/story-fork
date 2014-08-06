from datetime import datetime
from collections import defaultdict

from sqlalchemy import Column, Integer, PickleType

from bin.db_connect import Base
from bin.mutabledict import MutableDict
from twitter_search import user_handle, user_mentions, status_user_info, status_expanded_urls, status_text, status_dt, status_url, status_id, status_embed_html, status_is_retweet

DOMAINS = ['www.jehosafet.com', 'thu-jehosafet.herokuapp.com']
BASE_URLS = ['http://' + domain + '/story_fork/view/' for domain in DOMAINS]
URL = BASE_URLS[0]
BASE_USER = 'st_f_'
USER = '@' + BASE_USER
PRE_ROOT_TINE_ID = 0
STORY_FORK_DB_TABLE_NAME = 'story_fork'

class Tweet(object):
    def __init__(self, mention, html):
        self.mention = mention
        self.html = html

def update_tweets(tweets):
    handle = user_handle()
    for mention in user_mentions(handle):
        cur_id = status_id(mention)
        if cur_id in tweets or status_is_retweet(mention):
            continue
        tweet_html = status_embed_html(handle, mention)
        tweet = Tweet(mention, tweet_html)
        tweets[cur_id] = tweet

def process_tweets(tweets):
    def unpack_tine_ref(all_urls):
        """
        The ref references the parent tweet
        """
        def base_url(url):
            for x in BASE_URLS:
                if x in url:
                    return x
        urls = [url.split(base_url(url))[1] for url in all_urls if base_url(url)]
        if not urls:
            print 'ERROR: no url {0} in {1}'.format(all_urls, BASE_URLS)
            return None
        url = urls[-1]
        try:
            story_id, tine_id = url.split('/')
        except ValueError:
            print 'ERROR: url {0} without /'.format(url)
            return None
        try:
            return TineRef(int(story_id), int(tine_id))
        except ValueError:
            print 'ERROR: cannot make TineRef with story_id {0}, tine_id {1}, in url {2}'.format(story_id, tine_id, url)
            return None
    def unpack_message(text):
        """ removes username, and last word (i.e. url)"""
        return ' '.join(text.replace(USER, '').split()[:-1])
    new_tine_lookup = defaultdict(list)
    tine_refs_in_order_read = []
    for tweet in tweets:
        mention = tweet.mention
        parent_ref = unpack_tine_ref(status_expanded_urls(mention))
        if not parent_ref:
            continue
        u = User(*status_user_info(mention))
        t = Tine(None, u, status_dt(mention), unpack_message(status_text(mention)), status_url(mention), tweet.html)
        new_tine_lookup[parent_ref].append(t)
        tine_refs_in_order_read.append(parent_ref)
    return new_tine_lookup, tine_refs_in_order_read

class StoryForkData(Base):
    __tablename__ = STORY_FORK_DB_TABLE_NAME
    id = Column(Integer, primary_key=True)
    story_data = Column(MutableDict.as_mutable(PickleType))
    story_tweet_ids = Column(MutableDict.as_mutable(PickleType))
    tweets = Column(MutableDict.as_mutable(PickleType))

    @staticmethod
    def singleton(db_session):
        return db_session.query(StoryForkData).one()

    @staticmethod
    def empty_singleton():
        return StoryForkData(story_data={}, story_tweet_ids={}, tweets={})

    def existing_tine_ref_lookup(self):
        tine_refs = {}
        for story_id, story in self.story_data.iteritems():
            for tine_id, tine in story.tines.iteritems():
                tine_refs[TineRef(story_id, tine_id)] = tine
        return tine_refs

    def get_next_story_index(self):
        if not self.story_data:
            return 1
        return max(self.story_data)+1

    def print_status(self):
        out = 'Tweets saved: {0}\n'.format(len(self.tweets))
        out += 'Tweets processed: {0}\n'.format(len(self.story_tweet_ids))
        out += 'Stories: {0}\n'.format(self.story_data.keys())
        return out

    def update(self):
        try:
            update_tweets(self.tweets)
            new_tweet_ids = list(set(self.tweets) - set(self.story_tweet_ids))
            unprocessed_tweets = [self.tweets[i] for i in new_tweet_ids]
            chronological_unprocessed_tweets = sorted(unprocessed_tweets, key=lambda tweet: status_dt(tweet.mention))
            print 'Found {0} unprocessed tweets'.format(len(chronological_unprocessed_tweets))
            orphan_tines, tine_refs_in_order_read = process_tweets(chronological_unprocessed_tweets)
            for i in new_tweet_ids:
                self.story_tweet_ids[i] = None
        except Exception, e:
            # mostly just trying to catch twython.exceptions.TwythonRateLimitError 
            print e
            print '--------------------'
            print '--------------------'
            print 'RATE LIMIT EXCEEDED?'
            print '--------------------'
            print '--------------------'
            return
        c = 0
        s = 0
        for tine_ref in tine_refs_in_order_read:
            tines = orphan_tines[tine_ref]
            for tine in tines:
                if tine_ref.is_pre_root:
                    """
                    Create new story
                    """
                    story_id = tine_ref.story_id
                    if story_id in self.story_data:
                        story_id = self.get_next_story_index()
                    self.story_data[story_id] = Story(story_id, tine.user, tine.date, '', tine)
                    s += 1
                    c += 1
                else:
                    """
                    Update existing story
                    """
                    if tine_ref.story_id not in self.story_data:
                        """
                        This is either because a tweet involved was deleted,
                        or because the paging doesn't go back far enough
                        (currently only knows the last 200 tweets)
                        """
                        print '-------------------------------'
                        print 'ERROR - story_id {0} not found'.format(tine_ref.story_id)
                        print '-------------------------------'
                        continue
                    story = self.story_data[tine_ref.story_id]
                    if tine_ref.tine_id not in story.tines:
                        """
                        Same as above.
                        """
                        print '---------------------------------------------'
                        print 'ERROR - tine_id {0} not found in story_id {1}'.format(tine_ref.tine_id, tine_ref.story_id)
                        print '---------------------------------------------'
                        continue
                    c += 1
                    story.fork(tine_ref.tine_id, tine)
                    # the below needs to be done to trigger the PickleType to notice the change
                    self.story_data[tine_ref.story_id] = story
        print 'Added {0} new stories and {1} new tines'.format(s, c)

    def clear_stories(self):
        self.story_data = {}
        self.story_tweet_ids = {}

    def clear_all(self):
        self.tweets = {}
        self.clear_stories()

class User(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url

class Story(object):
    def __init__(self, index, user, date, title, root_tine):
        self.index = index
        self.user = user
        self.date = date
        self.title = title
        self.next_tine_index = 1

        self.root_tine = root_tine
        self.root_tine.story_index = self.index
        self.root_tine.index = self.get_next_tine_index()
        self.tines = {self.root_tine.index: self.root_tine}

    def get_next_tine_index(self):
        ind = self.next_tine_index
        self.next_tine_index += 1
        return ind

    def fork(self, parent_index, tine):
        tine.story_index = self.index
        tine.index = self.get_next_tine_index()
        self.tines[tine.index] = tine
        tine.parent_tine = self.tines[parent_index]
        tine.parent_tine.child_tines.append(tine)
        print 'Parent: {0}\nNew child: {1}\nChildren: {2}\n'.format(tine.parent_tine, tine, len(tine.parent_tine.child_tines))
        return tine.index

    def to_json(self):
        return self.root_tine.to_json()

class Tine(object):
    def __init__(self, parent_tine, user, date, content, url, embed):
        self.story_index = None
        self.index = None
        self.parent_tine = parent_tine
        self.user = user
        self.date = date
        self.content = content if content else ''
        self.embed = embed
        self.child_tines = []

    def url(self):
        return str(self.embed['url'])

    def to_json(self):
        return {
                "name": str(self.content),
                "index": self.index,
                "story_index": self.story_index,
                "children": [child.to_json() for child in self.child_tines],
                "url": self.url(),
            }

    def __str__(self):
        return '{0} says "{1}"'.format(self.user.name, self.content)

class TineRef(object):
    def __init__(self, story_id, tine_id):
        self.story_id = story_id
        self.tine_id = tine_id
        self.is_pre_root = self.tine_id == PRE_ROOT_TINE_ID

def fake_story():
    return Story(1, 'a', datetime.now(), '', Tine(None, 'b', datetime.now(), '', '', {'url': ''}))
