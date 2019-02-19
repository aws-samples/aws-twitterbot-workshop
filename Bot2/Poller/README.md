# Poller

## Steps

1. Look at the 2 lambda functions code available in this repository.
2. Get the lambda code
3. Let's create a folder with the different libraries described in requirements.txt
```bash
pip install -r requirements.txt -t build/
cp twitterPoller.py build/
```
4. Create zip file for our lambdas with all the libraries needed and the code source:
```bash
cd build/
zip -r twitterPoller.zip .
```
5. Create a lambda function from scratch
6. Upload the zip file for the lambda
7. Create a new IAM role with the following rights: Lambda Basic Execution, add also inline policies as provided in the folder [policies](../IAM_policies/) for SQS, KMS and SSM rights.
8. Configure 2 environment variables: 
    - sqsMessage to let lambda knows which queue to send messages to, put the value to an existing sqs Queue created in the previous steps.
    - DateOfLastTweet
9. Create a test event, empty to test your function.
10. If everything is ok, you could create a CloudWatch event trigger with a frequency of 5 mins

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
