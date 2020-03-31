
### S3 Bucket ###
# Things to consider:
#  - file name: uuid/normal/user_id
#  - if there is changes to file name, need to process dl_link to return original filename
import boto3

s3_access_key_id = "AKIA4YHNNVAJLVVKOE52"
s3_secret_access_key = "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"
s3_resource = boto3.resource('s3', aws_access_key_id = s3_access_key_id, aws_secret_access_key = s3_secret_access_key)
bucket_name = "elasticbeanstalk-us-west-2-876671248402"
bucket_region = "us-west-2"
bucket = s3_resource.Bucket(bucket_name)
# S3 Helper Functions
def s3_upload_file(file_name, file_content):
    bucket.upload_fileobj(file_content, file_name, ExtraArgs={'ACL':'public-read'})

# Return the href to put into html for downloading
def s3_download_file(file_name):
    # https://elasticbeanstalk-us-west-2-876671248402.s3-us-west-2.amazonaws.com/test.txt
    return "https://{}.s3-{}.amazonaws.com/{}".format(bucket_name, bucket_region, file_name)

def main():
    s3_upload_file("test.txt", open("test.txt", "rb"))
    print(s3_download_file("test.txt"))

if __name__ == "__main__":
    main()