# Manage your twitter credentials in AWS

## Overview

During the first steps, you enabled your twitter developer account and created your first app.
This app allowed you to have 4 credentials which will be used to interact with Twitter API.
As we want to use these credentials in the bot we are building, we could store in many ways:
1. Put it in the environment variables of your Lambda function
2. Put it in a share parameters management tools a.k.a AWS Systems Manager - Parameter Store
3. Put it in a AWS Secrets Manager

During this session, we will leverage AWS Systems Manager as we have multiple parameters beyond the API keys for twitter.

## Steps

1. Gather the twitter credentials, generated in the pre requisites, you have 4 keys to store.
2. Go to [AWS Key Management Service (KMS)](https://us-west-2.console.aws.amazon.com/kms/home?region=us-west-2#/kms/home)
2. Create a KMS key that we will use to encrypt the twitter credentials
3. Go to [AWS Systems Manager](https://us-west-2.console.aws.amazon.com/systems-manager/parameters/?region=us-west-2) 
4. Create the following parameters as Secure String and choose your KMS key, put the value of your twitter credentials in each of it.
    - twitter-access-token
    - twitter-access-token-secret
    - twitter-consumer-key
    - twitter-consumer-secret
5. Only for Bot 2, create additional parameters not encrypted, these will be used in the lambdas:
    - twitter-max-id as String, put '' as value.
    - day-tweet-processed as StringList

