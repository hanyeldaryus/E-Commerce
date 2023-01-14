from flask import redirect, request, url_for
from flask import Flask, session
from flask import render_template
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt #pip install passlib

from routes.config import * 
import src.loadkota as loadkota
loadkota.loadAll("data/kota.json")

def signin():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        print(username,password)
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', [username])
        # Fetch one record and return result
        user_data = cursor.fetchone()
        
        # If account exists in accounts table in out database
        if user_data:
            profile = {
            'username': user_data[0],
            'password': user_data[1],
            'name': user_data[2],
            'jenis_kelamin': user_data[3],
            'alamat': user_data[4],
            }
            if sha256_crypt.verify(password, profile['password']):
            # Create session data, we can access this data in other routes
                session['logged_in'] = True
                session['username'] =profile['username']
            # Redirect to home page
                return redirect(url_for('home'))
            else:
            # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username/password!'
                return render_template('login.html', msg=msg)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            return render_template('login.html', msg=msg)
    # Show the login form with message (if any)

    return render_template('login.html', msg=msg)


def register():
    listidkota = list(range(1, len(loadkota.getAll()) + 1))
    listkota = []
    msg=""
    for i in listidkota:
        kota = {
                'id': i,
                'nama': loadkota.search(i)['city_name']
        }
        listkota.append(kota)
    
    if request.method == 'GET':
        # profile['namakota'] = loadkota.search(profile['kotaID'])['city_name']

        return render_template("signup.html", listkota=listkota, msg=msg)

    else:
        nama = request.form['nama']
        username = request.form['username']
        password = request.form['password']
        password = sha256_crypt.encrypt(password)
        jenis_kelamin = request.form['jenis_kelamin']
        jalan = request.form['jalan']
        kotaId = request.form['kota']

        cur = mysql.connection.cursor()
        cur.execute("select count(*) from users where username=%s;",[username])
        count = cur.fetchone()[0]
        print(count)
        username_is_used = count > 0

        if username_is_used:
            msg = "Username is used! Please try different username..."
            return render_template("signup.html", listkota=listkota, msg=msg)

        else:
            cur.execute("CALL AddUser(%s,%s,%s,%s,%s,%s)",(username,password,nama,jenis_kelamin,jalan,kotaId))

            mysql.connection.commit()
            return redirect(url_for('start'))