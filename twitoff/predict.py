"""Prediction of Users based on Tweet embeddings."""
import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from .models import User
from .twitter import BASILICA

def predict_user(user1_name, user2_name, tweet_text):
    """Determine and return which user is more likely to say a given Tweet.
    
    # Arguments
        user1_name: str, twitter user name for user1 in comparison
        user1_name: str, twitter user name for user2 in comparison
        tweet_text: str, tweet text to evaluate

    # Returns
        prediction from logistic regression model
    """
    user1 = User.query.filter(User.name == user1_name).one()
    user2 = User.query.filter(User.name == user2_name).one()
    user1_embeddings = np.array([tweet.embedding for tweet in user1.tweet])
    user2_embeddings = np.array([tweet.embedding for tweet in user2.tweet])
    embeddings = np.vstack([user1_embeddings, user2_embeddings])
    labels = np.concatenate([np.ones(len(user1.tweet)),
                                np.zeros(len(user2.tweet))])
    log_reg = LogisticRegression().fit(embeddings, labels)
    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')
    return log_reg.predict(np.array(tweet_embedding).reshape(1, -1))