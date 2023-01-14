from flask import redirect, request, url_for
from flask import Flask, session
from flask import render_template
from flask_mysqldb import MySQL

from routes.config import * 

@app.route('/cart')
def cart():
    if not session.get('logged_in'):
        return redirect(url_for('signin'))

    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cart WHERE username=%s", [username])
    cart_data = cur.fetchall()
    cur.execute("SELECT nama FROM users WHERE username=%s", [username])
    name = cur.fetchone()[0]

    remove_status = ''
    if session.get('remove_from_cart_success') == 'success':
        remove_status = 'success'
        session['remove_from_cart_success'] = ''
    elif session.get('remove_from_cart_success') == 'failed':
        remove_status = 'failed'
        session['remove_from_cart_success'] = ''
    
    if cart_data:
        cart_items = []
        cartinfo = {
            'total_price': 0,
            'total_shipping': 25000,
            'total_payment': 0,
        }
        for item in cart_data:
            product_id = item[1]
            cur.execute("SELECT * FROM products WHERE productId=%s", [product_id])
            p = cur.fetchone()
            cart_item = {
                    'productId': p[0],
                    'nama': p[1],
                    'kategori': p[2],
                    'kondisi': p[3],
                    'harga': p[5],
                    'username': p[6],
                    'image': p[7],
                    'jumlah': item[2],
                    'total_harga': item[2] * p[5]
                }
            cartinfo['total_price'] += cart_item['total_harga']
            cart_items.append(cart_item)
        
        cartinfo['total_payment'] = cartinfo['total_price'] + cartinfo['total_shipping']

        return render_template("cart.html", username=username, name=name 
        ,cart_items=cart_items, cartinfo=cartinfo, remove_status=remove_status)
    else:
        msg = "Keranjang belanja anda masih kosong"
        return render_template("cart.html",username=username, name=name, 
        msg=msg, remove_status=remove_status )


@app.route('/cart/add/<product_id>', methods=['GET'])
def add_to_cart(product_id):

    if not session.get('logged_in'):
        return redirect(url_for('signin'))

    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute("CALL AddToCart(%s,%s)", (username, product_id))
    status = cur.fetchone()
    cur.close()
    mysql.connection.commit()
    
    status = status[0]
    
    if status != 0:
        session['add_to_cart_success'] = 'success'
    else:
        session['add_to_cart_success'] = 'failed'

    return redirect(url_for('productdetail', product_id=product_id))

@app.route('/cart/delete/<product_id>', methods=['GET'])
def remove_from_cart(product_id):

    if not session.get('logged_in'):
        return redirect(url_for('signin'))

    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute("CALL RemoveFromCart(%s,%s)", (username, product_id))
    status = cur.fetchone()
    cur.close()
    mysql.connection.commit()
    
    status = status[0]
    
    
    if status != 0:
        session['remove_from_cart_success'] = 'success'
    else:
        session['remove_from_cart_success'] = 'failed'
    

    return redirect(url_for('cart'))