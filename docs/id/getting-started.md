# Memulai dengan AI Code Agent

Selamat datang di AI Code Agent! Panduan ini akan membantu Anda memulai dengan cepat menggunakan alat modifikasi kode cerdas kami.

## Mulai Cepat

1. **Prasyarat**
   - Python 3.8 atau lebih tinggi
   - pip package manager
   - (Opsional) Ollama untuk model lokal

2. **Instalasi**
   ```bash
   git clone [URL_REPOSITORY_ANDA]
   cd ai-code-agent
   python -m venv venv
   source venv/bin/activate  # Di Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Konfigurasi**
   ```bash
   cp config_agent.yaml.example config_agent.yaml
   ```
   Edit `config_agent.yaml` dengan pengaturan yang Anda inginkan:
   ```yaml
   openrouter:
     api_key: "API_KEY_ANDA"
   ollama:
     base_url: "http://localhost:11434"
   ```

4. **Perintah Pertama**
   ```bash
   python agent.py "Tambahkan docstring ke hello.py yang menjelaskan apa yang dilakukan fungsi greet"
   ```

## Konsep Dasar

- **Perintah Bahasa Alami**: Cukup jelaskan apa yang ingin Anda ubah dalam bahasa sehari-hari
- **Deteksi File Pintar**: Agen secara otomatis menemukan file yang tepat
- **Operasi Aman**: Selalu menampilkan preview perubahan dan meminta konfirmasi
- **Sistem Backup**: Secara otomatis mem-backup file sebelum modifikasi

## Langkah Selanjutnya

- Lihat [Tutorial](tutorial.md) kami untuk contoh lebih detail
- Baca [Panduan Pemula](beginner-guide.md) untuk pemahaman lebih dalam
- Jelajahi [Penggunaan Lanjutan](advanced-usage.md) untuk fitur-fitur canggih

## Mendapatkan Bantuan

Jika Anda mengalami masalah:
1. Periksa pesan error untuk panduan spesifik
2. Tinjau [Panduan Pemecahan Masalah](troubleshooting.md)
3. Buka issue di repository GitHub kami