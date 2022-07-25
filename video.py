import json
import tempfile
from os.path import exists

import imageio.v3 as iio
from werkzeug.datastructures import FileStorage

import credentials.secrets as secrets
from utils import g_sqs_client, g_rek_client


class VideoFaceDetectionError(Exception):
    pass


def _dump_error(sqs_response, filename_tail):
    path = f"venv/tmp/sqs_response_err_{filename_tail}.json"
    for msg in sqs_response["Messages"]:
        msg["Body"] = json.loads(msg["Body"])
        msg["Body"]["Message"] = json.loads(msg["Body"]["Message"])
    with open(path, "w") as err_file:
        json.dump(sqs_response, err_file)


def detect_faces(video_name):
    # todo: Rekognition wrapper instead of global variable.
    job_id = g_rek_client.start_face_detection(
        Video={"S3Object": {"Bucket": secrets.kBucketName, "Name": video_name}},
        NotificationChannel={"SNSTopicArn": secrets.kSnsTopicArn, "RoleArn": secrets.kRoleArn},
        FaceAttributes="ALL")["JobId"]
    while True:
        sqs_response = g_sqs_client.receive_message(
            QueueUrl=secrets.kSqsUrl,
            MessageAttributeNames=["ALL"],
            MaxNumberOfMessages=10)
        if "Messages" not in sqs_response: continue
        for msg in sqs_response["Messages"]:
            msg_body = json.loads(msg["Body"])
            job_result = json.loads(msg_body["Message"])
            if job_result["JobId"] != job_id: continue
            g_sqs_client.delete_message(QueueUrl=secrets.kSqsUrl, ReceiptHandle=msg["ReceiptHandle"])
            if job_result["Status"] == "SUCCEEDED":
                return g_rek_client.get_face_detection(JobId=job_id)
            _dump_error(sqs_response, job_id)
            raise VideoFaceDetectionError(f"<JobId={job_id}>")


class InMemVideoAdaptor:
    """FFMPEG does not support in-memory files, this wrapper lies to it."""

    def __init__(self, video: FileStorage):
        # Normalize the video to H.264 codec
        # FFMPEG doesn't seem to support in-mem conversion hence the maneuver with tempfile.
        buffer = tempfile.NamedTemporaryFile()
        buffer.write(video.read())
        buffer.seek(0)
        self._frames = iio.imread(buffer.name, plugin="FFMPEG", fps=18)
        self._video = tempfile.NamedTemporaryFile()
        iio.imwrite(self._video.name, self._frames, plugin="FFMPEG", fps=18)

    def video_from_start(self):
        self._video.seek(0)
        return self._video

    def frames(self):
        return self._frames


def normalize_video(video: FileStorage, fps=18) -> str:
    """Close the file on disposal."""
    # Normalize the video to H.264 codec
    # FFMPEG doesn't seem to support in-mem conversion hence the maneuver with tempfile.
    file = tempfile.NamedTemporaryFile(delete=False)
    file.write(video.read())
    file.close()
    frames = iio.imread(file.name, plugin="FFMPEG", fps=fps)
    iio.imwrite(file.name, frames, plugin="FFMPEG", fps=fps)
    return file.name, frames


def make_video_file(frames, fps=18) -> FileStorage:
    buffer = tempfile.NamedTemporaryFile()
    iio.imwrite(buffer.name, frames, plugin="FFMPEG", fps=fps)
    buffer.seek(0)
    return buffer


import moviepy.editor as mp
from moviepy.editor import VideoFileClip, AudioFileClip


def extract_audio(video_path, audio_path):
    my_clip = mp.VideoFileClip(video_path)
    if my_clip.audio:
        my_clip.audio.write_audiofile(audio_path)


# 视频添加音频
def video_add_audio(video_path, audio_path, out_video_path, fps):
    video = VideoFileClip(video_path)
    if exists(audio_path):
        videos = video.set_audio(AudioFileClip(audio_path))  # 音频文件
    else:
        videos = video
    videos.write_videofile(out_video_path, audio_codec='aac', fps=fps)  # 保存合成视频，注意加上参数audio_codec='aac'，否则音频无声音
