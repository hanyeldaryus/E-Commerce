DROP DATABASE IF EXISTS weshop;
CREATE DATABASE weshop;
USE weshop;

#TABLES
CREATE TABLE products(
	productId INT(6) AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(1000),
    kategori VARCHAR(100),
    kondisi VARCHAR(100),
    deskripsi VARCHAR(10000),
    harga DECIMAL(10,2),
    username VARCHAR(1000) DEFAULT 'admin',
    image_url VARCHAR(1000),
    tanggal DATETIME,
    stok INT
);

ALTER TABLE products
	ADD COLUMN available ENUM('Yes','No');

CREATE TABLE users(
	username VARCHAR(100) PRIMARY KEY,
    password VARCHAR(1000),
    nama VARCHAR(1000),
    jenis_kelamin ENUM('Male','Female'),
    jalan VARCHAR(1000),
    idKota INT(6) 
);

ALTER TABLE users
	ADD COLUMN filename VARCHAR(1000);

CREATE TABLE cart(
	username VARCHAR(100),
    productId INT(6),
    quantity INT
);

CREATE TABLE kurir (
    kode_kurir VARCHAR(1000),
    nama_kurir VARCHAR(1000)
);

CREATE TABLE orders (
	orderId VARCHAR(100),
	customerUsername VARCHAR(100), 
	orderDate DATETIME, 
	shippedDate DATETIME, 
	shipVia VARCHAR(1000), 
	shipAddress VARCHAR(1000), 
	shipCityId INT(10), 
	total_payment DECIMAL, 
    payment_method ENUM('E-Wallet','COD'),
	paid ENUM('True','False'),
    status ENUM('Dikirim','Diterima','Selesai')
);

Create TABLE order_detail (
	orderId VARCHAR(100), 
	productId INT(10),
	quantity INT(100)
);

Create TABLE saldo (
	username VARCHAR(100), 
	saldo_ewallet DECIMAL(10,2)
);

CREATE TABLE review (
	productId INT(10),
    usernameReviewer VARCHAR(100),
    rating DECIMAL(10,2)
);


