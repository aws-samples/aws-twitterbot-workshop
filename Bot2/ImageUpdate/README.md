# ImageUpdater

## Steps

1. Reuse or create an S3 bucket to host your code package
2. Look at the Lambda code in this repository
3. Create the lambda package
    1. Use SAM and init a project
    ```sam init --runtime python2.7```
    2. Update template.yaml with the one in this repository
    3. Copy/paste the code in a file twitterUpdateImage.py
    4. Update the code with the name of the SSM variables
    5. Update requirements.txt with needed libraries (sample provided in this repository)
    6. ```pip install -r requirements.txt -t build/```
    7. Get the pillow.zip archive in the folder upper and decompress it in your build/ folder to have pillow. \ 
    (The library is used to manipulate images.
    8. Copy your python file in build folder: \ 
    ```cp hello_world/*.py build/```
    
4. Package the Lambda and put it in your s3 bucket for deployment: \
```sam package --template-file template.yaml --output-template-file bot2-packaged.yaml --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME```
5. Deploy the lambda with a proper stack name and enable IAM capability to create roles automatically \
```sam deploy --template-file packaged.yaml --stack-name bot2-imageupdate --capabilities CAPABILITY_IAM```
6. Create a new IAM role with the following rights: Lambda Basic Execution, add also inline policies as provided in the folder [policies](../IAM_policies/) for SQS, Rekognition, KMS and SSM rights and replace the one generated automatically.
7. Go to the Lambda Console, configure the trigger of the Lambda to be Amazon SQS on the queue defined in the Poller.
8. Create a test event to check everything is ok. Click on Test at the top of the page. Let the value as it is and give a name. Test. If you have errors with module import, please check the following:
    1. What is the name of your main python file (app.py or else)
    2. Check if the template.yaml the name of the Handler align the first part to the name of your python file ```Handler: twitterUpdateImage.lambda_handler```
    3. Check the codeURI: the start point is where your template.yaml resides. ```CodeUri: build/```
    4. Make the appropriate updates and do again steps 3 and 4 and check if 6 is still there.
    5. Redo the test
9. Create a tweet with the keyword #AWSNinja or the one you want if you udpated it
10. Let's tweet with an image and the keyword chosen.
11. After processing, you should have a new tweet with the image updated.


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
