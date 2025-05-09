# Panduan Penggunaan Lanjutan

Panduan ini membahas fitur-fitur lanjutan dan teknik untuk memaksimalkan penggunaan AI Code Agent.

## Fitur Lanjutan

### Bekerja dengan Beberapa File

Agen dapat menangani operasi kompleks di beberapa file:

```bash
# Memperbarui fungsi terkait di berbagai file
python agent.py "Perbarui sistem login untuk menggunakan token JWT alih-alih cookie sesi" --dry-run

# Refactor komponen bersama
python agent.py "Ekstrak fungsi utilitas umum dari api/*.py ke modul baru utils/api_helpers.py"
```

### Penanda Blok Kustom

Gunakan penanda kustom untuk mendefinisikan region kode tertentu:

```python
# START_CUSTOM_LOGIC
def logika_bisnis_kompleks():
    # kode Anda di sini
# END_CUSTOM_LOGIC
```

Kemudian modifikasi hanya bagian tersebut:
```bash
python agent.py "Optimalkan kode antara penanda START_CUSTOM_LOGIC dan END_CUSTOM_LOGIC"
```

### Konfigurasi Penyedia LLM

#### Pengaturan OpenRouter
Untuk akses ke model-model terkini:

```yaml
openrouter:
  api_key: "kunci_anda"
  model_identifier: "mistralai/mistral-7b-instruct"
  model_generation: "anthropic/claude-2"
```

#### Pengaturan Ollama
Untuk eksekusi model lokal dan privat:

```yaml
ollama:
  base_url: "http://localhost:11434"
  model_identifier: "codellama:13b"
  model_generation: "codellama:34b"
```

### Opsi CLI Lanjutan

```bash
# Kombinasikan beberapa opsi
python agent.py "Refactor autentikasi pengguna" \
  --file_path src/auth.py \
  --llm_provider ollama \
  --model_generation "codellama:34b" \
  --dry-run

# Proses beberapa file
python agent.py "Tambahkan validasi input" \
  --file_path "src/api/*.py" \
  --yes
```

## Kasus Penggunaan Lanjutan

### 1. Refactoring Kompleks

#### Mengkonversi ke Pola Desain
```bash
# Konversi ke Factory Pattern
python agent.py "Refactor kelas DocumentProcessor untuk menggunakan pola Factory untuk berbagai jenis dokumen"

# Implementasi Observer Pattern
python agent.py "Tambahkan pola observer ke UserService untuk memberi tahu layanan terkait tentang perubahan pengguna"
```

#### Perubahan Arsitektur
```bash
# Beralih ke Arsitektur Heksagonal
python agent.py "Restrukturisasi sistem pemrosesan pesanan untuk mengikuti prinsip arsitektur heksagonal"
```

### 2. Optimasi Kinerja

#### Implementasi Caching
```bash
# Menambahkan Redis Caching
python agent.py "Tambahkan caching Redis ke query database yang berat di UserRepository"

# Implementasi Memoization
python agent.py "Tambahkan memoization ke fungsi rekursif di algorithm.py"
```

#### Konversi Async
```bash
# Konversi ke Async
python agent.py "Konversi operasi file sinkron di storage.py untuk menggunakan aiofiles"
```

### 3. Peningkatan Testing

#### Menambahkan Cakupan Test
```bash
# Generate Tests
python agent.py "Generate unit test komprehensif untuk kelas OrderProcessor"

# Tambahkan Property-Based Tests
python agent.py "Tambahkan test berbasis property menggunakan hypothesis untuk fungsi validasi data"
```

## Praktik Terbaik untuk Penggunaan Lanjutan

### 1. Strategi Perubahan Kompleks

1. **Memecah Perubahan**
   ```bash
   # Langkah 1: Ekstrak interface
   python agent.py "Ekstrak interface dari kelas UserService"
   
   # Langkah 2: Buat implementasi
   python agent.py "Buat implementasi MongoDB untuk interface UserService"
   
   # Langkah 3: Perbarui dependensi
   python agent.py "Perbarui referensi service untuk menggunakan interface UserService"
   ```

2. **Gunakan Dry Run**
   ```bash
   # Preview perubahan kompleks
   python agent.py "Implementasikan pola CQRS untuk pemrosesan pesanan" --dry-run
   ```

### 2. Bekerja dengan Codebase Besar

1. **Kontrol Lingkup**
   ```bash
   # Batasi ke modul tertentu
   python agent.py "Perbarui logging" --file_path "src/logging/*.py"
   ```

2. **Perubahan Bertahap**
   ```bash
   # Fase 1
   python agent.py "Konversi kelas User untuk menggunakan dataclass, pertahankan method yang ada"
   
   # Fase 2
   python agent.py "Tambahkan validasi ke field dataclass User"
   ```

### 3. Alur Kerja Kustom

1. **Kombinasi dengan Git**
   ```bash
   # Buat branch fitur
   git checkout -b fitur/auth-baru
   
   # Buat perubahan
   python agent.py "Implementasikan autentikasi OAuth2"
   
   # Review dan commit
   git add .
   git commit -m "feat: implementasi autentikasi OAuth2"
   ```

2. **Integrasi CI/CD**
   ```bash
   # Perbarui GitHub Actions
   python agent.py "Tambahkan langkah pemeriksaan tipe ke pipeline CI di .github/workflows/ci.yml"
   ```

## Konfigurasi Lanjutan

### Strategi Backup Kustom
```yaml
backup:
  enabled: true
  max_backups: 5
  path: "./backups"
  format: "{filename}.{timestamp}.bak"
```

### Konfigurasi Logging
```yaml
logging:
  level: "DEBUG"
  file: "ai_code_agent.log"
  format: "%(asctime)s - %(levelname)s - %(message)s"
```

## Mengatasi Masalah Lanjutan

1. **Masalah Pemilihan Model**
   - Coba model berbeda untuk tugas berbeda
   - Gunakan model lebih besar untuk refactoring kompleks
   - Gunakan model kode khusus untuk tugas spesifik framework

2. **Optimasi Kinerja**
   - Gunakan model lokal untuk iterasi lebih cepat
   - Gabungkan perubahan serupa
   - Manfaatkan fitur pemrosesan paralel

3. **Navigasi Codebase Kompleks**
   - Gunakan penanda kustom untuk bagian kompleks
   - Pecah file besar
   - Pertahankan struktur kode yang konsisten

## Langkah Selanjutnya

- Berkontribusi pada proyek
- Bagikan kasus penggunaan lanjutan Anda
- Bergabung dengan komunitas pengembang
- Jelajahi kemungkinan integrasi

Ingat: Kekuatan besar membawa tanggung jawab besar. Selalu tinjau perubahan yang dihasilkan, terutama untuk modifikasi kompleks.