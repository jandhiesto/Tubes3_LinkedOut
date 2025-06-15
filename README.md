# Tugas Besar 3 IF2211 Strategi Algoritma Semester 2 2024/2025

# Oleh Kelompok: LinkedOut

## Penjelasan Algoritma

### Knuth-Morris-Path (KMP)
Algoritma Knuth-Morris-Pratt, atau yang lebih dikenal sebagai algoritma KMP, adalah algoritma pencocokan string (string matching) yang efisien untuk mencari kemunculan sebuah pola (pattern) dalam teks (text). Algoritma ini dikembangkan oleh Donald Knuth, Vaughan Pratt, dan James H. Morris pada tahun 1977. KMP memanfaatkan informasi dari kegagalan pencocokan sebelumnya untuk menghindari pemeriksaan ulang karakter yang sudah diketahui tidak cocok, sehingga meningkatkan efisiensi dibandingkan pendekatan naif (brute force).

### Boyer-Moore
Algoritma Boyer-Moore adalah algoritma pencocokan string lain yang sangat efisien, dikembangkan oleh Robert S. Boyer dan J Strother Moore pada tahun 1977. Berbeda dengan algoritma KMP yang memeriksa teks dari kiri ke kanan, Boyer-Moore memeriksa teks dari kanan ke kiri (right-to-left). Algoritma ini dikenal karena kemampuannya untuk melompati sejumlah besar karakter dalam teks, terutama ketika pola tidak sering muncul dalam teks.

## _Requirement_ Program
- MySQL
- Python

## Instalasi dan Cara Run Aplikasi

1. Clone Repository

2. Konfigurasi file .env dengan cara buat file copy isi file .env.template atau rename file .env.template menjadi .env lalu ubah bagian
```bash
    DB_PASSWORD="Password SQL anda" (Tanpa tanda "")
``` 
Menjadi Password SQL anda

3. Buat Virtual Environment 
```bash
    python -m venv venv
``` 
4. Aktifkan Virtual Environment
```bash
    source venv/bin/activate
``` 
5. Install requirment
```bash
    pip install -r requirements.txt
``` 

5. Jalankan init_db sekali saja
```bash
    python -m src.init_db
``` 

6. Jalankan jalankan main
```bash
    python -m src.main
``` 

## Author
- Boye Mangaratua Ginting (13523127)
- Muhammad Aulia Azka (13523137)
- Muhammad Rizain Firdaus (13523164)