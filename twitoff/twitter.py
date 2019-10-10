import basilica
import tweepy
from decouple import config
from .models import DB, Tweet, User

TWITTER_USERS = ['elonmusk', 'nasa', 'lockheedmartin', 'bigdata', 'buzzfeed', 'kdnuggets', 'google', 'garyvee', 'theeconomist', 'funnyordie']

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'), config('TWITTER_CONSUMER_SECRET'))

#TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY,TWITTER_CONSUMER_SECRET)
TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'), config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(config('BASILICA_KEY'))


def add_or_update_user(username):
    """Add a user and their tweets to database."""
    try:
        # Get user info from tweepy API    
        twitter_user = TWITTER.get_user(username)


        # Add as many recent non-retweet/reply tweets as possible
        # 200 is a Twitter API limit for single request
        tweets = twitter_user.timeline(count=200, 
                                       exclude_replies=True, 
                                       include_rts=False, 
                                       tweet_mode='extended')

        newest_tweet_id = tweets[0].id                                       
        # Add user info to User table in database
        db_user = User(id=twitter_user.id, 
                       name=twitter_user.screen_name,
                       followers=twitter_user.followers_count,
                       newest_tweet_id=newest_tweet_id)

        DB.session.add(db_user)

        # Loop over each tweet 
        for tweet in tweets:

            # Get Basilica embedding for each tweet
            embedding = BASILICA.embed_sentence(tweet.full_text, 
                                                model='twitter')

            # Add tweet info to Tweets table in database
            db_tweet = Tweet(id=tweet.id, 
                              text=tweet.full_text[:300],
                              embedding=embedding)
            db_user.tweet.append(db_tweet)
    #        DB.session.add(db_tweet)
    except Exception as e:
        print('Error processing {}: {}'.format(username, e))
        raise e
    else:
        DB.session.commit()


def add_default_users(users=TWITTER_USERS):
    """
    Add/update a list of users (strings of user names).
    May take awhile, so run "offline" (flask shell).
    """
    for user in users:
        add_or_update_user(user)


def update_all_users():
    """Update all Tweets for all Users in the User table."""
    for user in User.query.all():
        add_or_update_user(user.name)