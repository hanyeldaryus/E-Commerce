from flask import render_template, url_for, redirect, session, send_from_directory
import jinja2
import os
from src.filter import *
import src.loadkota as loadkota

from routes.config import *
import routes.auth
import routes.cart
import routes.config
import routes.customerorders
import routes.home
import routes.myorders
import routes.myproducts
import routes.orderdetail
import routes.payment
import routes.product
import routes.profile

# Custom template and filter
jinja2.filters.FILTERS['to_rupiah'] = to_rupiah

loadkota.loadAll("data/kota.json")

app.add_url_rule('/home', view_func=routes.home.home)
app.add_url_rule('/signup',methods=['GET','POST'], view_func=routes.auth.register)
app.add_url_rule('/login',methods=['GET','POST'], view_func=routes.auth.signin)
app.add_url_rule("/product-detail/<product_id>",methods=['GET','POST'], view_func=routes.product.productdetail)

# #Route Signup
# @app.route('/signup', methods=["GET", "POST"])

    
# #Route Signin    
# @app.route("/login", methods=['GET','POST'])

@app.route('/')
@app.route('/start')
def start():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect(url_for('home'))



# #Route ke profile page
# @app.route('/profile', methods=['GET'])
# def get_profile():
#     username = session.get('username')

#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM users WHERE username=%s", [username])
#     user_data = cur.fetchone()
#     cur.close()
#     # TODO : get data from database
#     if user_data:
#         profile = {
#             'username': user_data[0],
#             'name': user_data[2],
#             'jenis_kelamin': user_data[3],
#             'jalan': user_data[4],
#             'kotaID': user_data[5],
#             'namakota': ""
#         }
#         # set nama kota disini
#         profile['namakota'] = loadkota.search(profile['kotaID'])['city_name']
        
#         listidkota = list(range(1, len(loadkota.getAll()) + 1))
#         listkota = []
#         for i in listidkota:
#             kota = {
#                 'id': i,
#                 'nama': loadkota.search(i)['city_name']
#             }
#             listkota.append(kota)

#         return render_template("profile.html", profile=profile, username=username, listkota=listkota)
#     else:
#         return redirect(url_for('signin'))

# #Route ke update profile
# @app.route('/profile/update', methods=['POST'])
# def update_profile():
#     print(request.form)
#     username = session.get('username')

#     password = request.form['password']
#     if password != '':
#         password = sha256_crypt.encrypt(password)
#     nama = request.form['name']
#     jenis_kelamin = request.form['jenis_kelamin']
#     jalan = request.form['jalan']
#     kotaId = request.form['kotaID']

#     cur = mysql.connection.cursor()
#     cur.execute("CALL UpdateUserData(%s,%s,%s,%s,%s,%s)", (username,password,nama,jenis_kelamin, jalan, kotaId))
#     mysql.connection.commit()
#     return redirect(url_for('get_profile'))




@app.route('/logout')
def logout():
  session['logged_in'] = False
  session['username'] = ''
  session['add_to_cart_success'] = ''
  session['remove_from_cart_success'] = ''
  session['kurir'] = ''
  session['ongkir'] = 0
  session['order_info'] = {
                'total_price': 0,
                'total_shipping': 0,
                'total_payment': 0,
            }
    
  return redirect(url_for('signin'))

# @app.route("/product-detail/<product_id>", methods=['GET','POST'])
# def productdetail(product_id):
#     if request.method == 'GET':
#         username = session.get('username')
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM products WHERE productId=%s", [product_id])
#         data = cur.fetchone()
#         cur.execute("SELECT nama FROM users WHERE username=%s", [data[6]])
#         nama = cur.fetchone()

#         #cek jika sudah mereview
#         cur.execute("SELECT COUNT(*) FROM review WHERE usernameReviewer=%s AND productId = %s", (username,product_id))
#         have_reviewed = False
#         rev_count = cur.fetchone()[0]
#         if rev_count > 0:
#             have_reviewed = True

#         #cek jika sudah pernah membeli
#         cur.execute("""
#         SELECT count(*) FROM order_detail 
#         WHERE productId =%s AND orderId IN (
#         SELECT orderId FROM orders WHERE customerUsername =%s AND status = 'Selesai');
#         """, (product_id, username))

#         jumlah_beli = cur.fetchone()[0]
#         have_bought = False
#         if jumlah_beli > 0:
#             have_bought = True

#         #hitung review
#         review_count = 0
#         overall_rating = 0
        
#         cur.execute("SELECT sum(rating), count(*) FROM review WHERE productId=%s", [product_id])
#         review_data = cur.fetchone()
#         review_count = review_data[1]
#         sum_rating = 0
#         if review_count > 0:
#             sum_rating = review_data[0]
#             overall_rating = round(sum_rating/review_count,2)

