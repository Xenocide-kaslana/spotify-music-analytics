# Dashboard Analisis Musik Spotify

Dashboard berbasis Streamlit untuk melihat dan memahami data lagu Spotify. Pengguna dapat memfilter data berdasarkan genre, popularitas, konten eksplisit, dan durasi lagu. Dashboard ini juga menampilkan ringkasan statistik, grafik, serta daftar lagu secara lengkap.

## Fitur Aplikasi

- Ringkasan KPI, seperti jumlah lagu, rata-rata popularitas, rata-rata energi, dan jumlah genre.
- Temuan utama yang diperbarui secara otomatis sesuai filter yang dipilih.
- Grafik distribusi popularitas dan pembagian konten eksplisit.
- Urutan genre berdasarkan popularitas atau jumlah lagu.
- Diagram karakteristik audio, termasuk korelasi dan distribusi fitur.
- Pencarian nama lagu atau nama artis pada halaman Eksplorasi Lagu.
- Tampilan seluruh data lagu yang sesuai dengan hasil filter dan pencarian.
- Pilihan tampilan Gelap dan Terang.
- Informasi sumber data, definisi metrik, proses pengolahan, dan keterbatasan data.

## Persyaratan

Disarankan menggunakan Python 3.10 atau versi yang lebih baru.

## Cara Menjalankan

1. Buka terminal pada folder project.
2. Buat dan aktifkan environment Python:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Pasang semua library yang diperlukan:

```powershell
python -m pip install -r requirements.txt
```

4. Jalankan proses pengolahan data:

```powershell
python src/data_processing.py
```

5. Jalankan dashboard:

```powershell
streamlit run app.py
```

Aplikasi akan dibuka melalui alamat Streamlit yang ditampilkan pada terminal, biasanya `http://localhost:8501`.

## Cara Menggunakan Dashboard

1. Gunakan filter di sidebar untuk memilih genre, rentang popularitas, konten eksplisit, dan durasi.
2. Tekan **Atur Ulang Filter** untuk mengembalikan semua filter ke nilai awal.
3. Pilih **Gelap** atau **Terang** untuk mengubah tema dashboard.
4. Gunakan tab **Ringkasan**, **Eksplorasi Genre**, **Karakteristik Audio**, dan **Eksplorasi Lagu** untuk membuka halaman yang berbeda.
5. Pada halaman Eksplorasi Lagu, gunakan kotak pencarian untuk mencari nama lagu atau artis. Semua hasil yang cocok akan ditampilkan sesuai jumlah hasil yang tersedia; slider hanya digunakan untuk membatasi jumlah baris yang ingin dilihat.

## Proses Pengolahan Data

File sumber tidak diubah langsung oleh aplikasi. Proses pengolahan data dilakukan sebagai berikut:

1. Menghapus kolom `Unnamed: 0` apabila kolom tersebut merupakan indeks lama.
2. Mengisi nama artis, nama album, dan nama lagu yang kosong dengan nilai `Unknown`.
3. Memeriksa kolom angka dan rentang karakteristik audio.
4. Menghapus baris yang benar-benar sama atau duplikat.
5. Menyimpan satu baris untuk setiap `track_id` berdasarkan popularitas tertinggi dan kelengkapan data.
6. Menambahkan kolom `duration_min` untuk menampilkan durasi dalam satuan menit tanpa menghapus `duration_ms`.
7. Menyimpan hasil ke `data/cleaned_spotify_tracks.csv` dan laporan kualitas data ke `data/data_quality.json`.

Jumlah baris hasil pengolahan dapat lebih sedikit daripada data sumber karena satu lagu dapat memiliki beberapa genre dan dipilih satu data dengan popularitas tertinggi.

## Sumber Data

Aplikasi menggunakan [Spotify Tracks Dataset di Kaggle](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset).

Dataset tidak menyediakan tanggal rilis atau tahun. Oleh karena itu, dashboard tidak menampilkan analisis tren berdasarkan waktu.

## Panduan Menyimpan di Streamlit Community Cloud

1. Unggah project ke repository GitHub.
2. Pastikan file dan credential rahasia tidak ikut diunggah ke GitHub.
3. Pastikan `data/dataset.csv` tersedia atau jelaskan proses unduhan dataset yang digunakan.
4. Pada Streamlit Community Cloud, pilih repository yang benar dan jadikan `app.py` sebagai file utama.
5. Pastikan `requirements.txt` tersedia dan lakukan deployment.
6. Uji aplikasi dari environment baru dengan menjalankan `streamlit run app.py`.

Apabila ukuran file CSV terlalu besar, gunakan proses unduhan otomatis atau Git LFS sesuai kebutuhan. Jangan mengunggah data pribadi, data berizin terbatas, atau credential rahasia.

## Penyusun

**RAFFI KURNIAWAN**  
NIM: 241041001  
Program Studi: Manajemen Informatika

## Teknologi yang Digunakan

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
