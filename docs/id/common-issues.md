# Masalah Umum

Dokumen ini mencantumkan masalah yang sering ditemui dan solusinya saat menggunakan AI Code Agent.

## Masalah Terkait Model

### 1. Model Tidak Merespons

**Masalah**: Model terlalu lama merespons atau timeout.

**Solusi**:
- Coba model yang berbeda (misalnya, beralih dari OpenRouter ke Ollama)
- Gunakan model yang lebih kecil dan cepat untuk tugas sederhana
- Periksa koneksi internet Anda
- Tingkatkan pengaturan timeout di konfigurasi

### 2. Generasi Kode Buruk

**Masalah**: Kode yang dihasilkan tidak benar atau berkualitas rendah.

**Solusi**:
- Berikan instruksi yang lebih spesifik
- Berikan lebih banyak konteks dalam prompt Anda
- Coba model berbeda yang khusus untuk kode
- Pecah perubahan kompleks menjadi langkah-langkah kecil

### 3. Model Tidak Tersedia

**Masalah**: Model yang dipilih tidak dapat diakses.

**Solusi**:
- Verifikasi nama model di konfigurasi
- Periksa apakah Anda memiliki akses ke model
- Pastikan kunci API memiliki izin yang diperlukan
- Coba model alternatif

## Operasi File

### 1. File Tidak Ditemukan

**Masalah**: Agen tidak dapat menemukan file target.

**Solusi**:
- Periksa path file sudah benar
- Verifikasi file ada di workspace
- Gunakan path absolut jika diperlukan
- Periksa izin file

### 2. Modifikasi File Gagal

**Masalah**: Perubahan tidak dapat diterapkan ke file.

**Solusi**:
- Pastikan file tidak read-only
- Periksa file tidak sedang dibuka di program lain
- Verifikasi ruang disk mencukupi
- Periksa izin sistem file
- Gunakan `--dry-run` untuk menguji perubahan terlebih dahulu

### 3. Masalah Backup

**Masalah**: Tidak dapat membuat file backup.

**Solusi**:
- Periksa ruang disk
- Verifikasi izin direktori backup
- Bersihkan backup lama
- Konfigurasi lokasi backup di config_agent.yaml

## Masalah Konfigurasi

### 1. Konfigurasi Tidak Valid

**Masalah**: File konfigurasi tidak dapat dimuat.

**Solusi**:
- Verifikasi sintaks YAML
- Periksa encoding file (gunakan UTF-8)
- Bandingkan dengan config_agent.yaml.example
- Hapus pengaturan bermasalah

### 2. Masalah Kunci API

**Masalah**: Autentikasi API gagal.

**Solusi**:
- Periksa kunci API valid
- Verifikasi kunci dikonfigurasi dengan benar
- Pastikan kunci belum kedaluwarsa
- Periksa konflik variabel lingkungan

### 3. Konfigurasi Model

**Masalah**: Pengaturan model tidak benar.

**Solusi**:
- Verifikasi nama/pengidentifikasi model
- Periksa pengaturan khusus penyedia
- Perbarui ke versi model terbaru
- Gunakan konfigurasi model yang direkomendasikan

## Identifikasi Blok Kode

### 1. Blok Tidak Ditemukan

**Masalah**: Agen tidak dapat menemukan blok kode target.

**Solusi**:
- Lebih spesifik dalam deskripsi blok
- Periksa apakah blok ada di file
- Gunakan nama fungsi/kelas yang tepat
- Coba gunakan penanda kustom

### 2. Blok Yang Dipilih Salah

**Masalah**: Agen memodifikasi bagian kode yang salah.

**Solusi**:
- Gunakan pengidentifikasi yang lebih spesifik
- Tambahkan penanda kustom di sekitar blok target
- Preview perubahan dengan `--dry-run`
- Pecah file kompleks

### 3. Masalah Penanda

**Masalah**: Penanda kustom tidak berfungsi.

**Solusi**:
- Periksa sintaks penanda
- Verifikasi penempatan penanda
- Gunakan nama penanda unik
- Ikuti pedoman format penanda

## Masalah Kinerja

### 1. Operasi Lambat

**Masalah**: Operasi agen terlalu lambat.

**Solusi**:
- Gunakan model lokal melalui Ollama
- Bekerja dengan file yang lebih kecil
- Pecah perubahan besar
- Optimalkan pemilihan model

### 2. Penggunaan Memori

**Masalah**: Konsumsi memori tinggi.

**Solusi**:
- Proses file yang lebih kecil
- Gunakan model yang lebih efisien
- Bersihkan backup lama
- Pantau sumber daya sistem

### 3. Pembatasan Rate

**Masalah**: Batas rate API tercapai.

**Solusi**:
- Gunakan model lokal jika memungkinkan
- Implementasikan pembatasan permintaan
- Gabungkan perubahan serupa
- Tingkatkan paket API jika diperlukan

## Praktik Terbaik untuk Menghindari Masalah

1. **Selalu Uji Terlebih Dahulu**
   - Gunakan `--dry-run` untuk preview
   - Uji pada file sampel
   - Tinjau perubahan dengan teliti

2. **Pertahankan Struktur yang Baik**
   - Jaga file terorganisir
   - Gunakan penamaan yang konsisten
   - Dokumentasikan kode dengan baik

3. **Pemeliharaan Rutin**
   - Perbarui dependensi
   - Bersihkan backup
   - Pantau ruang disk
   - Jaga konfigurasi tetap diperbarui

4. **Konfigurasi yang Tepat**
   - Gunakan kunci API yang aman
   - Konfigurasi logging
   - Atur timeout yang sesuai
   - Dokumentasikan pengaturan kustom

## Mendapatkan Bantuan Lebih Lanjut

Jika Anda menemui masalah yang tidak tercakup di sini:

1. Periksa [Panduan Pemecahan Masalah](troubleshooting.md)
2. Tinjau [Referensi API](api-reference.md)
3. Cari masalah di GitHub
4. Bergabung dengan diskusi komunitas
5. Buat laporan bug yang detail

Ingat untuk selalu menyertakan:
- Pesan error
- Detail konfigurasi
- Langkah-langkah untuk mereproduksi
- Informasi sistem