#         cur.close()

#         if data:
#             if nama:
#                 cart_status = ''
#                 if session.get('add_to_cart_success') == 'success':
#                     cart_status = 'success'
#                     session['add_to_cart_success'] = ''
#                 elif session.get('add_to_cart_success') == 'failed':
#                     cart_status = 'failed'
#                     session['add_to_cart_success'] = ''
            
#                 name = nama[0]

#                 products = {
#                     'productId': data[0],
#                     'nama': data[1],
#                     'kategori': data[2],
#                     'kondisi': data[3],
#                     'deskripsi': data[4],
#                     'harga': data[5],
#                     'username': data[6],
#                     'image': data[7],
#                     'tanggal': data[8],
#                     'stok': data[9],
#                     'jumlah_ulasan': review_count,
#                     'overall_rating': overall_rating,
#                 }
#                 print(products['jumlah_ulasan'])
#                 print(products['overall_rating'])

#                 return render_template("product-detail.html", 
#                 products=products, sudah_beli=have_bought, sudah_review=have_reviewed, name=name, 
#                 username=username, cart_status=cart_status) #detail produk
#             else:
#                 return render_template("product-detail.html", products=products, name=name, username=username) #detail produk
        
#         return redirect(url_for('home'))
    
#     else:
#         #method POST utk review
#         username = session.get('username')
#         cur = mysql.connection.cursor()

#         #cek jika sudah mereview
#         cur.execute("SELECT COUNT(*) FROM review WHERE usernameReviewer=%s AND productId = %s", (username,product_id))
#         have_reviewed = False
#         rev_count = cur.fetchone()[0]
#         if rev_count > 0:
#             have_reviewed = True

#         #cek jika sudah pernah membeli
#         cur.execute("""
#         SELECT count(*) FROM order_detail 
#         WHERE productId =%s AND orderId IN (
#         SELECT orderId FROM orders WHERE customerUsername =%s AND status = 'Selesai');
#         """, (product_id, username))

#         jumlah_beli = cur.fetchone()[0]
#         have_bought = False
#         if jumlah_beli > 0:
#             have_bought = True

#         rating = float(request.form['review'])
#         if rating > 5:
#             rating = 5

#         if have_bought and not have_reviewed: 
#             cur.execute("CALL AddReview(%s,%s,%s)", (product_id, username, rating))

#         cur.close()
#         mysql.connection.commit()

#         return redirect(url_for('productdetail', product_id=product_id))


# @app.route('/cart')
# def cart():
#     if not session.get('logged_in'):
#         return redirect(url_for('signin'))

#     username = session.get('username')
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM cart WHERE username=%s", [username])
#     cart_data = cur.fetchall()
#     cur.execute("SELECT nama FROM users WHERE username=%s", [username])
#     name = cur.fetchone()[0]

#     remove_status = ''
#     if session.get('remove_from_cart_success') == 'success':
#         remove_status = 'success'
#         session['remove_from_cart_success'] = ''
#     elif session.get('remove_from_cart_success') == 'failed':
#         remove_status = 'failed'
#         session['remove_from_cart_success'] = ''
    
#     if cart_data:
#         cart_items = []
#         cartinfo = {
#             'total_price': 0,
#             'total_shipping': 25000,
#             'total_payment': 0,
#         }
#         for item in cart_data:
#             product_id = item[1]
#             cur.execute("SELECT * FROM products WHERE productId=%s", [product_id])
#             p = cur.fetchone()
#             cart_item = {
#                     'productId': p[0],
#                     'nama': p[1],
#                     'kategori': p[2],
#                     'kondisi': p[3],
#                     'harga': p[5],
#                     'username': p[6],
#                     'image': p[7],
#                     'jumlah': item[2],
#                     'total_harga': item[2] * p[5]
#                 }
#             cartinfo['total_price'] += cart_item['total_harga']
#             cart_items.append(cart_item)
        
#         cartinfo['total_payment'] = cartinfo['total_price'] + cartinfo['total_shipping']

#         return render_template("cart.html", username=username, name=name 
#         ,cart_items=cart_items, cartinfo=cartinfo, remove_status=remove_status)
#     else:
#         msg = "Keranjang belanja anda masih kosong"
#         return render_template("cart.html",username=username, name=name, 
#         msg=msg, remove_status=remove_status )


# @app.route('/cart/add/<product_id>', methods=['GET'])
# def add_to_cart(product_id):

#     if not session.get('logged_in'):
#         return redirect(url_for('signin'))

