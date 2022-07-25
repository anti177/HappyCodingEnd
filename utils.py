from datetime import datetime

import boto3

import credentials.secrets as secrets


class RegionalSession:
    """Has convenient methods for working on AWS Sessions"""

    def __init__(self, access_key_id, access_key_secret, region):
        self._ssn = boto3.Session(access_key_id, access_key_secret)
        self._region = region

    def mk_client(self, service_name):
        return self._ssn.client(service_name, region_name=self._region)


def timestamp_str(now=None):
    if now is None: now = datetime.utcnow()
    # noinspection PyTypeChecker
    return str(int(now.timestamp() * 1e6))


g_ssn = RegionalSession(secrets.kAccessKeyId, secrets.kAccessKeySecret, secrets.kRegionName)
g_s3_client = g_ssn.mk_client("s3")
g_rek_client = g_ssn.mk_client("rekognition")
g_sqs_client = g_ssn.mk_client("sqs")
