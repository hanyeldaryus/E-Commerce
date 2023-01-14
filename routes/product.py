from flask import redirect, request, url_for
from flask import session
from flask import render_template

from routes.config import * 

def productdetail(product_id):
    if request.method == 'GET':
        username = session.get('username')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products WHERE productId=%s AND available='Yes' ", [product_id])
        data = cur.fetchone()
        cur.execute("SELECT nama FROM users WHERE username=%s", [data[6]])
        nama = cur.fetchone()

        #cek jika sudah mereview
        cur.execute("SELECT COUNT(*) FROM review WHERE usernameReviewer=%s AND productId = %s", (username,product_id))
        have_reviewed = False
        rev_count = cur.fetchone()[0]
        if rev_count > 0:
            have_reviewed = True

        #cek jika sudah pernah membeli
        cur.execute("""
        SELECT count(*) FROM order_detail 
        WHERE productId =%s AND orderId IN (
        SELECT orderId FROM orders WHERE customerUsername =%s AND status = 'Selesai');
        """, (product_id, username))

        jumlah_beli = cur.fetchone()[0]
        have_bought = False
        if jumlah_beli > 0:
            have_bought = True

        #hitung review
        review_count = 0
        overall_rating = 0
        
        cur.execute("SELECT AVG(rating), count(*) FROM review WHERE productId=%s", [product_id])
        review_data = cur.fetchone()
        review_count = review_data[1]
        if review_count > 0:
            avg_rating = review_data[0]
            overall_rating = round(avg_rating,2)

        cur.close()

        if data:
            if nama:
                cart_status = ''
                if session.get('add_to_cart_success') == 'success':
                    cart_status = 'success'
                    session['add_to_cart_success'] = ''
                elif session.get('add_to_cart_success') == 'failed':
                    cart_status = 'failed'
                    session['add_to_cart_success'] = ''
            
                name = nama[0]

                products = {
                    'productId': data[0],
                    'nama': data[1],
                    'kategori': data[2],
                    'kondisi': data[3],
                    'deskripsi': data[4],
                    'harga': data[5],
                    'username': data[6],
                    'image': data[7],
                    'tanggal': data[8],
                    'stok': data[9],
                    'jumlah_ulasan': review_count,
                    'overall_rating': overall_rating,
                }
                print(products['jumlah_ulasan'])
                print(products['overall_rating'])

                return render_template("product-detail.html", 
                products=products, sudah_beli=have_bought, sudah_review=have_reviewed, name=name, 
                username=username, cart_status=cart_status) #detail produk
            else:
                return render_template("product-detail.html", products=products, name=name, username=username) #detail produk
        
        return redirect(url_for('home'))
    
    else:
        #method POST utk review
        username = session.get('username')
        cur = mysql.connection.cursor()

        #cek jika sudah mereview
        cur.execute("SELECT COUNT(*) FROM review WHERE usernameReviewer=%s AND productId = %s", (username,product_id))
        have_reviewed = False
        rev_count = cur.fetchone()[0]
        if rev_count > 0:
            have_reviewed = True

        #cek jika sudah pernah membeli
        cur.execute("""
        SELECT count(*) FROM order_detail 
        WHERE productId =%s AND orderId IN (
        SELECT orderId FROM orders WHERE customerUsername =%s AND status = 'Selesai');
        """, (product_id, username))

        jumlah_beli = cur.fetchone()[0]
        have_bought = False
        if jumlah_beli > 0:
            have_bought = True

        rating = float(request.form['review'])
        if rating > 5:
            rating = 5

        if have_bought and not have_reviewed: 
            cur.execute("CALL AddReview(%s,%s,%s)", (product_id, username, rating))

        cur.close()
        mysql.connection.commit()

        return redirect(url_for('productdetail', product_id=product_id))