#     username = session.get('username')
#     cur = mysql.connection.cursor()
#     cur.execute("CALL AddToCart(%s,%s)", (username, product_id))
#     status = cur.fetchone()
#     cur.close()
#     mysql.connection.commit()
    
#     status = status[0]
    
#     if status != 0:
#         session['add_to_cart_success'] = 'success'
#     else:
#         session['add_to_cart_success'] = 'failed'

#     return redirect(url_for('productdetail', product_id=product_id))

# @app.route('/cart/delete/<product_id>', methods=['GET'])
# def remove_from_cart(product_id):

#     if not session.get('logged_in'):
#         return redirect(url_for('signin'))

#     username = session.get('username')
#     cur = mysql.connection.cursor()
#     cur.execute("CALL RemoveFromCart(%s,%s)", (username, product_id))
#     status = cur.fetchone()
#     cur.close()
#     mysql.connection.commit()
    
#     status = status[0]
    
    
#     if status != 0:
#         session['remove_from_cart_success'] = 'success'
#     else:
#         session['remove_from_cart_success'] = 'failed'
    

#     return redirect(url_for('cart'))


# @app.route('/order-detail', methods=['GET','POST'])
# def order_detail():
    
#     if request.method == "GET":
#         if not session.get('logged_in'):
#             return redirect(url_for('signin'))
        
#         username = session.get('username')
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM cart WHERE username=%s", [username])
#         cart_data = cur.fetchall()
#         cur.execute("SELECT nama FROM users WHERE username=%s", [username])
#         name = cur.fetchone()[0]
#         cur.execute("SELECT * from kurir")
#         datakurir = cur.fetchall()
#         listkurir = []
#         for k in datakurir:
#             kurir = {
#                 'kode': k[0],
#                 'nama': k[1]
#             }
#             listkurir.append(kurir)

#         if cart_data:
#             cart_items = []
#             orderinfo = {
#                 'total_price': 0,
#                 'total_shipping': 0,
#                 'total_payment': 0,
#             }
#             for item in cart_data:
#                 product_id = item[1]
#                 cur.execute("SELECT * FROM products WHERE productId=%s", [product_id])
#                 p = cur.fetchone()
                
#                 cur.execute("SELECT products.username, users.idKota  FROM cart INNER JOIN products ON cart.productId=products.productId INNER JOIN users ON users.username=products.username WHERE cart.username =%s", [username])
#                 sellerData = cur.fetchone()
                
#                 cart_item = {
#                     'productId': p[0],
#                     'nama': p[1],
#                     'kategori': p[2],
#                     'kondisi': p[3],
#                     'harga': p[5],
#                     'username': p[6],
#                     'image': p[7],
#                     'jumlah': item[2],
#                     'total_harga': item[2] * p[5],
#                     'pengirim': sellerData[0],
#                     'alamatpengirim': loadkota.search(sellerData[1])['city_name']
#                 }
#                 orderinfo['total_price'] += cart_item['total_harga']
#                 cart_items.append(cart_item)


#             cur.execute("SELECT idKota FROM users WHERE username =%s", [username])
#             kotaIduser = cur.fetchone()[0]
#             cur.execute("SELECT jalan FROM users WHERE username =%s", [username])
#             alamatUSer = cur.fetchone()[0]

#             kotaUser = alamatUSer + " " + loadkota.search(kotaIduser)['city_name']

#             kurir_pilihan = session.get('kurir')
#             session['kurir_temp'] = kurir_pilihan
            
#             kurir = {
#                     'kode': '',
#                     'nama': ''
#                     }
#             if kurir_pilihan != '':
#                 cur.execute("SELECT * FROM kurir WHERE kode_kurir=%s", [kurir_pilihan])
#                 k = cur.fetchone()
#                 if k:
#                     kurir = {
#                     'kode': k[0],
#                     'nama': k[1]
#                     }
#                     session['kurir'] = ''

#             ongkir = session.get('ongkir')
#             session['ongkir'] = 0

#             if ongkir is not None:
#                 if ongkir > 0:
#                     orderinfo['total_shipping'] = ongkir
            
#             orderinfo['total_payment'] = orderinfo['total_price'] + orderinfo['total_shipping']
#             session['order_info'] = orderinfo

#             return render_template("order-detail.html", username=username, name=name 
#             ,cart_items=cart_items, orderinfo=orderinfo, kurir=kurir, listkurir=listkurir, kotaUser=kotaUser)

#         else:
#             msg = "Keranjang belanja anda masih kosong"
#             return render_template("order-detail.html",username=username, name=name, 
#             msg=msg )
    
