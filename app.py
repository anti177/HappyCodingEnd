from collections import defaultdict

import imageio.v3
import numpy
from PIL import Image
from flask import Flask, request
from flask_cors import CORS

import credentials.secrets as secrets
from tag_emoticon import tag_emoticon, pil_base64
from utils import timestamp_str, g_s3_client, g_rek_client
from video import detect_faces, extract_audio, video_add_audio

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello():
    return "Hi. The Happy-coding team is healthy!"


@app.route("/video", methods=["POST"])
def handle_video():
    tail = timestamp_str()
    video_name = f"original_{tail}.mp4"
    audio_name = f"audio_{tail}.mp3"
    video = request.files.get("file")
    video.save(video_name)

    extract_audio(video_name, audio_name)

    # Upload original video
    g_s3_client.upload_file(video_name, secrets.kBucketName, video_name)

    # Tag emoticons
    # todo: Is framerate fixed?
    detection_result = detect_faces(video_name)
    faces = detection_result["Faces"]
    meta = detection_result["VideoMetadata"]
    framerate = float(meta["FrameRate"])

    age_sum = 0
    emotions = defaultdict(int)
    frames = []
    faces_in_frame = []
    for i, frame in enumerate(imageio.v3.imiter(video_name, plugin="FFMPEG")):
        timestamp = i * 1000 / framerate
        tmp = [x["Face"] for x in faces if timestamp <= float(x["Timestamp"]) < (timestamp + 1000 / framerate)]
        if len(tmp) != 0: faces_in_frame = tmp
        summary = []
        tagged_img = tag_emoticon(Image.fromarray(frame), faces_in_frame, summary)
        frames.append(numpy.asarray(tagged_img))
        for x in summary:
            age_sum += int(x["age"][:x["age"].find('-')])
            emotions[x["emotion"]] += 1

    quiet_video_name = f"quiet_{tail}.mp4"
    final_video_name = f"processed_{tail}.mp4"
    imageio.v3.imwrite(quiet_video_name, frames, plugin="FFMPEG")
    video_add_audio(quiet_video_name, audio_name, final_video_name, framerate)

    g_s3_client.upload_file(final_video_name, secrets.kBucketName, final_video_name, ExtraArgs={'ACL': 'public-read'})

    return {
        "code": 200,
        "message": "上传视频请求成功",
        "url": f"https://{secrets.kBucketName}.s3.amazonaws.com/{final_video_name}",
        "summary": [{
            "age": round(age_sum / len(frames), 2),
            "happy": round(emotions["happy"] / len(frames) * 100, 2),
            "sad": round(emotions["sad"] / len(frames) * 100, 2),
            "calm": round(emotions["calm"] / len(frames) * 100, 2),
            "surprised": round(emotions["surprised"] / len(frames) * 100, 2),
            "disgusted": round(emotions["disgusted"] / len(frames) * 100, 2),
            "confused": round(emotions["confused"] / len(frames) * 100, 2),
            "angry": round(emotions["angry"] / len(frames) * 100, 2)
        }],
    }


@app.route("/photo", methods=["POST"])
def handle_photo():
    photo_file = request.files.get("file")
    face_details = g_rek_client.detect_faces(Image={"Bytes": photo_file.read()}, Attributes=["ALL"])["FaceDetails"]

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
