from boto3 import Session
from typing import Dict


class RekognitionAdaptor:
    def __init__(self, aws_session: Session, region_name="us-east-1"):
        self._client = aws_session.client("rekognition", region_name=region_name)

    def find_face_details(self, img) -> Dict:
        data = img.read()
        img.seek(0)
        return self._client.detect_faces(Image={'Bytes': data}, Attributes=["ALL"])
