from datetime import datetime
from flask import Flask, request
from flask_cors import CORS

from credentials.config import S3_BUCKET_NAME, S3_KEY, S3_SECRET
from database import S3FileManager

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)
s3_manager = S3FileManager(S3_BUCKET_NAME, S3_KEY, S3_SECRET)


def make_unique_filename(extension='txt'):
    return f'file{datetime.utcnow()}.{extension}'


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/video', methods=["POST"])
def video():
    fileObj = request.files.get("file")
    print(fileObj)

    #处理文件
    # TODO：

    #返回处理好的到前端
    # TODO：
    return {"code": 200, "message": "上传请求成功"}

@app.route('/photo', methods=["POST"])
def photo():
    fileObj = request.files.get("file")
    print(fileObj)

    #处理文件
    #TODO：

    #返回处理好的文件到前端
    #TODO：
    return {"code": 200, "message": "上传请求成功"}


if __name__ == '__main__':
    app.run(port=5233, debug=True)
