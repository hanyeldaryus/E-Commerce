from flask import redirect, request, url_for
from flask import Flask, session
from flask import render_template
from flask_mysqldb import MySQL

from routes.config import * 
import src.loadkota as loadkota
loadkota.loadAll("data/kota.json")

@app.route('/customer-orders')
def customer_orders():
    username = session.get('username')
    cur = mysql.connection.cursor()

    cur.execute('''SELECT * FROM orders WHERE orderId IN (SELECT DISTINCT orderId FROM order_detail WHERE
    productId IN (SELECT productId from products where username =%s)) ORDER BY status, orderDate DESC ''',[username])
    data_orders = cur.fetchall()
    
    if data_orders:
        has_order = True
        costumer_orders = []
        for order in data_orders:
            costumer_order = {
                'order_id': order[0],
                'cust_username': order[1],
                'order_date': order[2],
                'payment_method':order[8],
                'status': order[10],
                'foto_thumbnail':'',
                'jumlah_produk': 0
            }
            cur.execute(
            """
            SELECT productId FROM order_detail WHERE orderId=%s 
            AND productId IN (SELECT productId from products where username =%s) 
            LIMIT 1
            """, (costumer_order['order_id'],username))
            product_id_thumbnail = cur.fetchone()[0]
            #print(product_id_thumbnail)

            cur.execute('SELECT image_url FROM products WHERE productId=%s', [product_id_thumbnail])
            thumbnail_url = cur.fetchone()[0]
            #print(thumbnail_url)

            cur.execute('SELECT COUNT(*) FROM order_detail WHERE orderId=%s', [costumer_order['order_id']])
            jml_produk = cur.fetchone()[0]
            #print(jml_produk)

            costumer_order['foto_thumbnail'] = thumbnail_url
            costumer_order['jumlah_produk'] = jml_produk

            costumer_orders.append(costumer_order)
        
        return render_template("customer_orders.html", username=username, has_order=has_order, customer_orders=costumer_orders)

    else:
        has_order = False
        return render_template("customer_orders.html", username=username, has_order=has_order)

@app.route('/customer-orders-detail/<order_id>', methods=['GET'])
def customer_orders_detail(order_id):
    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM orders WHERE orderId=%s', [order_id])
    order = cur.fetchone()

    #buat nyimpen informasi order
    order_information = {
        'order_id' : order[0],
        'order_date': order[2],
        'kode_kurir': order[4],
        'kurir': '',
        'ship_address': order[5],
        'ship_cityId': order[6],
        'alamat_pengiriman': '',
        'total_payment': 0,
        'payment_method': order[8],
        'status': order[10],
    }

    #ambil kurir
    kode_kurir = order_information['kode_kurir']
    cur.execute('SELECT nama_kurir FROM kurir WHERE kode_kurir=%s', [kode_kurir])
    kurir = cur.fetchone()[0]
    order_information['kurir'] = kurir
    print(kurir)

    #ambil kota dan tulis alamat pengiriman
    kota = loadkota.search(order_information['ship_cityId'])['city_name']
    alamat = order_information['ship_address'] + ' ' + kota
    order_information['alamat_pengiriman'] = alamat
    print(alamat)

    order_items = []

    #ambil data tiap produk di order detail 
    #ditambah statement di where biar ambil data sesuai nama seller
    cur.execute('SELECT * FROM order_detail WHERE orderId=%s AND productId IN (SELECT productId from products WHERE username=%s)', (order_id, username))
    order_detail = cur.fetchall()
    for item in order_detail:

        product_id = item[1]
        cur.execute('SELECT nama, harga, username, image_url FROM products WHERE productId=%s', [product_id])
        product = cur.fetchone()

        username_seller = product[2]
        cur.execute('SELECT nama, idKota FROM users WHERE username=%s', [username_seller])
        seller = cur.fetchone()
        
        #buat nyimpen tiap produk di order detail
        order_item = {
            'nama': product[0],
            'harga': product[1],
            'nama_seller': seller[0],
            'kota_seller': loadkota.search(seller[1])['city_name'] ,
            'image_url': product[3],
            'jumlah': item[2],
            'total_harga': product[1] * item[2]
        } 

        order_information['total_payment'] += order_item['total_harga']

        order_items.append(order_item)
    
    print(order_information)

    return render_template("customer-orders-detail.html", username=username, 
	informasi_pesanan=order_information, my_orders=order_items, order_id=order_id)