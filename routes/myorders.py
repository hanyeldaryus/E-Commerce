from flask import redirect, request, url_for
from flask import Flask, session
from flask import render_template
from flask_mysqldb import MySQL

from routes.config import * 
import src.loadkota as loadkota
loadkota.loadAll("data/kota.json")

@app.route('/myorders')
def my_orders():
    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM orders WHERE customerUsername=%s ORDER BY status, orderDate DESC', [username])
    data_orders = cur.fetchall()
    
    if data_orders:
        has_order = True
        my_orders = []
        for order in data_orders:
            my_order = {
                'order_id': order[0],
                'cust_username': order[1],
                'order_date': order[2],
                'payment_method':order[8],
                'status': order[10],
                'foto_thumbnail':'',
                'jumlah_produk': 0
            }
            cur.execute('SELECT productId FROM order_detail WHERE orderId=%s LIMIT 1', [my_order['order_id']])
            product_id_thumbnail = cur.fetchone()[0]
            #print(product_id_thumbnail)

            cur.execute('SELECT image_url FROM products WHERE productId=%s', [product_id_thumbnail])
            thumbnail_url = cur.fetchone()[0]
            #print(thumbnail_url)

            cur.execute('SELECT COUNT(*) FROM order_detail WHERE orderId=%s', [my_order['order_id']])
            jml_produk = cur.fetchone()[0]
            #print(jml_produk)

            my_order['foto_thumbnail'] = thumbnail_url
            my_order['jumlah_produk'] = jml_produk

            my_orders.append(my_order)
        
        return render_template("myorders.html", username=username, has_order=has_order, my_orders=my_orders)

    else:
        has_order = False
        return render_template("myorders.html", username=username, has_order=has_order)


@app.route('/myorders-detail/<order_id>', methods=['GET','POST'])
def myorders_detail(order_id):
    if request.method == 'GET':
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
            'total_payment': order[7],
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
        cur.execute('SELECT * FROM order_detail WHERE orderId=%s', [order_id])
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

            order_items.append(order_item)
        
        print(order_information)

        return render_template("myorders-detail.html", username=username, 
        informasi_pesanan=order_information, my_orders=order_items)
        

    else:
        username = session.get('username')
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM orders WHERE orderId=%s', [order_id])
        order = cur.fetchone()
       
        if order[1] == username:

            cur.execute('''
            UPDATE orders
            SET 
                status = 'Selesai',
                paid = 'True'
            WHERE orderId = %s;
            ''', [order_id])

            cur.execute('SELECT * FROM order_detail WHERE orderId=%s', [order_id])
            order_detail = cur.fetchall() 

            for item in order_detail:
                cur.execute('SELECT * FROM products WHERE productId = %s', [item[1]])
                product = cur.fetchone()

                username_seller = product[6]
        
                cur.execute('SELECT * FROM saldo WHERE username = %s', [username_seller])
                current_saldo = cur.fetchone()[1]

                saldo_baru = current_saldo + (product[5]*item[2])
               
                cur.execute('''
                UPDATE saldo
                set 
                saldo_ewallet = %s
                WHERE 
                username = %s''', (saldo_baru, username_seller))

            cur.close()
            mysql.connection.commit()

            return redirect(url_for('myorders_detail', order_id=order_id))

        else:
            #kalo customerUsername order tidak sama dengan username session
            return redirect(url_for('my_orders'))