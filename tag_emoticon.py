import base64
from io import BytesIO

import PIL
from PIL.Image import Image


def pil_base64(image):
    img_buffer = BytesIO()
    image.save(img_buffer, format='PNG')
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode("utf-8")
    return base64_str


def tag_emoticon(img: Image, face_details, summary) -> Image:
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

        xx = {'age': age,
              'male': male,
              'emotion': emotion,
              'bearded': bearded,
              'img': "data:image/png;base64,"+pil_base64(emoji_img)
              }
        summary.append(xx)

    return img
