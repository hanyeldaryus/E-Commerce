from flask import redirect, request, url_for
from flask import Flask, session
from flask import render_template
from flask_mysqldb import MySQL

from routes.config import * 
import src.loadkota as loadkota
loadkota.loadAll("data/kota.json")
import src.rajaongkir as rajaongkir

@app.route('/order-detail', methods=['GET','POST'])
def order_detail():
    
    if request.method == "GET":
        if not session.get('logged_in'):
            return redirect(url_for('signin'))
        
        username = session.get('username')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cart WHERE username=%s", [username])
        cart_data = cur.fetchall()
        cur.execute("SELECT nama FROM users WHERE username=%s", [username])
        name = cur.fetchone()[0]
        cur.execute("SELECT * from kurir")
        datakurir = cur.fetchall()
        listkurir = []
        for k in datakurir:
            kurir = {
                'kode': k[0],
                'nama': k[1]
            }
            listkurir.append(kurir)

        if cart_data:
            cart_items = []
            orderinfo = {
                'total_price': 0,
                'total_shipping': 0,
                'total_payment': 0,
            }
            for item in cart_data:
                product_id = item[1]
                cur.execute("SELECT * FROM products WHERE productId=%s", [product_id])
                p = cur.fetchone()
                
                cur.execute("SELECT products.username, users.idKota  FROM cart INNER JOIN products ON cart.productId=products.productId INNER JOIN users ON users.username=products.username WHERE cart.username =%s", [username])
                sellerData = cur.fetchone()
                
                cart_item = {
                    'productId': p[0],
                    'nama': p[1],
                    'kategori': p[2],
                    'kondisi': p[3],
                    'harga': p[5],
                    'username': p[6],
                    'image': p[7],
                    'jumlah': item[2],
                    'total_harga': item[2] * p[5],
                    'pengirim': sellerData[0],
                    'alamatpengirim': loadkota.search(sellerData[1])['city_name']
                }
                orderinfo['total_price'] += cart_item['total_harga']
                cart_items.append(cart_item)


            cur.execute("SELECT idKota FROM users WHERE username =%s", [username])
            kotaIduser = cur.fetchone()[0]
            cur.execute("SELECT jalan FROM users WHERE username =%s", [username])
            alamatUSer = cur.fetchone()[0]

            kotaUser = alamatUSer + " " + loadkota.search(kotaIduser)['city_name']

            kurir_pilihan = session.get('kurir')
            session['kurir_temp'] = kurir_pilihan
            
            kurir = {
                    'kode': '',
                    'nama': ''
                    }
            if kurir_pilihan != '':
                cur.execute("SELECT * FROM kurir WHERE kode_kurir=%s", [kurir_pilihan])
                k = cur.fetchone()
                if k:
                    kurir = {
                    'kode': k[0],
                    'nama': k[1]
                    }
                    session['kurir'] = ''

            ongkir = session.get('ongkir')
            session['ongkir'] = 0

            if ongkir is not None:
                if ongkir > 0:
                    orderinfo['total_shipping'] = ongkir
            
            orderinfo['total_payment'] = orderinfo['total_price'] + orderinfo['total_shipping']
            session['order_info'] = orderinfo

            return render_template("order-detail.html", username=username, name=name 
            ,cart_items=cart_items, orderinfo=orderinfo, kurir=kurir, listkurir=listkurir, kotaUser=kotaUser)

        else:
            msg = "Keranjang belanja anda masih kosong"
            return render_template("order-detail.html",username=username, name=name, 
            msg=msg )
    
    else: #order-detail/shipment jadinya disini aja ya pake method POST
        username = session.get('username')
        cur = mysql.connection.cursor()
        cur.execute("SELECT products.username, users.idKota  FROM cart INNER JOIN products ON cart.productId=products.productId INNER JOIN users ON users.username=products.username WHERE cart.username =%s", [username])
        sellerData = cur.fetchone()

        cur.execute("SELECT idKota FROM users WHERE username =%s", [username])
        kotaIduser = cur.fetchone()

        # while True:
        #     try:
        #         totalOngkir = rajaongkir.cekOngkir(sellerData[1], kotaIduser[0], kurir);
        #     except:
        #         continue
        #     else:
        #         #the rest of the code
        #         session['ongkir'] = totalOngkir['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value']
        #         break
        # return redirect(url_for('order_detail'))

        kurir = request.form['pilihkurir']
        session['kurir'] = kurir

        while True:
            try:
                totalOngkir = rajaongkir.cekOngkir(sellerData[1], kotaIduser[0], kurir);
            except:
                continue
            else:
                session['ongkir'] = totalOngkir['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value']
                break
        return redirect(url_for('order_detail'))

        # totalOngkir = rajaongkir.cekOngkir(sellerData[1], kotaIduser[0], kurir)
        # session['ongkir'] = totalOngkir['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value']
        # return redirect(url_for('order_detail'))