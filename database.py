from boto3 import Session


class S3FileManager:
    def __init__(self, bucket_name, aws_access_key_id, aws_secret_access_key):
        self._bucket_name = bucket_name
        self._s3_client = Session(aws_access_key_id, aws_secret_access_key).client('s3')

    def upload_by_name(self, local_filename, remote_filename=None):
        if remote_filename is None: remote_filename = local_filename
        self._s3_client.upload_file(local_filename, self._bucket_name, remote_filename)

    def upload(self, data, remote_filename):
        self._s3_client.upload_fileobj(data, self._bucket_name, remote_filename)

    def download_by_name(self, remote_filename, local_filename):
        self._s3_client.download_file(self._bucket_name, remote_filename, local_filename)
