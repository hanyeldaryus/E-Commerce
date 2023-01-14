from flask import redirect, request, url_for
from flask import Flask, session
from flask import render_template
from flask_mysqldb import MySQL

from routes.config import * 

@app.route('/payment', methods=['GET','POST'])
def payment():
    
    if request.method == 'GET':
        if not session.get('logged_in'):
            return redirect(url_for('signin'))

        username = session.get('username')
        orderinfo = session.get('order_info')
        pembayaran = {
            'total_barang': 0,
            'ongkir': 0,
            'asuransi_pengiriman': 1000,
            'total_tagihan': 0
        }
        
        pembayaran['total_barang'] += int(float(orderinfo['total_price']))
        pembayaran['ongkir'] += int(float(orderinfo['total_shipping']))
        pembayaran['total_tagihan'] += int(float(orderinfo['total_payment'])) + pembayaran['asuransi_pengiriman']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM saldo WHERE username=%s", [username])
        data_saldo = cur.fetchone()
        saldo = data_saldo[1]

        msg = ''
        if saldo >= pembayaran['total_tagihan']:
            msg = 'cukup'

        return render_template("payment.html",username=username, total=pembayaran, saldo=saldo, msg=msg)

    else:
        username = session.get('username')
        orderinfo = session.get('order_info')
        pembayaran = {
            'total_barang': 0,
            'ongkir': 0,
            'asuransi_pengiriman': 1000,
            'total_tagihan': 0
        }
        
        pembayaran['total_barang'] += int(float(orderinfo['total_price']))
        pembayaran['ongkir'] += int(float(orderinfo['total_shipping']))
        pembayaran['total_tagihan'] += int(float(orderinfo['total_payment'])) + pembayaran['asuransi_pengiriman']

        payment_option = str(request.form['metode_bayar'])

        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM orders WHERE customerUsername=%s", [username])
        count = cur.fetchone()[0]
        cur.execute("SELECT jalan, idKota FROM users WHERE username=%s", [username])
        address = cur.fetchone()

        orderId = username + '-' + str(count + 1)
        shipVia = session.get('kurir_temp')
        shipAddress = address[0]
        shipCityId = address[1]
        total_payment = int(request.form['total_tagihan'])
        print(payment_option)
        status = 'Dikirim'

        if payment_option == 'COD':
            paid = 'False'
            cur.execute("CALL AddOrder(%s,%s,NOW(),NOW(),%s,%s,%s,%s,%s,%s,%s)", 
            (orderId, username, shipVia, shipAddress, shipCityId, total_payment, payment_option, paid, status))
            
            
        elif payment_option == 'E-Wallet':
            cur.execute("""
            SELECT saldo_ewallet INTO @cur_saldo FROM saldo WHERE username = %s;
            UPDATE saldo
	            SET
		            saldo_ewallet = @cur_saldo - %s
            WHERE username = %s;
            """, (username,total_payment,username))

            paid = 'True'
            cur.execute("CALL AddOrder(%s,%s,NOW(),NOW(),%s,%s,%s,%s,%s,%s,%s)", 
            (orderId, username, shipVia, shipAddress, shipCityId, total_payment, payment_option, paid, status))

        cur.execute("SELECT * FROM cart where username=%s",[username])
        cart = cur.fetchall()

        for item in cart:
            productId = item[1]
            quantity = item[2]
            
            cur.execute("CALL AddOrderDetail(%s,%s,%s)",(orderId, productId, quantity))
            
        #Clear User's Cart
        cur.execute("""
            DELETE FROM cart
            WHERE username = %s;
            """, [username])

        cur.close()
        mysql.connection.commit()

        return render_template("payment-success.html",username=username, total=pembayaran, payment_option=payment_option)