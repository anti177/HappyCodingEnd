import numpy
from PIL import Image
from flask import Flask, request
from flask_cors import CORS

import credentials.secrets as secrets
from tag_emoticon import tag_emoticon, pil_base64
from utils import timestamp_str, g_s3_client, g_rek_client
from video import detect_faces, normalize_video, make_video_file

app = Flask(__name__)
CORS(app)


@app.route("/video", methods=["POST"])
def handle_video():
    norm_video_name, frames = normalize_video(request.files.get("file"))
    with open(norm_video_name, "rb") as video:
        video_short_name = f"video_{timestamp_str()}"
        remote_video_name = f"{video_short_name}.mp4"
        new_video_name = f"{video_short_name}_processed.mp4"

        g_s3_client.upload_fileobj(video, secrets.kBucketName, remote_video_name, ExtraArgs={'ACL': 'public-read'})

        face_details = detect_faces(remote_video_name)["Faces"]
        new_frames = []
        for i, f in enumerate(frames):
            new_img = tag_emoticon(Image.fromarray(f), face_details[i], [])
            new_frames.append(numpy.asarray(new_img))
        new_video = make_video_file(new_frames)
        g_s3_client.upload_fileobj(new_video, secrets.kBucketName, new_video_name, ExtraArgs={'ACL': 'public-read'})
        new_video.seek(0)

        return {
            "code": 200,
            "message": "上传视频请求成功",
            "summary": "todo",
            "resultUrl": f"https://{secrets.kBucketName}.s3.amazonaws.com/{new_video_name}",
        }


@app.route("/photo", methods=["POST"])
def handle_photo():
    photo_file = request.files.get("file")
    face_details = g_rek_client.detect_faces(Images={"Bytes": photo_file.read()}, Attributes=["ALL"])["FaceDetails"]

    summary = []
    photo_file.seek(0)
    new_img = tag_emoticon(Image.open(photo_file), face_details, summary)

    return {
        "code": 200,
        "message": "上传图片请求成功",
        "faceDetails": summary,
        "img": pil_base64(new_img),
    }


if __name__ == "__main__":
    app.run(port=5233, debug=True)