#     else: #order-detail/shipment jadinya disini aja ya pake method POST
#         username = session.get('username')
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT products.username, users.idKota  FROM cart INNER JOIN products ON cart.productId=products.productId INNER JOIN users ON users.username=products.username WHERE cart.username =%s", [username])
#         sellerData = cur.fetchone()

#         cur.execute("SELECT idKota FROM users WHERE username =%s", [username])
#         kotaIduser = cur.fetchone()

#         # while True:
#         #     try:
#         #         totalOngkir = rajaongkir.cekOngkir(sellerData[1], kotaIduser[0], kurir);
#         #     except:
#         #         continue
#         #     else:
#         #         #the rest of the code
#         #         session['ongkir'] = totalOngkir['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value']
#         #         break
#         # return redirect(url_for('order_detail'))

#         kurir = request.form['pilihkurir']
#         session['kurir'] = kurir

#         while True:
#             try:
#                 totalOngkir = rajaongkir.cekOngkir(sellerData[1], kotaIduser[0], kurir);
#             except:
#                 continue
#             else:
#                 session['ongkir'] = totalOngkir['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value']
#                 break
#         return redirect(url_for('order_detail'))

#         # totalOngkir = rajaongkir.cekOngkir(sellerData[1], kotaIduser[0], kurir)
#         # session['ongkir'] = totalOngkir['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value']
#         # return redirect(url_for('order_detail'))
    
# @app.route('/payment', methods=['GET','POST'])
# def payment():
    
#     if request.method == 'GET':
#         if not session.get('logged_in'):
#             return redirect(url_for('signin'))

#         username = session.get('username')
#         orderinfo = session.get('order_info')
#         pembayaran = {
#             'total_barang': 0,
#             'ongkir': 0,
#             'asuransi_pengiriman': 1000,
#             'total_tagihan': 0
#         }
        
#         pembayaran['total_barang'] += int(float(orderinfo['total_price']))
#         pembayaran['ongkir'] += int(float(orderinfo['total_shipping']))
#         pembayaran['total_tagihan'] += int(float(orderinfo['total_payment'])) + pembayaran['asuransi_pengiriman']

#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM saldo WHERE username=%s", [username])
#         data_saldo = cur.fetchone()
#         saldo = data_saldo[1]

#         msg = ''
#         if saldo >= pembayaran['total_tagihan']:
#             msg = 'cukup'

#         return render_template("payment.html",username=username, total=pembayaran, saldo=saldo, msg=msg)

#     else:
#         username = session.get('username')
#         orderinfo = session.get('order_info')
#         pembayaran = {
#             'total_barang': 0,
#             'ongkir': 0,
#             'asuransi_pengiriman': 1000,
#             'total_tagihan': 0
#         }
        
#         pembayaran['total_barang'] += int(float(orderinfo['total_price']))
#         pembayaran['ongkir'] += int(float(orderinfo['total_shipping']))
#         pembayaran['total_tagihan'] += int(float(orderinfo['total_payment'])) + pembayaran['asuransi_pengiriman']

#         payment_option = str(request.form['metode_bayar'])

#         cur = mysql.connection.cursor()
#         cur.execute("SELECT COUNT(*) FROM orders WHERE customerUsername=%s", [username])
#         count = cur.fetchone()[0]
#         cur.execute("SELECT jalan, idKota FROM users WHERE username=%s", [username])
#         address = cur.fetchone()

#         orderId = username + '-' + str(count + 1)
#         shipVia = session.get('kurir_temp')
#         shipAddress = address[0]
#         shipCityId = address[1]
#         total_payment = int(request.form['total_tagihan'])
#         print(payment_option)
#         status = 'Dikirim'

#         if payment_option == 'COD':
#             paid = 'False'
#             cur.execute("CALL AddOrder(%s,%s,NOW(),NOW(),%s,%s,%s,%s,%s,%s,%s)", 
#             (orderId, username, shipVia, shipAddress, shipCityId, total_payment, payment_option, paid, status))
            
            
#         elif payment_option == 'E-Wallet':
#             cur.execute("""
#             SELECT saldo_ewallet INTO @cur_saldo FROM saldo WHERE username = %s;
#             UPDATE saldo
# 	            SET
# 		            saldo_ewallet = @cur_saldo - %s
#             WHERE username = %s;
#             """, (username,total_payment,username))

#             paid = 'True'
#             cur.execute("CALL AddOrder(%s,%s,NOW(),NOW(),%s,%s,%s,%s,%s,%s,%s)", 
#             (orderId, username, shipVia, shipAddress, shipCityId, total_payment, payment_option, paid, status))

#         cur.execute("SELECT * FROM cart where username=%s",[username])
#         cart = cur.fetchall()

