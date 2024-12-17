import tweepy
import time

# Twitter API credentials
consumer_key = "1868610138292244481-PW1jmkMNRTiQPoBhhcIgwf596FOyxu"
consumer_secret = "929zw0q3CH1iZk957TSoTSL2YxeX1zlr7pWi7tSpAF4Ga"
access_key = "S9ZtLZ1ki0h4FS3nPDhOSbSxs"
access_secret = "FlENh5NeU6VDZkbiGRxrvjpJ0yYZxzZA50Y4YrOaBqg97RNJaD"

# Authenticate to Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Check the connection
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

# Function to get tweets based on id
def get_tweets(tweet_ids):
    tweets = []
    for i in tweet_ids:
        try:
            tweet = api.get_status(i)
            tweets.append(tweet.text)
        except tweepy.TweepError as te:
            print(f"Failed to get tweet with ID {i}, reason:", te.reason)
        time.sleep(1)  # To avoid rate limit
        print(tweet.text)
    return tweets

# Read tweet IDs from file
with open('sources/ids_twitter_data_breaches.txt', 'r') as f:
    tweet_ids = f.read().splitlines()
with open('sources/ids_twitter_infosec_1.txt', 'r') as f:
    tweet_ids += f.read().splitlines()
with open('sources/ids_twitter_infosec_2.txt', 'r') as f:
    tweet_ids += f.read().splitlines()
with open('sources/ids_twitter_infosec_3.txt', 'r') as f:
    tweet_ids += f.read().splitlines()

# Get tweets based on the IDs
tweets = get_tweets(tweet_ids)

# Save the tweets to a file
with open('sources/tweets.txt', 'w') as f:
    for tweet in tweets:
        f.write("%s\n" % tweet)
