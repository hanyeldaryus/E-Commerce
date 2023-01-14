## Cara Pakai Library Loadkota

1. import dulu librarynya
   `import src.loadkota as loadkota`
2. initialize librarynya
   `loadkota.init('lokasi/ke/namafile.json')`
3. list fungsi
   - cari data kota berdasarkan id
     `loadkota.search('id_kota')`
   - cari data kota berdasarkan nama
    `loadkota.searchByName('nama_kota')`
   - ambil semua data kota  
   `loadkota.getAll()`


## Contoh Penggunaan
print kota Bima
```python
print(loadkota.search('69')['nama_kota'])
```

### note:
- di file app.py sudah di import dan di initialize, jadi tinggal pake