#         for item in cart:
#             productId = item[1]
#             quantity = item[2]
            
#             cur.execute("CALL AddOrderDetail(%s,%s,%s)",(orderId, productId, quantity))
            
#         #Clear User's Cart
#         cur.execute("""
#             DELETE FROM cart
#             WHERE username = %s;
#             """, [username])

#         cur.close()
#         mysql.connection.commit()

#         return render_template("payment-success.html",username=username, total=pembayaran, payment_option=payment_option)

    
# @app.route('/myorders')
# def my_orders():
#     username = session.get('username')
#     cur = mysql.connection.cursor()
#     cur.execute('SELECT * FROM orders WHERE customerUsername=%s ORDER BY orderDate DESC', [username])
#     data_orders = cur.fetchall()
    
#     if data_orders:
#         has_order = True
#         my_orders = []
#         for order in data_orders:
#             my_order = {
#                 'order_id': order[0],
#                 'cust_username': order[1],
#                 'order_date': order[2],
#                 'payment_method':order[8],
#                 'status': order[10],
#                 'foto_thumbnail':'',
#                 'jumlah_produk': 0
#             }
#             cur.execute('SELECT productId FROM order_detail WHERE orderId=%s LIMIT 1', [my_order['order_id']])
#             product_id_thumbnail = cur.fetchone()[0]
#             #print(product_id_thumbnail)

#             cur.execute('SELECT image_url FROM products WHERE productId=%s', [product_id_thumbnail])
#             thumbnail_url = cur.fetchone()[0]
#             #print(thumbnail_url)

#             cur.execute('SELECT COUNT(*) FROM order_detail WHERE orderId=%s', [my_order['order_id']])
#             jml_produk = cur.fetchone()[0]
#             #print(jml_produk)

#             my_order['foto_thumbnail'] = thumbnail_url
#             my_order['jumlah_produk'] = jml_produk

#             my_orders.append(my_order)
        
#         return render_template("myorders.html", username=username, has_order=has_order, my_orders=my_orders)

#     else:
#         has_order = False
#         return render_template("myorders.html", username=username, has_order=has_order)


# @app.route('/myorders-detail/<order_id>', methods=['GET','POST'])
# def myorders_detail(order_id):
#     if request.method == 'GET':
#         username = session.get('username')
#         cur = mysql.connection.cursor()
#         cur.execute('SELECT * FROM orders WHERE orderId=%s', [order_id])
#         order = cur.fetchone()

#         #buat nyimpen informasi order
#         order_information = {
#             'order_id' : order[0],
#             'order_date': order[2],
#             'kode_kurir': order[4],
#             'kurir': '',
#             'ship_address': order[5],
#             'ship_cityId': order[6],
#             'alamat_pengiriman': '',
#             'total_payment': order[7],
#             'payment_method': order[8],
#             'status': order[10],
#         }

#         #ambil kurir
#         kode_kurir = order_information['kode_kurir']
#         cur.execute('SELECT nama_kurir FROM kurir WHERE kode_kurir=%s', [kode_kurir])
#         kurir = cur.fetchone()[0]
#         order_information['kurir'] = kurir
#         print(kurir)

#         #ambil kota dan tulis alamat pengiriman
#         kota = loadkota.search(order_information['ship_cityId'])['city_name']
#         alamat = order_information['ship_address'] + ' ' + kota
#         order_information['alamat_pengiriman'] = alamat
#         print(alamat)

#         order_items = []

#         #ambil data tiap produk di order detail 
#         cur.execute('SELECT * FROM order_detail WHERE orderId=%s', [order_id])
#         order_detail = cur.fetchall()
#         for item in order_detail:

#             product_id = item[1]
#             cur.execute('SELECT nama, harga, username, image_url FROM products WHERE productId=%s', [product_id])
#             product = cur.fetchone()

#             username_seller = product[2]
#             cur.execute('SELECT nama, idKota FROM users WHERE username=%s', [username_seller])
#             seller = cur.fetchone()
            
#             #buat nyimpen tiap produk di order detail
#             order_item = {
#                 'nama': product[0],
#                 'harga': product[1],
#                 'nama_seller': seller[0],
#                 'kota_seller': loadkota.search(seller[1])['city_name'] ,
#                 'image_url': product[3],
#                 'jumlah': item[2],
#                 'total_harga': product[1] * item[2]
#             } 

#             order_items.append(order_item)
        
#         print(order_information)

#         return render_template("myorders-detail.html", username=username, 
#         informasi_pesanan=order_information, my_orders=order_items)
        

#     else:
#         username = session.get('username')
#         cur = mysql.connection.cursor()
#         cur.execute('SELECT * FROM orders WHERE orderId=%s', [order_id])
#         order = cur.fetchone()
       
