from twython import TwythonStreamer
from twitter_search import CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

# https://dev.twitter.com/docs/streaming-apis/streams/user

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print data['text'].encode('utf-8')
        # Want to disconnect after the first result?
        # self.disconnect()

    def on_error(self, status_code, data):
        print status_code, data

def stream():
    stream = MyStreamer(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    return stream.user()

if __name__ == '__main__':
    stream()
