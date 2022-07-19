from datetime import datetime
from flask import Flask, request
from flask_cors import CORS

from credentials.s3_config import S3_BUCKET_NAME, S3_KEY, S3_SECRET
from database import S3FileManager

app = Flask(__name__)
app.config.from_pyfile('credentials/s3_config.py')
CORS(app)
s3_manager = S3FileManager(S3_BUCKET_NAME, S3_KEY, S3_SECRET)


def make_unique_filename(extension=None):
    tail = '.' + extension if extension else ''
    return f'file{datetime.utcnow()}{tail}'


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/video', methods=["POST"])
def video():
    fileObj = request.files.get("file")
    print(fileObj)

    remote_filename = make_unique_filename()
    s3_manager.upload(fileObj, remote_filename)

    # todo: Real processing logic and return result to the frontend.

    return {"code": 200, "message": "上传请求成功"}


@app.route('/photo', methods=["POST"])
def photo():
    files = request.files.get("file")
    print(files)
    s3_manager.upload(files, make_unique_filename("jpeg"))

    # todo: Real processing logic and return result to the frontend.

    return {"code": 200, "message": "上传请求成功"}


if __name__ == '__main__':
    app.run(port=5233, debug=True)