#         if order[1] == username:

#             cur.execute('''
#             UPDATE orders
#             SET 
#                 status = 'Selesai',
#                 paid = 'True'
#             WHERE orderId = %s;
#             ''', [order_id])

#             cur.execute('SELECT * FROM order_detail WHERE orderId=%s', [order_id])
#             order_detail = cur.fetchall() 

#             for item in order_detail:
#                 cur.execute('SELECT * FROM products WHERE productId = %s', [item[1]])
#                 product = cur.fetchone()

#                 username_seller = product[6]
        
#                 cur.execute('SELECT * FROM saldo WHERE username = %s', [username_seller])
#                 current_saldo = cur.fetchone()[1]

#                 saldo_baru = current_saldo + (product[5]*item[2])
               
#                 cur.execute('''
#                 UPDATE saldo
#                 set 
#                 saldo_ewallet = %s
#                 WHERE 
#                 username = %s''', (saldo_baru, username_seller))

#             cur.close()
#             mysql.connection.commit()

#             return redirect(url_for('myorders_detail', order_id=order_id))

#         else:
#             #kalo customerUsername order tidak sama dengan username session
#             return redirect(url_for('my_orders'))

# kalo mau di comment/uncomment diblok terus Ctrl + Shift + /
# # ROUTE detail pesanan saya
# @app.route('/myorders-detail/<order_id>', methods=['GET','POST'])
# def myorders_detail(order_id):
#     if request.method == 'GET':
#         if False:
#             username = session.get('username')
#             cur = mysql.connection.cursor()
#             cur.execute('SELECT * FROM orders WHERE customerUsername=%s', [username])
#             data_orders = cur.fetchall()

#             my_orders = []
#             for order in data_orders:

#                 my_order = {
#                     'order_id' : order[0],
#                     'order_date': order[2],
#                     'kurir': order[4],
#                     'ship_address': order[5],
#                     'total_payment': order[7],
#                     'payment_method': order[8],
#                     'status': order[10],
#                     'nama_barang':''
#                 }

#                 # kayaknya masih ada yang salah
#                 cur.execute('SELECT nama FROM products WHERE productId=%s', [my_order['order_id']])
#                 namabarang = cur.fetchone()[0]

#                 my_order['nama_barang'] = namabarang

#                 my_orders.append(my_order)

#         # RETURN VALUENYA TAK GANTI DULU
#         # return render_template("myorders-detail.html", username=username, my_orders=my_orders)

#         username = session.get('username')
#         my_orders = [
#             {
#                 'nama': 'Coffee Maker Espresso Machine Mesin Kopi Mayaka Premium CM 5013 Black',
#                 'kota_penjual': 'jakarta',
#                 'jumlah': 12,
#                 'harga_total': 12000000,
#                 'img_url': 'https://cf.shopee.co.id/file/46c3bc579f8762d94974fefe7edc621d'
#             }, 
#             {
#                 'nama': 'Jaket Pria',
#                 'kota_penjual': 'bandung',
#                 'jumlah': 1,
#                 'harga_total': 120000,
#                 'img_url': 'https://media.karousell.com/media/photos/products/2021/9/3/size_m_jaket_bomber_original_1630681353_d2c60297.jpg'
#             },{
#                 'nama': 'Coffee Maker Espresso Machine Mesin Kopi Mayaka Premium CM 5013 Black',
#                 'kota_penjual': 'jakarta',
#                 'jumlah': 12,
#                 'harga_total': 12000000,
#                 'img_url': 'https://cf.shopee.co.id/file/46c3bc579f8762d94974fefe7edc621d'
#             }, 
#             {
#                 'nama': 'Jaket Pria',
#                 'kota_penjual': 'bandung',
#                 'jumlah': 1,
#                 'harga_total': 120000,
#                 'img_url': 'https://media.karousell.com/media/photos/products/2021/9/3/size_m_jaket_bomber_original_1630681353_d2c60297.jpg'
#             },{
#                 'nama': 'Coffee Maker Espresso Machine Mesin Kopi Mayaka Premium CM 5013 Black',
#                 'kota_penjual': 'jakarta',
#                 'jumlah': 12,
#                 'harga_total': 12000000,
#                 'img_url': 'https://cf.shopee.co.id/file/46c3bc579f8762d94974fefe7edc621d'
#             }, 
#             {
#                 'nama': 'Jaket Pria',
#                 'kota_penjual': 'bandung',
#                 'jumlah': 1,
#                 'harga_total': 120000,
#                 'img_url': 'https://media.karousell.com/media/photos/products/2021/9/3/size_m_jaket_bomber_original_1630681353_d2c60297.jpg'
#             },{
#                 'nama': 'Coffee Maker Espresso Machine Mesin Kopi Mayaka Premium CM 5013 Black',
#                 'kota_penjual': 'jakarta',
#                 'jumlah': 12,
#                 'harga_total': 12000000,
#                 'img_url': 'https://cf.shopee.co.id/file/46c3bc579f8762d94974fefe7edc621d'
#             }, 
#             {
#                 'nama': 'Jaket Pria',
#                 'kota_penjual': 'bandung',
#                 'jumlah': 1,
#                 'harga_total': 120000,
#                 'img_url': 'https://media.karousell.com/media/photos/products/2021/9/3/size_m_jaket_bomber_original_1630681353_d2c60297.jpg'
#             },
#         ]
#         informasi_pesanan = {
#             'status': 'dikirim',
#             'metode_bayar': 'COD',
#             'tanggal': '20 Maret 2022',
#             'alamat': 'Apartemen Mansion City Lantai 7 No. 32, Jalan Rumput Hijau Kav. 18, Matraman, Jakarta Timur, 13120',
#             'kurir': 'JNE',
#             'total': 10000000,
#         }
#         return render_template("myorders-detail.html", username=username, my_orders=my_orders, informasi_pesanan=informasi_pesanan)