#PROCEDURES
DELIMITER $$
CREATE PROCEDURE AddUser(
	username VARCHAR(100),
    password VARCHAR(1000),
    nama VARCHAR(1000),
    jenis_kelamin ENUM('Male','Female'),
    jalan VARCHAR(1000),
    idKota INT(6)
)
BEGIN
	INSERT INTO 
		users 
    VALUES 
    (
    username,
    password,
    nama,
    jenis_kelamin,
    jalan,
    idKota,
    "https://images.tokopedia.net/img/cache/300/default_picture_user/default_toped-19.jpg"
    );
    INSERT INTO
		saldo
	VALUES
    (username, 0);
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE UpdateUserData(
	username_target VARCHAR(100),
    new_password VARCHAR(1000),
    new_nama VARCHAR(1000),
    new_jenis_kelamin ENUM('Male','Female'),
    new_jalan VARCHAR(1000),
    new_idKota INT(6) 
)
BEGIN
	SELECT password INTO @old_password from users WHERE username = username_target;
	IF new_password = @old_password OR new_password = '' THEN
		UPDATE users 
		SET 
			nama = new_nama,
			jenis_kelamin = new_jenis_kelamin,
			jalan = new_jalan,
            idKota = new_idKota
		WHERE
			username = username_target;
	ELSE
		UPDATE users 
		SET 
			password = new_password,
			nama = new_nama,
			jenis_kelamin = new_jenis_kelamin,
			jalan = new_jalan,
            idKota = new_idKota
		WHERE
			username = username_target;
	END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE UpdateProductData(
	productId_target INT(6),
	new_nama VARCHAR(1000),
    new_kategori VARCHAR(100),
    new_kondisi VARCHAR(100),
    new_deskripsi VARCHAR(10000),
    new_harga DECIMAL(10,2),
    new_image_url VARCHAR(1000),
    new_tanggal DATETIME,
    new_stok INT
)
BEGIN
	UPDATE products
		SET 
			nama = new_nama,
            kategori = new_kategori,
            kondisi = new_kondisi,
            deskripsi = new_deskripsi,
            harga = new_harga,
            image_url = new_image_url,
            tanggal = new_tanggal,
            stok = new_stok
		WHERE
			productId = productId_target;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE AddProduct(
	nama VARCHAR(1000),
    kategori VARCHAR(100),
    kondisi VARCHAR(100),
    deskripsi VARCHAR(10000),
    harga DECIMAL(10,2),
    username VARCHAR(100),
    image_url VARCHAR(1000),
    stok INT
)
BEGIN
	INSERT INTO products
    (nama, kategori, kondisi, deskripsi, harga, username, image_url, tanggal, stok, available) 
    VALUES
    (nama, kategori, kondisi, deskripsi, harga, username, image_url, NOW(), stok, 'Yes')
    ;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE DeleteProduct(
	productId_target INT,
    username_target VARCHAR(1000)
)
BEGIN
	UPDATE products
	SET
		available = 'No'
	WHERE productId = productId_target AND username = username_target
    ;
    DELETE from cart WHERE productId = productId_target;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE GetStock(
    productId_target INT
)
BEGIN
	SELECT stok FROM products WHERE productId = productId_target;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE AddToCart(
	username_target VARCHAR(100),
    productId_target INT
)
BEGIN
	SELECT stok INTO @stok FROM products WHERE productId = productId_target;
    SELECT COUNT(*) INTO @exist FROM cart 
	WHERE username = username_target AND productId = productId_target;
    IF @stok > 0 AND @exist > 0 THEN
		SELECT quantity INTO @cur_quantity FROM cart 
		WHERE username = username_target AND productId = productId_target;
		UPDATE cart
		SET 
            quantity = @cur_quantity + 1
		WHERE
			username = username_target AND productId = productId_target;
		SELECT stok FROM products WHERE productId = productId_target;
        UPDATE products
		SET 
            stok = @stok - 1
		WHERE
			productId = productId_target;
    ELSEIF @stok > 0 THEN
		INSERT INTO cart
			(username, productId, quantity) 
		VALUES
			(username_target, productId_target, 1)
		;
        SELECT stok FROM products WHERE productId = productId_target;
        UPDATE products
		SET 
            stok = @stok - 1
		WHERE
			productId = productId_target;
		
    ELSE
		SELECT stok FROM products WHERE productId = productId_target;
    END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE AddOrder(
	orderId VARCHAR(100),
	customerUsername VARCHAR(100), 
	orderDate DATETIME, 
	shippedDate DATETIME, 
	shipVia VARCHAR(1000), 
	shipAddress VARCHAR(1000), 
	shipCityId INT(10), 
	total_payment DECIMAL, 
    payment_method ENUM('E-Wallet','COD'),
	paid ENUM('True','False'),
    status ENUM('Dikirim','Diterima','Selesai')
)
BEGIN
INSERT INTO orders
    VALUES 
    (
    orderId,
    customerUsername,
    orderDate,
    shippedDate,
    shipVia,
    shipAddress,
    shipCityId,
    total_payment,
    payment_method,
    paid,
    status
    );
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE AddOrderDetail(
	orderId VARCHAR(100), 
	productId INT(10),
	quantity INT(100)
)
BEGIN
INSERT INTO order_detail
    VALUES 
    (
   	orderId,
	productId,
	quantity
    );
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE RemoveFromCart(
	username_target VARCHAR(100),
    	productId_target INT
)
BEGIN
    SELECT COUNT(*) INTO @exist FROM cart 
		WHERE username = username_target AND productId = productId_target;
    IF @exist > 0 THEN
		SELECT COUNT(*) FROM cart 
			WHERE username = username_target AND productId = productId_target;
        SELECT stok INTO @stok FROM products WHERE productId = productId_target;
        SELECT quantity INTO @quantity FROM cart 
			WHERE username = username_target AND productId = productId_target;
		UPDATE products
		SET 
            stok = @stok + @quantity
		WHERE
			productId = productId_target;
		DELETE FROM cart 
			WHERE username = username_target AND productId = productId_target;
		
	ELSE
		SELECT COUNT(*) FROM cart 
		WHERE username = username_target AND productId = productId_target;
	END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE AddReview(
	productId INT(10),
    usernameReviewer VARCHAR(100),
    rating DECIMAL(10,2)
)
BEGIN
INSERT INTO review
    VALUES 
    (
	productId,
	usernameReviewer,
    rating
    );
