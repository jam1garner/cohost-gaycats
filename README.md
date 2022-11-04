# gaycats cohost bot

A bot for posting images of cats to cohost regularly

## Runtime requirements

* python
    * python 3.10 or higher
    * pip requirements from requirements.txt

**Environment Variables**

* For cohost authentication:
    * `COHOST_EMAIL` - the email of the cohost account to log into
    * `COHOST_PASSWORD` - the password of the cohost account for logging in
    * `COHOST_USERNAME` - the username of the page to post to
* For alt text generation:
    * `AZURE_CV_SUBSCRIPTION_KEY` - azure subscription key for a computer vision instance
    * `AZURE_CV_ENDPOINT` - azure computer vision instance endpoint
