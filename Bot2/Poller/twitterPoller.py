from TwitterSearch import TwitterSearchOrder, TwitterUserOrder, TwitterSearch, TwitterSearchException
import boto3
import datetime
import time
import json
import os

# Get the service resource
sqs = boto3.resource('sqs', region_name='us-west-2')
ssm = boto3.client('ssm', region_name='us-west-2')

global queueName
queueName = os.environ['sqsQueue']
#queueName = 'testMessage'
print("Queue from env variable: " + queueName)
if queueName == None:
    queueName = 'testMessage'

# max id of tweet.
global next_max_id
#next_max_id = 0

# Validate the tweet has a media (photo)
def validate_tweet(tweet):
    if (tweet.get('entities', {}).get('media')):
        return True
    return False

def authenticate_twitter():
    # it's about time to create a TwitterSearch object with our secret tokens
    # The tokens are stored in SSM and encrypted

    ts = TwitterSearch(
        consumer_key = (ssm.get_parameter(Name='twitter-consumer-key', WithDecryption=True))['Parameter']['Value'],
        consumer_secret = (ssm.get_parameter(Name='twitter-consumer-secret', WithDecryption=True))['Parameter']['Value'],
        access_token = (ssm.get_parameter(Name='twitter-access-token', WithDecryption=True))['Parameter']['Value'],
        access_token_secret = (ssm.get_parameter(Name='twitter-access-token-secret', WithDecryption=True))['Parameter']['Value']
     )
    return ts

def defineMaxID():
    now = datetime.datetime.now()
    datefortweet = datetime.date(now.year, now.month, now.day)
    dateOfLastTweet = os.environ['DateOfLastTweet']
    #dateOfLastTweet = datetime.date(now.year, now.month, now.day)
    
    print("dateofLastWeek: " + str(dateOfLastTweet))

    if (dateOfLastTweet == datefortweet):
        next_max_id = int((ssm.get_parameter(Name='twitter-max-id'))['Parameter']['Value'])
    else:
        next_max_id = 0
        #dateOfLastTweet = datefortweet
        tweet_list = ''
        ssm.put_parameter(Name='day-tweet-processed', Type='StringList', Value=tweet_list, Overwrite=True)
        os.environ['DateOfLastTweet'] = str(dateOfLastTweet)
    print("MaxID: %i" % next_max_id)
    
    return next_max_id

def configureSearch(id_tweet):
    print("ConfigureSearch: "+ str(id_tweet))
    now = datetime.datetime.now()
    datefortweet = datetime.date(now.year, now.month, now.day)

    twSOrder = TwitterSearchOrder() # create a TwitterSearchOrder object
    #twSOrder.set_keywords(['from:YodaBotter', 'to:YodaBotter'], or_operator = True)
    twSOrder.add_keyword("#AWSNinja")
    #twSOrder.set_language('en') # we want to see English tweets only
    twSOrder.set_include_entities(True) # and get all the entities incl. Media
    print("Search: " + twSOrder.create_search_url())
    twSOrder.set_since(datefortweet)
    
    return twSOrder

def build_send_sqs_message(screenName, tweetBody, mediaID, mediaURL):
    # Get the queue
    queue = sqs.get_queue_by_name(QueueName=queueName)
    
    # Create the body of message in SQS
    MessageBody="@"+screenName+ ": " + tweetBody

    # Put attributes in SQS
    MessageAttributes={
        'mediaID': {
            'DataType': 'String',
            'StringValue': mediaID
        },
        'mediaURL': {
            'DataType': 'String',
            'StringValue': mediaURL
        }
    }
    queue.send_message(MessageBody=MessageBody, MessageAttributes=MessageAttributes) 

def lambda_handler(event, context):
    try:
        twitterS = authenticate_twitter()
        #maxID = defineMaxID()
        tso = configureSearch(0)
        
        imageTweet = 0
        #print("maxID: %i" % maxID)

        for tweet in twitterS.search_tweets_iterable(tso):
            tweet_id = int(tweet['id'])
            print("TweetID: %i" % tweet_id)
            # current ID is lower than current next_max_id?
            #if (tweet_id > maxID) or (maxID == 0):
            #    maxID = tweet_id
                
            if (validate_tweet(tweet)):
                mediaURL = tweet['entities']['media'][0]['media_url']
                mediaID = str(tweet['entities']['media'][0]['id'])
                screenName = tweet['user']['screen_name']
                tweetBody = tweet['text']
                print("Media: " + mediaID + " " + mediaURL)
                build_send_sqs_message(mediaID, mediaURL, screenName, tweetBody)
                imageTweet += 1
        #ssm.put_parameter(Name='twitter-max-id',Type='String',Value=str(maxID),Overwrite=True)
        print("Queries done: %i. Tweets received: %i" % twitterS.get_statistics())
        print("Tweets with image: %i" % imageTweet)

    except TwitterSearchException as e: # take care of all those ugly errors if there are some
            print(e)

    return {
        "statusCode": 200,
        "body": json.dumps(
        {"message": "Poller"}
        ),
    }

def main():
  lambda_handler('','')
  
if __name__== "__main__":
  main()