END$$
DELIMITER ;


#GENERATE DATA
INSERT INTO products (nama,kategori,kondisi,deskripsi,harga,image_url,tanggal)
	VALUES (
    "Coffee Maker Espresso Machine Mesin Kopi Mayaka Premium CM 5013 Black",
    "Coffee & Tea Maker",
    "Baru",
    "
    Mayaka Premium Coffee Maker CM5013.B Mesin Kopi Espresso
	Produk Premium desain klasik yang unik ini cocok diletakan di dapur indah anda.
	Die Casting aluminium dengan 15 Bar Pump Pressure menjadikan CM5013.B tidak kalah fungsi dan spesifikasi dari Mesin Kopi merek yang lainya.
	- Voltase: 220-240v , 50Hz
	- Daya: 1100 Watt
	- Die Casting alumunium alloy pump
	- 15 bar powerful pressure pump
	- 1.2 Liter Detachable transparent water tank
	- 1 or 2 cups dual-stainless steel filter
	- With high pressure frothing function
	- With overheating and over pressure protected device
	- Detachable drip tray for easy cleaning
	- Adjustable steam knob
	- With thermometer to show the temperature clearly.
    ",
    1475000,
    "https://cf.shopee.co.id/file/46c3bc579f8762d94974fefe7edc621d",
	NOW()
    ),
	(
    "Sendal Jepit Pria / Sandal Jepit Ando Hawaii",
    "Sandal Pria",
    "Baru",
    "
    Ando Icon, the tonal Ando logo on a matte strap for style. Comfort comes courtesy of our signature textured footbed and multicolor sole.	
	Icon dari sendal Ando, logo sendal Ando ini memberikan kesan stylist pada sendal Anda. Kenyamaan sendal merupakan hal yang terpenting bagi Ando, dengan dilengkapi warna yang menarik
	Available Size :
	Size 41 : AVAILABLE
	Size 42 : AVAILABLE
	Size Chart :
	- Size 40 (26 cm)
	- Size 41 (27 cm)
	- Size 42 (27.5 cm)
    ",
    38000,
    "https://s0.bukalapak.com/img/06561723592/large/data.png.webp",
	NOW()
    ),
	(
    "Acer Aspire 5 Slim A514",
    "Laptop",
    "Baru",
    "
    Acer Aspire 5 Slim A514 i3 1115G4 4GB 256 SSD
    • CPU : Intel® Core™ i3-1115G4 processor
	• OS : Windows 11 Home
	• LCD : 14\" HD 1366 x 768 / 14 FHD IPS (1920 x 1080), Acer ComfyView™ LED-backlit TFT LCD, 16:9 aspect ratio, Ultra-slim design
	• Memory : 4 GB onboard DDR4 Dual Channel memory
	Upgradeability Max 20GB (4+16), using 1x Free SODIMM Slot
	• Storage : 512 GB SSD PCIe Gen3, 8 Gb/s ,NVMe
	• Graphic : INTEL UHD Graphics
	• Bluetooth : Bluetooth 5.1
	• Wifi : Intel® Wireless Wi-Fi 6 AX201 with MU-MIMO
	• Camera : HD webcam with:1280 x 720 resolution;720p HD audio/video recording;
	• Speaker : Acer Purified.Voice technology with two built-in microphones. Compatible with Cortana with Voice

	• I/O Port :
	HDMI® port
	1x USB 3.2 Gen 1 (with power off charging features)
	2x USB 3.2 Gen 1
	1x USB Type-C
	1x RJ45

	• Features : Power-off USB Charging, Wifi 6, Exo Amp
    ",
    6399000,
    "https://www.static-src.com/wcsstore/Indraprastha/images/catalog/full//93/MTA-10891504/acer_acer_aspire_5_a514-53-381h_i3_1005g1_4gb_1tb_uma_14-_fhd_w10_ohs_full01_gyg4vsie.jpg",
	NOW()
    ),
    (
    "JAKET BOMBER ORIGINAL TERBARU ADA 3 KANTONG DEPAN - CRIME BLACK, L",
    "Jaket Pria",
    "Baru",
    "
    JAKET BOMBER CRIME adalah jaket bomber dengan model terbaru, memiliki kerah dan aksesoris pada pundak. 
    Menyerupai model harrington namun dengan kombinasi fungsi seperti bomber. 
    Terdapat 3 kantong depan aktif yang bisa dipakai.

	Yuk cek detailnya :

	Keistimewaan :
	- ANTI ANGIN / ANTI AIR 100% PADA BAHAN
	(INI JAKET BUKAN JAS HUJAN, TIDAK DIREKOMENDASIKAN DIPAKAI SAAT HUJAN LEBAT)
	- Ada 3 kantong depan
	- Ada kantong dalam
	- Cocok untuk musim hujan karena hangat dan tidak cepat basah terkena air
    
    Code : BOMBER FF PILOT CRIME
	Material : PARASUT TASLAN dan Puring Cotton Fleece

	SIZE L XL
	L (P 67cm, L 54cm)
	XL (P 69cm, L 56cm)
    ",
    119000,
    "https://media.karousell.com/media/photos/products/2021/9/3/size_m_jaket_bomber_original_1630681353_d2c60297.jpg",
    NOW()
    ),
    (
    "Freeknight Tas Ransel Pria Backpack Laptop Waterproof TR107 - Hitam",
    "Tas Ransel",
    "Baru",
    "
    Large Compartment
	Tas laptop ini didesain dengan slot penyimpanan yang luas untuk menyimpan laptop, charger, buku, botol minum / payung dengan rapih. Memudahkan Anda untuk menyimpan atau mengambil barang bawaan Anda.

	Minimalist and Modern Design
	Dengan desain yang minimalis dan modern sangat cocok dipakai untuk pekerja kantoran maupun anak kuliahan.

	Good Quality Material
	Shoulder bag ini dibuat dengan material berkualitas bagus untuk menjamin tas ini tahan lama untuk di gunakan.

	Comfortable
	Tas laptop ini didesain dengan slot penyimpanan yang luas untuk menyimpan laptop, charger, buku, botol minum / payung dengan rapih. Memudahkan Anda untuk menyimpan atau mengambil barang bawaan Anda.

	Ukuran : 50 x 30 17 cm
	Warna : Hitam, Biru, Navy, Orange, Ungu
	Bahan : Nylon Fabric
    ",
    79000,
    "https://id-test-11.slatic.net/p/beadd5325967a48e0dc666555328a718.jpg",
    NOW()
    ),
    (
    "Meja Kerja / Belajar J-White",
    "Meja Kantor",
    "Bekas",
    "
    Meja sederhana yang multifungsi, bisa sebagai meja komputer, meja kantor, meja kamar tidur, meja belajar, dll
	- Mudah di lap
	- Tahan terhadap goresan
	- Tahan terhadap rembesan air
	- Tahan terhadap suhu tinggi
	- Kuat dan tahan lama
	- Mudah di rakit
	- Permukaan yang halus
	- Sudut meja bundar, mencegah benturan yang tidak disengaja
    
    Panjang : 80cm
	Lebar : 40cm

	- Bahan meja : Partikel board

	Fitur :
	* Desain modern & estetik
	* Harga sangat sesuai dengan kualitas produknya 
    ",
    244900,
    "https://cf.shopee.co.id/file/13f81f24c45b756af8da3a80cdc829b7",
    NOW()
    ),
    (
    "Sepatu Pria Sneakers Footstep Footwear - Atom Grey Black ",
    "Sneakers",
    "Baru",
    "
    Sepatu Pria Sneakers Footstep Footwear - Atom Grey Black

    SPESIFIKASI
	Type : Sneakers Type
	Color : Grey
	Upper : Canvas
	Sole : TPR (Thermo Plastic Rubber)
	Holes : 6 Holes
	Insole Material: Polyfoam
	Construction : Cementing

	DESKRIPSI
	Footstep Footwear hadir menawarkan sepatu sneakers dengan kenyamanan penggunaan. 
    Footstep Atom Grey hadir dalam balutan kanvas dengan desain terbaru serta sol TPR.

	SIZECHART SEPATU (dalam satuaan cm)
	- size 39 outsole 27.9cm insole 26.9cm
	- size 40 outsole 28.5cm insole 27.4cm
	- size 41 outsole 29.1cm insole 27.9cm
	- size 42 outsole 29.7cm insole 28.4cm
	- size 43 oustole 30.3cm insole 28.9cm
	- size 44 outsole 30.9cm insole 29.4cm
	- size 45 outsole 31.5cm insole 29.9cm
    ",
    175500,
    "https://s3.bukalapak.com/img/33165179392/large/data.jpeg",
    NOW()
    ),
    (
    "BIDEN Jam Tangan Pria Chronograph Tahan Air QUARTZ Top Bisnis Kasual",
    "Jam Tangan",
    "Baru",
    "
    Nama Merek: BIDEN
Nomor Model: 0241
Gerakan: Quartz
Style: Sport, Fashion, Cusual
Bentuk Kasus: Round
Band Jenis Bahan: Silicone
Case Bahan: Stainless steel
Dial Window Jenis Bahan: Kaca
Jenis Gesper: Gesper
Fitur: Tanggal Otomatis, Kronograf, Tangan Bercahaya,
Kedalaman Kedap Air Tahan Guncangan: 3Bar (Tidak dapat menyentuh air panas, Tidak dapat menekan tombol apa pun di bawah air)

Spesifikasi (perkiraan):
Diameter Dial: 48mm
Tebal Kasus: 16mm
Lebar Band :24mm
Panjang Band: 270mm



MENJAMIN—Jam tangan BIDEN asli, Termasuk garansi 1 tahun skala.
PENGEPAKAN—jam tangan * 1, kotak * 1, kartu garansi * 1,Instruksi*1
ACCURATE TIME KEEPING - Gerakan kuarsa Jepang berkualitas tinggi dengan tampilan analog, menyediakan waktu yang tepat.
LUXURY & ELEGANT DESIGN - gaya busana klasik dapat membuat Anda menjadi pribadi yang menawan. Hadiah fantastis untuk keluarga atau teman Anda.
WATERPROOF UNTUK HARIAN SEHARI-HARI - Stainless steel tahan lama tahan air penutup, Cuci Tangan, Hari Hujan, Berkeringat, TIDAKADA Masalah. 
Secara umum, tahan percikan atau perendaman singkat dalam air, tetapi tidak cocok untuk berenang. (Harap DONT PULL OUT tombol di bawah air) 
Sempurna untuk semua jenis bisnis, santai, kegiatan dalam ruangan atau penggunaan sehari-hari.
    ",
    365000,
    "https://images.tokopedia.net/img/cache/700/VqbcmM/2021/7/15/f3d46345-daa5-42f7-b3ce-0ebf4600f0c7.jpg",
    NOW()
    ),
    (
    "Fantech X9 THOR Macro Gaming Mouse",
    "Mouse",
    "Baru",
    "
    7D MACRO FUNCTION PERFORMANCE
Fantech THOR X9 dirancang dengan 7 tombol yang dapat diprogram untuk tugas makro Anda dengan perangkat lunaknya yang dapat menyimpan hingga 5 profil dan mendukung skrip tombol klik kiri dan penundaan pengeditan

10M SWITCH MADE FOR DURABILITY
Dilengkapi dengan sakelar seumur hidup 10 juta klik yang dibuat untuk daya tahan ekstra bahkan untuk kondisi penggunaan ekstrim sambil memastikan sakelar tetap cepat dan sangat responsif.

4800 DPI ON-THE-FLY DPI SWITCHING
Bersiaplah dalam sekejap dengan peralihan DPI antara 500-4800 DPI. Lakukan gerakan yang benar dalam situasi game apa pun. Beralih melalui beberapa pengaturan DPI untuk memilih opsi di layar dengan cepat atau memindai peta permainan (hingga 4800 DPI) atau menurunkan perpindahan gigi untuk membuat penargetan penembak jitu atau pemilihan unit (500 DPI) dengan presisi piksel menggunakan tombol yang ditempatkan dengan nyaman.

Fantech THOR X9 dibundel dengan perangkat lunak yang dapat diunduh dari fantechworld.com. Anda dapat menyesuaikan semua yang ada di dalamnya mulai dari pengeditan makro tugas tombol, sensitivitas, gulir dan kecepatan klik dua kali tahap DPI, lalu tingkat laporan.

TECHNICAL SPECIFICATION
Gaming Optical Sensor
On-the-fly Adjustable DPI 500-4800
10 million clicks lifetime
1.8m braided cable
RGB 4 color lighting
Size:128x68x41mm
    ",
    94900,
    "https://starcompjogja.com/storage/products/fcaa20942dabdcd151f5f0d15132bd91_mouse-fantech-x9-thor_1.webp",
    NOW()
    ),
    (
    "Yamaha Gitar Akustik Acoustic Folk F310",
    "Gitar Akustik",
    "Bekas",
    "
    Yamaha seri F 310 adalah gitar folk yang mereprentasi semua yang Anda harapkan dari sebuah produk instrumen musik bermerk dunia yang sudah terkenal, Yamaha. Bahan Spruce pada top, kayu mahogani pada bagian depan dan belakang, dan fingerboard rosewood menjadikan gitar folk ini sebuah gitar yang sangat hebat. F-310 cocok untuk Anda para pemula sampai yang sudah professional sekalipun.
Gitar F 310 memberikan kualitas, desain dan sound sama seperti gitar akustik lain namun dengan harga yang terjangkau.

# Adapun Spesifikasi nya ;
* String Skala String 634 mm
* Kedalaman Body 96-116 mm
* Lebar Papan Jari (Nut/Body) 43 mm
* Atas Spruce
* Belakang Meranti
* Sisi Samping Meranti
* Leher Nato
* Papan Jari Rosewood
* Pegangan Rosewood

Warna : Tobacco Brown Sunburst (TBS)
    ",
    1095000,
    "https://galerimusikindonesia.com/image/cache/data/gitar%20dan%20bass/Gitar%20Akustik/yamaha/F310/F310NT-700x700.jpg",
    NOW()
    )
;
INSERT INTO kurir
	VALUES 
    ("jne","Jalur Nugraha Ekakurir (JNE)"),
    ("pos","Pos Indonesia"),
    ("tiki","TIKI")
;

CALL AddUser('admin', '$5$rounds=535000$gE7mbXgQl9jyQYqN$6zHhSp/WoeouI2dzFbMq4xXBb5h40Cx5XKvDEbH7ca7', 'Admin', 'Male', 'Jl. MH Thamrin', 152);
#username : admin, password : admin123

UPDATE products
	SET
		stok = 10
WHERE username = 'admin'
;

UPDATE products
	SET
		available = 'Yes'
WHERE username = 'admin'
;
