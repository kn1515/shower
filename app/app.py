from flask import Flask, url_for
from markupsafe import escape
from flask import request
from flask import render_template
app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/")
def index():
    return render_template('index.html')

#クライアントの命名したファイル名を利用するためのsecure_filename()
from werkzeug.utils import secure_filename

@app.route('/admin', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        fileData = request.files["the_file"]
        #任意の階層をフルパスで指定(macの場合。任意のユーザー名は変更してください。)
        fileData.save('/usr/src/app/uploads/' + secure_filename(f.filename))
        #アップロードしてサーバーにファイルが保存されたらfinishedを表示
        return render_template('finished.html')
    else:
    	#GETでアクセスされた時、uploadsを表示
    	return render_template('admin.html')

if __name__ == '__main__':
	app.run()
