from PIL import Image as image
from credentials.secrets import AwsSecrets
from database import S3FileManager
from datetime import datetime
from face_converter import tag_emoticon,pil_base64
from face_analyzer import FaceAnalyzer
from flask import Flask, request
from flask_cors import CORS
import boto3


app = Flask(__name__)
app.config.from_pyfile("credentials/s3_config.py")
CORS(app)

kSession = boto3.Session(AwsSecrets.kAccessKeyId, AwsSecrets.kSecret)

# todo: Delete this as we might not need to persist data with S3
kS3BucketName = "happy-coding"
kS3Manager = S3FileManager(kS3BucketName, kSession)


@app.route("/video", methods=["POST"])
def video():
    file_obj = request.files.get("file")
    print(file_obj)

    def make_unique_filename(extension=None):
        tail = "." + extension if extension else ""
        return f"file{datetime.utcnow()}{tail}"

    remote_filename = make_unique_filename()
    kS3Manager.upload(file_obj, remote_filename)

    # todo: Real processing logic and return result to the frontend.

    return {"code": 200, "message": "上传请求成功"}


@app.route("/photo", methods=["POST"])
def photo():
    summary = []
    photo_file = request.files.get("file")
    face_details = FaceAnalyzer(kSession).analyze_face_details(photo_file)["FaceDetails"]
    emotified_img = tag_emoticon(image.open(photo_file), face_details, summary)
    print(face_details)
    emotified_img.show()

    return {
        "code": 200,
        "faceDetails": summary,
        "img": pil_base64(emotified_img),
    }


if __name__ == "__main__":
    app.run(port=5233, debug=True)
