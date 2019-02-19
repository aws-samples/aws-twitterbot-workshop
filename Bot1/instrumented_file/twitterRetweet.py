import boto3
import tweepy
import os
import json
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

ssm = boto3.client('ssm', region_name='us-west-2')


def authenticate_twitter():
    xray_recorder.begin_subsegment('twitter-authentication')
    xray_recorder.begin_subsegment('ssm-get_parameter')
    consumer_key = (ssm.get_parameter(Name='twitter-consumer-key', WithDecryption=True))['Parameter']['Value']
    consumer_secret = (ssm.get_parameter(Name='twitter-consumer-secret', WithDecryption=True))['Parameter']['Value']
    access_token = (ssm.get_parameter(Name='twitter-access-token', WithDecryption=True))['Parameter']['Value']
    access_token_secret = (ssm.get_parameter(Name='twitter-access-token-secret', WithDecryption=True))['Parameter']['Value']
    xray_recorder.end_subsegment()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    xray_recorder.end_subsegment()
    return api

def retweet(api, search, numberOfTweets):
    xray_recorder.begin_subsegment('retweet')
    for tweet in tweepy.Cursor(api.search, search).items(numberOfTweets):
        try:
            tweet_id = tweet.id
            print(tweet_id)
            if tweet.lang == "en":
                tweet.retweet()
                print('Retweeted the tweet')
            else:
                print('no retweet')
        except tweepy.TweepError as e:
            print(e.reason)
        except StopIteration:
            break
    xray_recorder.end_subsegment()


def lambda_handler(event, context):
    try:     
        patch_all()
        apiuse = authenticate_twitter()
        
        searchString = os.environ['TweetSearchString']
        
        numberOfTweets = 5
        print('String to look for: {0} and nb of tweets to retrieve: {1}'.format(searchString,numberOfTweets))
        
        retweet(apiuse, searchString, numberOfTweets)

    except Exception as e:
        print(e)
    
    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": "TwitterPoller"}
        ),
    }