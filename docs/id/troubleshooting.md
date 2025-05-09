# Panduan Pemecahan Masalah

Panduan ini membantu Anda menyelesaikan masalah umum yang mungkin Anda temui saat menggunakan AI Code Agent.

## Masalah dan Solusi Umum

### Masalah Instalasi

#### Masalah Lingkungan Python

**Masalah**: ImportError atau ModuleNotFoundError
```
ImportError: No module named 'yaml'
```

**Solusi**:
1. Pastikan Anda berada di virtual environment yang benar
   ```bash
   source venv/bin/activate  # Di Windows: venv\Scripts\activate
   ```
2. Instal ulang dependensi
   ```bash
   pip install -r requirements.txt
   ```

#### Masalah Konfigurasi

**Masalah**: File konfigurasi tidak ditemukan
```
FileNotFoundError: config_agent.yaml not found
```

**Solusi**:
1. Salin konfigurasi contoh
   ```bash
   cp config_agent.yaml.example config_agent.yaml
   ```
2. Edit config_agent.yaml dengan pengaturan Anda

### Masalah Koneksi API

#### Masalah OpenRouter

**Masalah**: Autentikasi gagal
```
ERROR: OpenRouter API authentication failed
```

**Solusi**:
1. Verifikasi kunci API Anda di config_agent.yaml
2. Periksa apakah kunci API diatur di variabel lingkungan
3. Pastikan kunci API memiliki izin yang cukup

#### Masalah Ollama

**Masalah**: Tidak dapat terhubung ke Ollama
```
ConnectionError: Failed to connect to http://localhost:11434
```

**Solusi**:
1. Pastikan Ollama sedang berjalan
2. Verifikasi URL dasar di konfigurasi
3. Periksa apakah Ollama dapat diakses dari jaringan Anda

### Masalah Modifikasi Kode

#### Masalah Akses File

**Masalah**: Izin ditolak
```
PermissionError: [Errno 13] Permission denied: 'file.py'
```

**Solusi**:
1. Periksa izin file
2. Jalankan perintah dengan hak akses yang sesuai
3. Pastikan file tidak sedang dibuka di program lain

#### Masalah Backup

**Masalah**: Tidak dapat membuat backup
```
ERROR: Failed to create backup file
```

**Solusi**:
1. Periksa ruang disk
2. Verifikasi izin direktori backup
3. Bersihkan backup lama menggunakan:
   ```bash
   python agent.py --cleanup-backups
   ```

### Masalah Terkait Model

#### Masalah Memuat Model

**Masalah**: Model tidak tersedia
```
ERROR: Model 'model_name' not found
```

**Solusi**:
1. Verifikasi nama model di konfigurasi
2. Periksa apakah model tersedia di penyedia Anda
3. Coba model alternatif

#### Masalah Generasi

**Masalah**: Timeout saat generasi kode
```
ERROR: Request timed out after 60 seconds
```

**Solusi**:
1. Coba blok kode yang lebih kecil
2. Gunakan model lokal melalui Ollama
3. Tingkatkan timeout di konfigurasi

## Pemecahan Masalah Lanjutan

### Mode Debug

Aktifkan logging debug untuk informasi detail:

```yaml
logging:
  level: "DEBUG"
  file: "debug.log"
```

### Analisis Log

Pola log umum dan artinya:

1. **Kegagalan Identifikasi Blok**
   ```
   DEBUG: Failed to identify code block in file.py
   ```
   - Periksa apakah kode target ada
   - Verifikasi isi file
   - Gunakan instruksi yang lebih spesifik

2. **Masalah Respons Model**
   ```
   DEBUG: Invalid model response format
   ```
   - Coba model yang berbeda
   - Sederhanakan permintaan
   - Periksa konfigurasi model

3. **Error Operasi File**
   ```
   DEBUG: Failed to apply changes to file.py
   ```
   - Periksa izin file
   - Verifikasi path file
   - Pastikan ruang disk mencukupi

### Langkah Pemulihan

Jika terjadi masalah:

1. **Periksa Backup**
   - Lihat di direktori backup
   - Pulihkan dari backup jika diperlukan
   - Verifikasi integritas file

2. **Reset Konfigurasi**
   ```bash
   cp config_agent.yaml.example config_agent.yaml
   ```

3. **Bersihkan Lingkungan**
   ```bash
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Optimasi Kinerja

### Operasi Lambat

Jika operasi berjalan lambat:

1. **Gunakan Model Lokal**
   - Konfigurasi Ollama
   - Gunakan model yang lebih kecil
   - Cache operasi yang sering digunakan

2. **Optimalkan Operasi File**
   - Bekerja dengan file yang lebih kecil
   - Gunakan path file spesifik
   - Gabungkan perubahan serupa

3. **Masalah Jaringan**
   - Periksa koneksi internet
   - Gunakan model yang di-cache jika memungkinkan
   - Konfigurasi timeout yang sesuai

## Mendapatkan Bantuan

Jika Anda masih mengalami masalah:

1. **Periksa Dokumentasi**
   - Tinjau panduan pemecahan masalah ini
   - Periksa [Referensi API](api-reference.md)
   - Baca panduan [Penggunaan Lanjutan](advanced-usage.md)

2. **Dukungan Komunitas**
   - Cari masalah yang ada di GitHub
   - Periksa diskusi komunitas
   - Bagikan contoh minimal yang dapat direproduksi

3. **Laporkan Bug**
   - Sertakan pesan error
   - Berikan detail konfigurasi
   - Bagikan langkah-langkah untuk mereproduksi

## Tips Pencegahan

1. **Pemeliharaan Rutin**
   - Perbarui dependensi
   - Bersihkan backup lama
   - Pantau ruang disk

2. **Praktik Terbaik**
   - Gunakan version control
   - Buat perubahan bertahap
   - Uji perubahan secara terisolasi

3. **Manajemen Konfigurasi**
   - Jaga keamanan data sensitif
   - Dokumentasikan pengaturan kustom
   - Pertahankan backup konfigurasi

Ingat: Selalu gunakan `--dry-run` untuk perubahan kritis dan pertahankan backup file penting.