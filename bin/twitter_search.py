import os
import sys
import argparse
from twython import Twython
from dateutil import parser

# @st_f_
# https://dev.twitter.com/apps/4784263/show
CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
OAUTH_TOKEN = os.environ['TWITTER_OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['TWITTER_OAUTH_TOKEN_SECRET']

# https://github.com/ryanmcgrath/twython
# https://twython.readthedocs.org/en/latest/usage/starting_out.html#oauth1
def get_token():
    twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, oauth_version=2)
    ACCESS_TOKEN = twitter.obtain_access_token()
    return ACCESS_TOKEN

def user_handle():
    return Twython(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

def handle(access_token):
    return Twython(CONSUMER_KEY, access_token=access_token)

def search(query, access_token):
    return handle(access_token).search(q=query)

def user_mentions(handle):
    return handle.get_mentions_timeline(include_rts=1, count=200)

def user_mentioned_in_status(screen_name, status):
    return screen_name in [x['screen_name'] for x in status['entities']['user_mentions']]

def status_is_retweet(status):
    return 'retweeted_status' in status

def status_id(status):
    return status['id_str']

def status_text(status):
    return status['text']

def status_url(status):
    screen_name = status['user']['screen_name']
    tweet_id = status_id(status)
    return 'http://twitter.com/{0}/status/{1}'.format(screen_name, tweet_id)

def status_embed_html(handle, status):
    tweet_id = status_id(status)
    return handle.get_oembed_tweet(id=tweet_id)

def status_user_info(status):
    name = status['user']['name']
    url = 'https://twitter.com/{0}'.format(status['user']['screen_name'])
    return name, url

def status_dt(status):
    return parser.parse(status['created_at'])

def status_expanded_urls(status):
    return [x['expanded_url'] for x in status['entities']['urls']]

def main():
    arg_parser = argparse.ArgumentParser(prog='python test_search.py')
    arg_parser.add_argument('--get-token', help='request access token', action='store_true')
    arg_parser.add_argument('--query', help='search for query')
    arg_parser.add_argument('--token', help='access token')
    args = arg_parser.parse_args(sys.argv[1:])
    if args.get_token:
        print get_token()
    elif args.query:
        print search(args.query, args.token)
    else:
        arg_parser.print_help()

if __name__ == '__main__':
    main()
