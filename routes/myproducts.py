from flask import redirect, request, url_for
from flask import Flask, session
from flask import render_template
from flask_mysqldb import MySQL

from routes.config import * 

@app.route('/myproducts')
def get_products():
    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE username=%s AND available='Yes' ", [username])
    user_products = cur.fetchall()    
    cur.execute('SELECT * FROM users WHERE username=%s', [username])
    user_data = cur.fetchone()

    if user_data:
        have_products = False
        profile = {
                'username': user_data[0],
                'nama': user_data[2],
                'jenis_kelamin': user_data[3],
                'alamat': user_data[4],
            }
        if user_products:
            have_products = True
            products = []
            for p in user_products:
                product = {
                    'productId': p[0],
                    'nama': p[1],
                    'kategori': p[2],
                    'kondisi': p[3],
                    'deskripsi': p[4],
                    'harga': p[5],
                    'username': p[6],
                    'image': p[7],
                    'stok': p[9],
                }
                products.append(product)

            return render_template("user-products.html", username = username , have_products = have_products, 
            profile = profile , products = products)
        else:
            msg = "You don't have any products"
            return render_template("user-products.html", username = username , have_products = have_products, 
            profile = profile, msg = msg)

    return redirect(url_for('home'))

#Route Update Product
@app.route('/myproducts/update', methods=['POST'])
def update_product():
    print(request.form)
    username = session.get('username')
    product_id = request.form['productId']
    nama = request.form['nama']
    kategori = request.form['kategori']
    kondisi = request.form['kondisi']
    deskripsi = request.form['deskripsi']
    harga = request.form['harga']
    image = request.form['image']
    stok = request.form['stok']
    cur = mysql.connection.cursor()
    cur.execute("CALL UpdateProductData(%s,%s,%s,%s,%s,%s,%s, NOW(),%s)",(product_id,nama,kategori,kondisi,deskripsi,harga,image, stok))
    mysql.connection.commit()
    return redirect(url_for('get_products'))

#Route Delete
@app.route('/myproducts/delete/<product_id>', methods=['GET'])
def delete_product(product_id):
    username = session.get('username')
    cur = mysql.connection.cursor()

    cur.execute("select username from products WHERE productId=%s", [product_id])
    username_target = cur.fetchone()[0]
    if username == username_target:
        cur.execute("CALL DeleteProduct(%s,%s)", (product_id, username))
        mysql.connection.commit()

    return redirect(url_for('get_products'))


@app.route('/myproducts/add', methods=['GET', 'POST'])
def addproduct():
    username = session.get('username')
    if request.method == 'GET':
        return render_template('addproduct.html' , username = username)
    else:
        nama = request.form['nama']
        kategori = request.form['kategori']
        kondisi = request.form['kondisi']
        deskripsi = request.form['deskripsi']
        harga = request.form['harga']
        username = session.get('username')
        image = request.form['image']
        stok = request.form['stok']
        cur = mysql.connection.cursor()

        username_check = cur.execute('SELECT * FROM users WHERE username = %s', [username])
        if username_check :
            cur.execute("CALL AddProduct(%s,%s,%s,%s,%s,%s,%s,%s)",(nama,kategori,kondisi,deskripsi,harga,username,image,stok))
            mysql.connection.commit()
            cur.close()
        else:
            return redirect(url_for('signin'))
        return redirect(url_for('get_products'))