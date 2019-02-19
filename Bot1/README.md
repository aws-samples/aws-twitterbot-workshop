# twitterPollerRetweeter

You will find here the main files for the application:
hello_World/
  * twitterRetweet.py -- main file for code source
  * requirements.txt -- the list of the library needed

**NOTE**: It is recommended to use a Python Virtual environment to separate your application development from  your system Python installation.

**Bot 1: Make a bot who retweet automatically the tweets based on keywords**
1. Create an S3 bucket to host your code package
2. Create the lambda package
    1. Use SAM and init a project
```sam init --runtime python3.6```
    2. Update template.yaml with the one in this repository
    3. Copy/paste the code in app.py or create a new file with the code of this repository in folder hello_world
    4. Update app.py with the name of the SSM variables or reuse [twitterRetweet.py](./hello_world/twitterRetweet.py) in this repository
    5. Update [requirements.txt](./requirements.txt) with needed libraries (sample provided in this repository)
    6. In the hello_world directory, package code, first get the packages updated using pip3\
    ```pip3 install -r requirements.txt -t build/```\
    ```cp hello_world/*.py build/```
    
3. Package the Lambda and put it in your s3 bucket for deployment:\
```sam package --template-file template.yaml --output-template-file packaged.yaml --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME```
4. Deploy the lambda with a proper stack name and enable IAM capability to create roles automatically\
```sam deploy --template-file packaged.yaml --stack-name twitterpollerretweeter --capabilities CAPABILITY_IAM```
5. Let's update the rights in IAM role created for the Lambda and allow access to KMS, SSM parameters. check the samples in folder [policies](policies) to give access to SSM and KMS. 
  1. Look at the name of your IAM role assigned to Lambda
  2. Go to IAM, find the role of your Lambda
  3. Update the role, adding inline policies to the role based on the policies in the folder above.
6. Make sure the Trigger event of the lambda is configured with your poller event. Go to Lambda Console, put the trigger to Cloudwatch Events. Configure the Event with the rule created during the creation.
7. Create a test event if you want to test your lambda without waiting for the trigger
8. If you have errors with module import, please check the following:
    1. What is the name of your main python file (app.py or else)
    2. Check if the template.yaml the name of the Handler align the first part to the name of your python file ```Handler: twitterRetweet.lambda_handler```
    3. Check the codeURI: the start point is where your template.yaml resides. ```CodeUri: build/```
    4. Make the appropriate updates and do again steps 3 and 4 and check if 6 is still there.
    5. Redo the test
9. Check your twitter account and see the retweets
10. If you do some code update, copy code only in build folder and redo sam package and sam deploy

**We could instrument a bit this function to leverage X-Ray and understand where we are spending the time:**

Sample of instrumented function in the folder [instrumented_file](instrumented_file)

11. Enable tracing with X-ray. Could do in Lambda console or sam file.
12. Import X-ray sdk in your project
13. Patch_all() will help to patch all boto3 and managed libraries
14. Enable some sub-segment in the code if you want more details.


# Appendix

### Python Virtual environment
**In case you're new to this**, python3 comes with `virtualenv` library by default so you can simply run the following:

1. Create a new virtual environment
2. Install dependencies in the new virtual environment

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```


**NOTE:** You can find more information about Virtual Environment at [Python Official Docs here](https://docs.python.org/3/tutorial/venv.html). Alternatively, you may want to look at [Pipenv](https://github.com/pypa/pipenv) as the new way of setting up development workflows
## AWS CLI commands

AWS CLI commands to package, deploy and describe outputs defined within the cloudformation stack:

```bash
sam package \
    --template-file template.yaml \
    --output-template-file packaged.yaml \
    --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME

sam deploy \
    --template-file packaged.yaml \
    --stack-name twitterpollerretweeter \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides MyParameterSample=MySampleValue

aws cloudformation describe-stacks \
    --stack-name twitterpollerretweeter --query 'Stacks[].Outputs'
```
