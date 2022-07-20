from boto3 import Session
from typing import Dict


class FaceAnalyzer:
	def __init__(self, aws_session: Session):
		self._client = aws_session.client("rekognition", region_name="us-east-1")

	def analyze_face_details(self, img_file) -> Dict:
		"""
		Analyzes the PIL.Image object, and return the analysis report in a dictionary.
		Refer to [this site](https://docs.aws.amazon.com/rekognition/latest/APIReference/API_DetectFaces.html)
		for the schema of the result.

		`img_file` must be an "rb" file.

		Note that the face details are in result["FaceDetails"].
		"""

		img_bytes = img_file.read()
		img_file.seek(0)
		return self._client.detect_faces(Image={'Bytes': img_bytes}, Attributes=["ALL"])
