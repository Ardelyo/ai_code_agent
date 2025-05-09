# Referensi API

Dokumen ini menyediakan informasi detail tentang antarmuka baris perintah AI Code Agent, opsi konfigurasi, dan API programatik.

## Antarmuka Baris Perintah

### Penggunaan Dasar

```bash
python agent.py "<instruksi>" [opsi]
```

### Opsi Baris Perintah

| Opsi | Tipe | Default | Deskripsi |
|--------|------|---------|-------------|
| `--file_path` | string | None | Path file spesifik untuk dimodifikasi. Bisa menggunakan pola glob. |
| `--llm_provider` | string | dari config | Penyedia LLM yang digunakan ('openrouter' atau 'ollama'). |
| `--model_identifier` | string | dari config | Model untuk identifikasi blok kode. |
| `--model_generation` | string | dari config | Model untuk generasi kode. |
| `--dry-run` | flag | False | Preview perubahan tanpa menerapkannya. |
| `--no-backup` | flag | False | Nonaktifkan backup file otomatis. |
| `--indentation_mode` | string | "match_original_block_start" | Cara menangani indentasi ("match_original_block_start" atau "as_is"). |
| `--yes` | flag | False | Lewati prompt konfirmasi. |
| `--openrouter_api_key` | string | dari config | Kunci API OpenRouter. |
| `--ollama_base_url` | string | dari config | URL dasar Ollama. |

### Variabel Lingkungan

| Variabel | Deskripsi |
|----------|-------------|
| `OPENROUTER_API_KEY` | Kunci API untuk OpenRouter |
| `OLLAMA_BASE_URL` | URL dasar untuk API Ollama |
| `AI_CODE_AGENT_CONFIG` | Path ke file konfigurasi |

## File Konfigurasi

File `config_agent.yaml` mendukung opsi konfigurasi berikut:

```yaml
openrouter:
  api_key: string
  model_identifier: string
  model_generation: string

ollama:
  base_url: string
  model_identifier: string
  model_generation: string

default_provider: "openrouter" | "ollama"

backup:
  enabled: boolean
  max_backups: number
  path: string
  format: string

logging:
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR"
  file: string
  format: string

indentation:
  default_mode: "match_original_block_start" | "as_is"
```

### Detail Konfigurasi

#### Pengaturan OpenRouter

```yaml
openrouter:
  api_key: "kunci_api_anda"  # Wajib untuk OpenRouter
  model_identifier: "mistralai/mistral-7b-instruct"  # Model default untuk identifikasi
  model_generation: "anthropic/claude-2"  # Model default untuk generasi
```

#### Pengaturan Ollama

```yaml
ollama:
  base_url: "http://localhost:11434"  # URL default Ollama
  model_identifier: "codellama:13b"  # Model default untuk identifikasi
  model_generation: "codellama:34b"  # Model default untuk generasi
```

#### Pengaturan Backup

```yaml
backup:
  enabled: true  # Aktifkan/nonaktifkan backup otomatis
  max_backups: 5  # Jumlah maksimum file backup yang disimpan
  path: "./backups"  # Direktori untuk file backup
  format: "{filename}.{timestamp}.bak"  # Format nama file backup
```

#### Pengaturan Logging

```yaml
logging:
  level: "INFO"  # Level logging (DEBUG, INFO, WARNING, ERROR)
  file: "ai_code_agent.log"  # Path file log
  format: "%(asctime)s - %(levelname)s - %(message)s"  # Format log
```

## Penanda Blok Kustom

Agen mendukung penanda blok kustom untuk mendefinisikan region kode tertentu:

### Penanda Berbasis Komentar

```python
# START_CUSTOM_LOGIC
def fungsi_anda():
    pass
# END_CUSTOM_LOGIC
```

### Penanda Berbasis Region (Multiple Bahasa)

```python
# region Logika Kustom
def fungsi_python():
    pass
# endregion
```

```csharp
#region Logika Bisnis
public void MetodeCSharp()
{
}
#endregion
```

```javascript
//#region Rute API
const router = express.Router();
//#endregion
```

## Penanganan Error

Agen menyediakan pesan error dan logging yang detail:

### Kode Error Umum

| Kode | Deskripsi | Solusi |
|------|-------------|----------|
| E001 | File tidak ditemukan | Periksa path file dan izin |
| E002 | Konfigurasi tidak valid | Verifikasi sintaks config_agent.yaml |
| E003 | Autentikasi API gagal | Periksa konfigurasi kunci API |
| E004 | Model tidak tersedia | Verifikasi nama model atau coba alternatif |
| E005 | Error parsing | Periksa sintaks blok kode |

### Pemulihan Error

Agen menyertakan mekanisme pemulihan error otomatis:

1. Pembuatan backup otomatis sebelum modifikasi
2. Rollback pada operasi yang gagal
3. Logging error detail untuk debugging

## API Integrasi

Untuk penggunaan programatik, agen menyediakan API Python:

```python
from ai_code_agent import Agent, Config

# Inisialisasi agen dengan konfigurasi kustom
agent = Agent(Config.from_file("config_agent.yaml"))

# Proses permintaan modifikasi kode
result = agent.process_request(
    instruction="Tambahkan penanganan error ke fungsi",
    file_path="src/main.py",
    dry_run=True
)

# Dapatkan preview modifikasi
preview = result.get_preview()

# Terapkan perubahan
if result.is_valid():
    result.apply()
```

### Metode API

| Metode | Deskripsi |
|--------|-------------|
| `process_request()` | Proses permintaan modifikasi |
| `get_preview()` | Dapatkan preview perubahan |
| `apply_changes()` | Terapkan modifikasi |
| `rollback()` | Kembalikan perubahan |
| `validate()` | Validasi perubahan yang diusulkan |

## Praktik Terbaik

### Manajemen Konfigurasi

1. Gunakan variabel lingkungan untuk data sensitif
2. Version control config_agent.yaml.example Anda
3. Dokumentasikan konfigurasi kustom

### Penanganan Error

1. Selalu gunakan `--dry-run` untuk perubahan kritis
2. Aktifkan logging untuk debugging
3. Pertahankan backup reguler

### Optimasi Kinerja

1. Gunakan model lokal untuk iterasi cepat
2. Gabungkan perubahan serupa
3. Optimalkan pemilihan model untuk tugas

## Pemecahan Masalah

### Masalah Umum

1. **Kegagalan Autentikasi**
   - Verifikasi kunci API
   - Periksa variabel lingkungan
   - Validasi file konfigurasi

2. **Error Model**
   - Verifikasi ketersediaan model
   - Periksa status penyedia
   - Coba model alternatif

3. **Operasi File**
   - Periksa izin file
   - Verifikasi path file
   - Pastikan ruang disk mencukupi

### Mode Debug

Aktifkan logging debug untuk informasi detail:

```yaml
logging:
  level: "DEBUG"
  file: "debug.log"
```

## Dukungan

Untuk bantuan tambahan:

1. Periksa [Panduan Pemecahan Masalah](troubleshooting.md)
2. Tinjau [Masalah Umum](common-issues.md)
3. Buka issue di GitHub