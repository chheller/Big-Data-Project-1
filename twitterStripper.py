import time
import datetime
from pymongo import MongoClient
import json
import tweepy
from tweepy import OAuthHandler
#############
#   PyMongo can be installed with pip: pip install pymongo
#   Tweepy can be installed wit pip: pip install tweepy
#############

consumer_key = 'DZywGzmksnJrOw1WpvAyp2ZsK'
consumer_secret = 'Zj6eWQuS0N8PU9kuLsWJvDoAv475jDOgBMdUxXL7E2cKWS3ypX'
access_token = '96603688-8o9HNqeiv0mZiT8rYo9t7sSjRORUcwdVtyPKhlPvZ'
access_token_secret = 'n8UY71GmWTwm1N9IXIdsAY2U9tVqwwbrlNrG9unxvlszs'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)

client = MongoClient('localhost', 27017)
db = client['twitter_db']

start_time = time.time()
last_sun = str(datetime.date.today() -
               datetime.timedelta(days=datetime.date.today().weekday() + 1))
last_mon = str(datetime.date.today() -
               datetime.timedelta(days=datetime.date.today().weekday() + 7))
searchQuery = ['#politics', "#Election2016"]


def crawler(searchQuery, maxTweets=100000, tweetsPerQry=1000):
    for word in searchQuery:
        max_id = -1
        tweetCount = 0
        collection = db['twitter_{0}'.format(word[1:])]
        while tweetCount < maxTweets:
            try:
                if (max_id <= 0):
                    new_tweets = api.search(lang="en",
                                            q=word, count=tweetsPerQry, since=last_mon, until=last_sun)
                else:
                    new_tweets = api.search(lang="en",
                                            q=word, count=tweetsPerQry, since=last_mon, until=last_sun, max_id=str(max_id - 1))

                if not new_tweets:
                    print("No more tweets found")
                    break

                for tweet in new_tweets:
                    collection.insert(json.loads(json.dumps(tweet._json)))

                tweetCount += len(new_tweets)
                print("Downloaded {0} tweets".format(tweetCount))
                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                # Just exit if any error
                print("some error : " + str(e))
                break

crawler(searchQuery=searchQuery)
