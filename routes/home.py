from flask import Flask, session
from flask import render_template
from flask_mysqldb import MySQL


from routes.config import *


def home():
    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE available='Yes' ORDER BY tanggal DESC LIMIT 10;")
    rv = cur.fetchall()

    # TODO Ganti jadi fetch rating dari database
    # karena rv ini bentuknya array bukan dictionary,
    # jadi aku anggap aja kalo rating ada di index 10
    # dan total_review di index 11

    products = []
    for i in rv:
        i = list(i)

        product_id = i[0]
        review_count = 0
        overall_rating = 0
        cur.execute("SELECT AVG(rating), count(*) FROM review WHERE productId=%s", [product_id])
        review_data = cur.fetchone()
        review_count = review_data[1]
        if review_count > 0:
            avg_rating = review_data[0]
            overall_rating = round(avg_rating,2)
            print(overall_rating)

        i.append(overall_rating)
        i.append(review_count)
        products.append(i)

    cur.close()

    return render_template('homepage.html', products=products, username=username) # 10 terbaru