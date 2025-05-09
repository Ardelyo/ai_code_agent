# Panduan Pemula AI Code Agent

Panduan ini dirancang untuk membantu pengguna baru memahami dan menggunakan AI Code Agent secara efektif. Kami akan membahas konsep dasar dan memberikan banyak contoh.

## Memahami Cara Kerjanya

AI Code Agent bekerja dalam empat langkah sederhana:

1. **Anda membuat permintaan** dalam bahasa sehari-hari
2. **AI memahami dan merencanakan** perubahan
3. **Perubahan ditampilkan** untuk ditinjau
4. **Anda mengkonfirmasi** dan perubahan diterapkan

## Kasus Penggunaan Umum

### 1. Menambahkan Dokumentasi
```bash
python agent.py "Tambahkan docstring ke semua fungsi di utils.py"
```

### 2. Memperbaiki Bug Sederhana
```bash
python agent.py "Perbaiki kesalahan off-by-one di loop range dalam fungsi process_list"
```

### 3. Menambahkan Fitur Baru
```bash
python agent.py "Tambahkan validasi input ke fungsi calculate_age untuk memastikan tanggal tidak di masa depan"
```

### 4. Refactoring Kode
```bash
python agent.py "Ubah perulangan for di parse_data menjadi list comprehension"
```

## Praktik Terbaik

1. **Spesifik dalam Permintaan**
   - Bagus: "Tambahkan type hints parameter ke fungsi process_user di auth.py"
   - Kurang Bagus: "Tambahkan beberapa type hints di suatu tempat"

2. **Mulai dari Yang Kecil**
   - Buat perubahan kecil dan terfokus terlebih dahulu
   - Tingkatkan ke modifikasi yang lebih kompleks

3. **Tinjau Perubahan**
   - Selalu periksa preview
   - Gunakan `--dry-run` untuk perubahan kompleks

4. **Gunakan Fitur Keamanan**
   - Jangan nonaktifkan backup otomatis kecuali diperlukan
   - Jaga keamanan file konfigurasi Anda

## Parameter Umum

- `--dry-run`: Preview perubahan tanpa menerapkannya
- `--file_path`: Tentukan file yang akan dimodifikasi
- `--no-backup`: Nonaktifkan backup otomatis (gunakan dengan hati-hati!)
- `--yes`: Lewati konfirmasi (gunakan dengan hati-hati!)

## Tips untuk Sukses

1. **Instruksi yang Jelas**
   - Sebutkan nama file spesifik jika diketahui
   - Jelaskan hasil yang diinginkan, bukan hanya masalahnya

2. **Memahami Konteks**
   - Agen dapat melihat seluruh file
   - Agen memahami struktur dan pola kode

3. **Penggunaan Interaktif**
   - Mulai dengan perubahan sederhana
   - Bangun kepercayaan secara bertahap

## Langkah Selanjutnya

- Coba contoh-contoh di [Tutorial](tutorial.md) kami
- Jelajahi [Penggunaan Lanjutan](advanced-usage.md)
- Lihat contoh dunia nyata di [Studi Kasus](case-studies.md)

Ingat: AI Code Agent adalah alat untuk membantu Anda, bukan menggantikan penilaian Anda. Selalu tinjau perubahan sebelum menerapkannya!