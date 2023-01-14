from urllib import response
from flask import redirect, request, url_for
from flask import Flask, session, flash
from flask import render_template
from flask_mysqldb import MySQL
import MySQLdb.cursors
from passlib.hash import sha256_crypt  # pip install passlib
from werkzeug.utils import secure_filename
from routes.config import *
import src.loadkota as loadkota
loadkota.loadAll("data/kota.json")

# Route ke profile page


@app.route('/profile', methods=['GET'])
def get_profile():
    username = session.get('username')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", [username])
    user_data = cur.fetchone()
    cur.close()
    # TODO : get data from database
    if user_data:
        profile = {
            'username': user_data[0],
            'name': user_data[2],
            'jenis_kelamin': user_data[3],
            'jalan': user_data[4],
            'kotaID': user_data[5],
            'namakota': "",
            'profile_pic': user_data[6]
        }
        # set nama kota disini
        profile['namakota'] = loadkota.search(profile['kotaID'])['city_name']

        listidkota = list(range(1, len(loadkota.getAll()) + 1))
        listkota = []
        for i in listidkota:
            kota = {
                'id': i,
                'nama': loadkota.search(i)['city_name']
            }
            listkota.append(kota)

        return render_template("profile.html", profile=profile, username=username, listkota=listkota, filename="")
    else:
        return redirect(url_for('signin'))


# Route ke update profile
@app.route('/profile/update', methods=['POST'])
def update_profile():
    print(request.form)
    username = session.get('username')

    password = request.form['password']
    if password != '':
        password = sha256_crypt.encrypt(password)
    nama = request.form['name']
    jenis_kelamin = request.form['jenis_kelamin']
    jalan = request.form['jalan']
    kotaId = request.form['kotaID']
    # filenames = request.files['files']

    # uploaded_files = request.files.getlist("file[]")
    # filenames = []
    # for file in uploaded_files:
    #     if file and allowed_file(file.filename):
    #         filename = secure_filename(file.filename)
    #         file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    #         filenames.append(filename)
    #     cur = mysql.connection.cursor()
    #     cur.execute('INSERT INTO users(filename) VALUES (%s)',(filename))

    # # This line is essential, store the data in session
    # session['filenames'] = filenames

    cur = mysql.connection.cursor()
    cur.execute("CALL UpdateUserData(%s,%s,%s,%s,%s,%s)",
                (username, password, nama, jenis_kelamin, jalan, kotaId))
    mysql.connection.commit()
    return redirect(url_for('get_profile'))


UPLOAD_FOLDER = 'static/images/userpp'


@app.route('/profile/updateimage', methods=['POST'])
def update_image():
    username = session.get('username')

    if 'file' not in request.files:
        print('No file part')
        return redirect(url_for('get_profile'))

    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('get_profile'))
    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        ext = file.filename.split('.')[-1]
        filepath = '/static/images/userpp' + username + "." + ext

        file.save(os.path.join(
            app.config['UPLOAD_FOLDER'],  username + "." + ext))
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users set filename=%s where username=%s",
                    (filepath, username))
        mysql.connection.commit()
        return redirect(url_for('get_profile'))


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
