from flask import Flask, url_for, flash, redirect, send_from_directory
from markupsafe import escape
from flask import request
from flask import render_template
import werkzeug
import os
import uuid
from dbModels import db, File

app = Flask(__name__)

app.config['SECRET_KEY'] = b'\x9e\xc3\x03\xbd\x90\x91*l\xb0}D<\xed\xc4l\xf9\x05`w\xabj\xc2\xcb9' #os.urandom(24)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # 5MB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        files = File.query.all()
        return render_template('index.html', files=files)

#クライアントの命名したファイル名を利用するためのsecure_filename()
from werkzeug.utils import secure_filename

@app.route('/admin', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'GET':
        files = File.query.all()
        return render_template('admin.html', files=files)

    else:
        if 'the_file' not in request.files:
            flash('ファイルが存在しません')
            return redirect(request.url)
        fileData = request.files["the_file"]
        if fileData.filename == '':
            flash('ファイルが選択されていません')
            return redirect(request.url)
        #任意の階層をフルパスで指定(macの場合。任意のユーザー名は変更してください。)
        if fileData and allowed_file(fileData.filename):
            #File Path
            file_uuid = str(uuid.uuid4())
            savename = file_uuid + secure_filename(fileData.filename)
            filepath = '/usr/src/app/uploads/' + savename
            fileData.save(filepath)
            #DBデータ保存
            filesize = os.stat(filepath).st_size
            #star = 0
            file_record = File(filename=savename, filesize=filesize)
            db.session.add(file_record)
            db.session.commit()
            files = File.query.all()
            #アップロードしてサーバーにファイルが保存されたらfinishedを表示
            return render_template('admin.html', fileurl=savename, files=files)
        else:
            flash('何らかのエラーが発生しました')
            return redirect(request.url)

@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def over_max_file_size(error):
    flash('ファイルサイズが大きすぎます')
    return redirect(request.url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('/usr/src/app/uploads/', filename)

@app.route('/delete/<int:id>')
def delete(id):
    file = File.query.filter_by(id=id).first()
    os.remove('/usr/src/app/uploads/' + file.filename)
    db.session.delete(file)
    db.session.commit()
    files = File.query.all()
    return render_template('admin.html', files=files)

if __name__ == '__main__':
    app.run()
