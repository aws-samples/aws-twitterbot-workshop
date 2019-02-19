import boto3
import datetime
import time
import json
from botocore.vendored import requests
import tweepy
import logging
from PIL import Image
from io import BytesIO
#from aws_xray_sdk.core import xray_recorder
#from aws_xray_sdk.core import patch_all

# Get the service resource
#sqs = boto3.resource('sqs', region_name='us-west-2')
ssm = boto3.client('ssm', region_name='us-west-2')
reko = boto3.client('rekognition', region_name='us-west-2')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get the image to transform original one
MASK = Image.open("mask.png")
if MASK.mode != 'RGBA':
    MASK = MASK.convert('RGBA')

def authenticate_twitter():
    consumer_key = (ssm.get_parameter(Name='twitter-consumer-key', WithDecryption=True))['Parameter']['Value']
    consumer_secret = (ssm.get_parameter(Name='twitter-consumer-secret', WithDecryption=True))['Parameter']['Value']
    access_token = (ssm.get_parameter(Name='twitter-access-token', WithDecryption=True))['Parameter']['Value']
    access_token_secret = (ssm.get_parameter(Name='twitter-access-token-secret', WithDecryption=True))['Parameter']['Value']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return auth 


def get_faces(image):
    resp = reko.detect_faces(Image={'Bytes': image})
    if 'FaceDetails' in resp:
        return resp['FaceDetails']
    else:
        return []

def get_face_boxes(faces, source_size):
    # this list comprehension builds a bounding box around the faces
    return [
        (
            int(f['BoundingBox']['Left'] * source_size[0]),
            int(f['BoundingBox']['Top'] * source_size[1]),
            int((f['BoundingBox']['Left'] + f['BoundingBox']['Width']) * source_size[0]),
            int((f['BoundingBox']['Top'] + f['BoundingBox']['Height']) * source_size[1]),
            # we store the final coordinate of the bounding box as the pitch of the face
            f['Pose']['Roll']
        )
        for f in faces
    ]


def build_masked_image(source, mask, boxes):
    print "PutMask"
    for box in boxes:
        size = (box[2] - box[0], box[3] - box[1])
        scaled_mask = mask.rotate(-box[4], expand=1).resize(size, Image.ANTIALIAS)
        # we cut off the final element of the box because it's the rotation
        source.paste(scaled_mask, box[:4], scaled_mask)

def updateImage(faceDetails, imageSource):
    print "UpdateImage"
    boxes = get_face_boxes(faceDetails, imageSource.size)
    if boxes:
        build_masked_image(imageSource, MASK, boxes)
    else:
        return None
    return imageSource

def tweetImage(authent, imageProcessed):
    print "tweetImage"
    api = tweepy.API(authent)
    destination = '/tmp/image_out.jpeg'
    imageProcessed.save(destination, "JPEG", quality=80, optimize=True, progressive=True)
    upload_result = api.media_upload('/tmp/image_out.jpeg')
    api.update_status(status="Image updated with Ninja faces", media_ids=[upload_result.media_id_string])

def addidtolist(tweet_list, tweet_id):
    if tweet_list == 'null':
        tweet_list = tweet_id
        ssm.put_parameter(Name='day-tweet-processed', Type='StringList', Value=tweet_list, Overwrite=True)
    else:
        tweet_list = tweet_list + ',' + tweet_id
        ssm.put_parameter(Name='day-tweet-processed', Type='StringList', Value=tweet_list, Overwrite=True)
    print 'New list: ' + tweet_list
    return tweet_list

def idinlist(t_list, idcheck):
    words = t_list.split(',')

    for word in words:
        if idcheck == word:
            return True
        print word
    return False


def process_messages(auth, eventReceived):
    count = 0
    imageWithFaces = 0

    for message in eventReceived['Records']:
        # Print out the body and tweet id
        body = message['body']
        print 'message body {}'.format(body)
        step_0 = body.split(' ')
        tweet_id = step_0[0]
        mediaURL = step_0[1]
        print "url: " + mediaURL
        step_1 = tweet_id.split('@')
        t_id = step_1[1]
        step_2 = t_id.split(':')
        t_id = step_2[0]
        print "tweetID: " + t_id
        
        # Check if tweet has been already processed
        t_list = (ssm.get_parameter(Name='day-tweet-processed'))['Parameter']['Value']
        print "Liste: " + t_list
        check = idinlist(t_list, t_id)
        print "Check value: " + str(check)
        
        if(check != True):
            print "Go to tweet if faces present"
            # Gather the image and check if faces are present
            count = count + 1
            logger.info("Count: %i" % count)
            respImage = requests.get(mediaURL+":large")
            faceDetails = get_faces(respImage.content)
            logger.info(faceDetails)
            img = Image.open(BytesIO(respImage.content))
            addidtolist(t_list, t_id)
            if len(faceDetails) == 0:
                print "No faces in the image" 
            else:
                imageWithFaces += 1   
                processed = updateImage(faceDetails, img)
                tweetImage(auth, processed)

    return imageWithFaces

def lambda_handler(event, context):
    try:
        #patch_all()
        authTwitter = authenticate_twitter()

        nbofImageFaces = process_messages(authTwitter, event)
        logger.info("Images with Faces: " + str(nbofImageFaces))
    except Exception as e: # take care of all those ugly errors if there are some
        print(e)

    return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "Update Image on twitter"}
            ),
        }  