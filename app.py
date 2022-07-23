import boto3
from PIL import Image
from credentials.secrets import AwsSecrets
from flask import Flask, request
from flask_cors import CORS

from database import S3FileManager
from rekognition_adaptor import RekognitionAdaptor
from tag_emoticon import tag_emoticon, pil_base64

app = Flask(__name__)
CORS(app)

kSession = boto3.Session(AwsSecrets.kAccessKeyId, AwsSecrets.kSecret)

# todo: Delete this as we might not need to persist data with S3
kS3BucketName = "happy-coding"
kS3Manager = S3FileManager(kS3BucketName, kSession)


@app.route("/video", methods=["POST"])
def video():
    file_obj = request.files.get("file")
    print(file_obj)

    return {"code": 200, "message": "上传请求成功"}


@app.route("/photo", methods=["POST"])
def photo():
    summary = []
    photo_file = request.files.get("file")
    face_details = RekognitionAdaptor(kSession).find_face_details(photo_file)["FaceDetails"]
    emotified_img = tag_emoticon(Image.open(photo_file), face_details, summary)
    print(face_details)
    # emotified_img.show()

    return {
        "code": 200,
        "faceDetails": summary,
        "img": pil_base64(emotified_img),
    }


if __name__ == "__main__":
    app.run(port=5233, debug=True)
