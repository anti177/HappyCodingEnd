import base64
import json
from io import BytesIO

import PIL
import imageio
import numpy
from PIL import Image

from video import extract_audio, video_add_audio


def pil_base64(image):
    img_buffer = BytesIO()
    image.save(img_buffer, format='PNG')
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode("utf-8")
    return base64_str


def tag_emoticon(img, face_details, summary):
    """Tag emoticons onto each face in the image. The list follows the schema defined by
    [Rekognition](https://docs.aws.amazon.com/rekognition/latest/APIReference/API_DetectFaces.html)."""

    for face_attributes in face_details:
        age = int(face_attributes["AgeRange"]["High"])
        male = (face_attributes["Gender"]["Value"] == "Male")
        emotion = face_attributes["Emotions"][0]["Type"].lower()
        bearded = face_attributes["Beard"]["Value"]
        box = face_attributes["BoundingBox"]

        assert age >= 0
        if male:
            tag = (
                "baby" if age < 4
                else "boy" if age < 16
                else "man" if age < 41
                else "oldman")
        else:
            tag = (
                "baby" if age < 4
                else "girl" if age < 16
                else "woman" if age < 41
                else "oldwoman")

        emoji_name = f"{tag}_{emotion}"
        if tag in ("man", "oldman") and not bearded:
            emoji_name += "_nobeard"

        left = int(img.width * box["Left"])
        top = int(img.height * box["Top"])
        width = int(img.width * box["Width"])
        height = int(img.height * box["Height"])

        emoji_img = PIL.Image.open(f"static/emoji/{emotion}/{emoji_name}.png").resize((width, height))
        img.paste(emoji_img, (left, top, left + width, top + height))

        xx = {
            "age": age,
            "male": male,
            "emotion": emotion,
            "bearded": bearded,
            "img": "data:image/png;base64," + pil_base64(emoji_img)
        }

        summary.append(xx)

    return img


if __name__ == '__main__':
    video_name = "original_1658641778681637.mp4"
    audio_name = "original_1658641778681637.mp3"
    extract_audio(video_name, audio_name)
    with open("venv/tmp/rek_face_demo.json", "r") as demo_data:
        detection_result = json.load(demo_data)
    faces = detection_result["Faces"]
    meta = detection_result["VideoMetadata"]
    framerate = float(meta["FrameRate"])
    frames = []
    p = 0
    faces_in_frame = []
    for i, frame in enumerate(imageio.v3.imiter(video_name, plugin="FFMPEG")):
        timestamp = i * 1000 / framerate
        tmp = [x["Face"] for x in faces if timestamp <= float(x["Timestamp"]) < (timestamp + 1000 / framerate)]
        if len(tmp) != 0: faces_in_frame = tmp
        tagged_img = tag_emoticon(Image.fromarray(frame), faces_in_frame, [])
        frames.append(numpy.asarray(tagged_img))
    new_video_name = f"processed_test.mp4"
    imageio.v3.imwrite(new_video_name, frames, plugin="FFMPEG", fps=framerate)
    video_add_audio(new_video_name, audio_name, "with_audio.mp4", framerate)