#     else:
#         username = session.get('username')

# @app.route('/customer-orders')
# def customer_orders():
#     username = session.get('username')
#     cur = mysql.connection.cursor()

#     cur.execute('''SELECT * FROM orders WHERE orderId IN (SELECT DISTINCT orderId FROM order_detail WHERE
#     productId IN (SELECT productId from products where username =%s)) ORDER BY orderDate DESC ''',[username])
#     data_orders = cur.fetchall()
    
#     if data_orders:
#         has_order = True
#         costumer_orders = []
#         for order in data_orders:
#             costumer_order = {
#                 'order_id': order[0],
#                 'cust_username': order[1],
#                 'order_date': order[2],
#                 'payment_method':order[8],
#                 'status': order[10],
#                 'foto_thumbnail':'',
#                 'jumlah_produk': 0
#             }
#             cur.execute(
#             """
#             SELECT productId FROM order_detail WHERE orderId=%s 
#             AND productId IN (SELECT productId from products where username =%s) 
#             LIMIT 1
#             """, (costumer_order['order_id'],username))
#             product_id_thumbnail = cur.fetchone()[0]
#             #print(product_id_thumbnail)

#             cur.execute('SELECT image_url FROM products WHERE productId=%s', [product_id_thumbnail])
#             thumbnail_url = cur.fetchone()[0]
#             #print(thumbnail_url)

#             cur.execute('SELECT COUNT(*) FROM order_detail WHERE orderId=%s', [costumer_order['order_id']])
#             jml_produk = cur.fetchone()[0]
#             #print(jml_produk)

#             costumer_order['foto_thumbnail'] = thumbnail_url
#             costumer_order['jumlah_produk'] = jml_produk

#             costumer_orders.append(costumer_order)
        
#         return render_template("customer_orders.html", username=username, has_order=has_order, customer_orders=costumer_orders)

#     else:
#         has_order = False
#         return render_template("customer_orders.html", username=username, has_order=has_order)

# @app.route('/customer-orders-detail/<order_id>', methods=['GET'])
# def customer_orders_detail(order_id):
#     username = session.get('username')
#     cur = mysql.connection.cursor()
#     cur.execute('SELECT * FROM orders WHERE orderId=%s', [order_id])
#     order = cur.fetchone()

#     #buat nyimpen informasi order
#     order_information = {
#         'order_id' : order[0],
#         'order_date': order[2],
#         'kode_kurir': order[4],
#         'kurir': '',
#         'ship_address': order[5],
#         'ship_cityId': order[6],
#         'alamat_pengiriman': '',
#         'total_payment': 0,
#         'payment_method': order[8],
#         'status': order[10],
#     }

#     #ambil kurir
#     kode_kurir = order_information['kode_kurir']
#     cur.execute('SELECT nama_kurir FROM kurir WHERE kode_kurir=%s', [kode_kurir])
#     kurir = cur.fetchone()[0]
#     order_information['kurir'] = kurir
#     print(kurir)

#     #ambil kota dan tulis alamat pengiriman
#     kota = loadkota.search(order_information['ship_cityId'])['city_name']
#     alamat = order_information['ship_address'] + ' ' + kota
#     order_information['alamat_pengiriman'] = alamat
#     print(alamat)

#     order_items = []

