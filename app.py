import os

import flask
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_files'
CORS(app)


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
