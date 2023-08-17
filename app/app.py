from flask import Flask, url_for, flash, redirect, send_from_directory
from markupsafe import escape
from flask import request
from flask import render_template
import werkzeug
import pdf2image
from flask_paginate import Pagination, get_page_parameter
import os
import sqlite3
import shutil
import pathlib
import glob
import uuid
from dbModels import db, File
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app,
    supports_credentials=True)

app.config['SECRET_KEY'] = b'\x9e\xc3\x03\xbd\x90\x91*l\xb0}D<\xed\xc4l\xf9\x05`w\xabj\xc2\xcb9' #os.urandom(24)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shower.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#con = sqlite3.connect('shower.db')
#cur = con.cursor()
#cur.execute('select * from file')

#results = cur.fetchall()

#cur.close()
#con.close()

def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        files = File.query.all()

        # pagenation
        page = request.args.get(get_page_parameter(), type=int, default=1)
        res = files[(page - 1)*9: page*9]
        pagination = Pagination(page=page, total=len(files),  per_page=9)
        
        return render_template('index.html', files=files, pagination=pagination, css_framework='foundation')

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

        theme = request.form["theme"]
        if theme == '':
            flash('テーマの記入を記入してください')
            return redirect(request.url)

        author = request.form["author"]
        if not request.form["author"]:
            flash('authorを記入してください')
            return redirect(request.url)

        #任意の階層をフルパスで指定(macの場合。任意のユーザー名は変更してください。)
        if fileData and allowed_file(fileData.filename):
            #File Path
            file_uuid = str(uuid.uuid4())
# uploadしたときに.が消えることがあったのでコメントアウト
#            savename = file_uuid + secure_filename(fileData.filename)
            savename = file_uuid + fileData.filename
            filepath = '/usr/src/app/uploads/' + savename
            fileData.save(filepath)

            #pdf to images
            images = pdf2image.convert_from_path(filepath, grayscale=False, size=800)
            fdir = '/usr/src/app/uploads/images/' + savename
            if os.path.exists(fdir) == False:
                os.makedirs(fdir)
                for index, image in enumerate(images):
                    image.save(fdir + '/' + savename +"-"+ str(index+1) + '.png')
            # imgの枚数を確認
            imgnum = len(glob.glob( fdir + '/*'))
            #DBデータ保存
            filesize = os.stat(filepath).st_size
            #star = 0
            file_record = File(filename=savename, filesize=filesize, theme=theme, author=author, stars=0, imgnum=imgnum)
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

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/images/<path:path>')
def send_img(path):
    return send_from_directory('/usr/src/app/uploads/images/', path=path)

@app.route('/imgnum/<filename>')
def img_num(filename):
    return str(len(glob.glob('/usr/src/app/uploads/images/' + filename + '/*')))

@app.route('/carousel/<int:id>')
def carousel(id):
    file = File.query.filter_by(id=id).first()
    images = glob.glob('/usr/src/app/uploads/images/' + file.filename + '/*')
    return render_template('slider.html', file=file, images=images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('/usr/src/app/uploads/', filename)

@app.route('/delete/<int:id>')
def delete(id):
    file = File.query.filter_by(id=id).first()
    os.remove('/usr/src/app/uploads/' + file.filename)
    shutil.rmtree('/usr/src/app/uploads/images/' + file.filename)
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for("upload_file"))

@app.route('/like/<int:id>')
def like(id):
    likes = File.query.filter_by(id=id).first()
    likes.stars = likes.stars + 1
    db.session.commit()
    return str(likes.stars)
    # redirect
#    file = File.query.filter_by(id=id).first()
#    images = glob.glob('/usr/src/app/uploads/images/' + file.filename + '/*')
#    return render_template('slider.html', file=file, images=images)

@app.route('/pdf2Images/<int:id>')
def pdf2Images(id):
    file = File.query.filter_by(id=id).first()
    images = pdf2image.convert_from_path('/usr/src/app/uploads/' + file.filename, grayscale=True, size=1000)
    fdir = '/usr/src/app/uploads/images/' + file.filename
    if os.path.exists(fdir) == False:
        os.makedirs(fdir)
        for index, image in enumerate(images):
           image.save(fdir + '/' + file.filename +"-"+ str(index+1) + '.png')
    return redirect(url_for("upload_file"))

if __name__ == '__main__':
    app.run()