#     #ambil data tiap produk di order detail 
#     #ditambah statement di where biar ambil data sesuai nama seller
#     cur.execute('SELECT * FROM order_detail WHERE orderId=%s AND productId IN (SELECT productId from products WHERE username=%s)', (order_id, username))
#     order_detail = cur.fetchall()
#     for item in order_detail:

#         product_id = item[1]
#         cur.execute('SELECT nama, harga, username, image_url FROM products WHERE productId=%s', [product_id])
#         product = cur.fetchone()

#         username_seller = product[2]
#         cur.execute('SELECT nama, idKota FROM users WHERE username=%s', [username_seller])
#         seller = cur.fetchone()
        
#         #buat nyimpen tiap produk di order detail
#         order_item = {
#             'nama': product[0],
#             'harga': product[1],
#             'nama_seller': seller[0],
#             'kota_seller': loadkota.search(seller[1])['city_name'] ,
#             'image_url': product[3],
#             'jumlah': item[2],
#             'total_harga': product[1] * item[2]
#         } 

#         order_information['total_payment'] += order_item['total_harga']

#         order_items.append(order_item)
    
#     print(order_information)

#     return render_template("customer-orders-detail.html", username=username, 
# 	informasi_pesanan=order_information, my_orders=order_items, order_id=order_id)
	
# @app.route('/myproducts')
# def get_products():
#     username = session.get('username')
#     cur = mysql.connection.cursor()
#     cur.execute('SELECT * FROM products WHERE username=%s', [username])
#     user_products = cur.fetchall()    
#     cur.execute('SELECT * FROM users WHERE username=%s', [username])
#     user_data = cur.fetchone()

#     if user_data:
#         have_products = False
#         profile = {
#                 'username': user_data[0],
#                 'nama': user_data[2],
#                 'jenis_kelamin': user_data[3],
#                 'alamat': user_data[4],
#             }
#         if user_products:
#             have_products = True
#             products = []
#             for p in user_products:
#                 product = {
#                     'productId': p[0],
#                     'nama': p[1],
#                     'kategori': p[2],
#                     'kondisi': p[3],
#                     'deskripsi': p[4],
#                     'harga': p[5],
#                     'username': p[6],
#                     'image': p[7],
#                     'stok': p[9],
#                 }
#                 products.append(product)

#             return render_template("user-products.html", username = username , have_products = have_products, 
#             profile = profile , products = products)
#         else:
#             msg = "You don't have any products"
#             return render_template("user-products.html", username = username , have_products = have_products, 
#             profile = profile, msg = msg)

#     return redirect(url_for('home'))

# #Route Update Product
# @app.route('/myproducts/update', methods=['POST'])
# def update_product():
#     print(request.form)
#     username = session.get('username')
#     product_id = request.form['productId']
#     nama = request.form['nama']
#     kategori = request.form['kategori']
#     kondisi = request.form['kondisi']
#     deskripsi = request.form['deskripsi']
#     harga = request.form['harga']
#     image = request.form['image']
#     stok = request.form['stok']
#     cur = mysql.connection.cursor()
#     cur.execute("CALL UpdateProductData(%s,%s,%s,%s,%s,%s,%s, NOW(),%s)",(product_id,nama,kategori,kondisi,deskripsi,harga,image, stok))
#     mysql.connection.commit()
#     return redirect(url_for('get_products'))

# #Route Delete
# @app.route('/myproducts/delete/<product_id>', methods=['GET'])
# def delete_product(product_id):
#     username = session.get('username')
#     cur = mysql.connection.cursor()
#     cur.execute("DELETE FROM products WHERE productId=%s AND username=%s", (product_id, username))
#     mysql.connection.commit()
#     return redirect(url_for('get_products'))


# @app.route('/myproducts/add', methods=['GET', 'POST'])
# def addproduct():
#     username = session.get('username')
#     if request.method == 'GET':
#         return render_template('addproduct.html' , username = username)
#     else:
#         nama = request.form['nama']
#         kategori = request.form['kategori']
#         kondisi = request.form['kondisi']
#         deskripsi = request.form['deskripsi']
#         harga = request.form['harga']
#         username = session.get('username')
#         image = request.form['image']
#         stok = request.form['stok']
#         cur = mysql.connection.cursor()

#         username_check = cur.execute('SELECT * FROM users WHERE username = %s', [username])
#         if username_check :
#             cur.execute("CALL AddProduct(%s,%s,%s,%s,%s,%s,%s,%s)",(nama,kategori,kondisi,deskripsi,harga,username,image,stok))
#             mysql.connection.commit()
#             cur.close()
#         else:
#             return redirect(url_for('signin'))
#         return redirect(url_for('get_products'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)
