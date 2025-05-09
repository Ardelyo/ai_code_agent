# Tutorial AI Code Agent

Tutorial ini akan memandu Anda melalui contoh penggunaan AI Code Agent dari kasus penggunaan dasar hingga lanjutan.

## Contoh Dasar

### 1. Menambahkan Dokumentasi
Mari mulai dengan contoh sederhana menambahkan dokumentasi ke fungsi:

```python
# Kode awal di calc.py
def add(a, b):
    return a + b
```

Perintah:
```bash
python agent.py "Tambahkan docstring ke fungsi add di calc.py yang menjelaskan bahwa fungsi ini menambahkan dua angka dan mengembalikan jumlahnya"
```

Agen akan menambahkan dokumentasi yang tepat:
```python
def add(a, b):
    """
    Menambahkan dua angka dan mengembalikan jumlahnya.

    Args:
        a: Angka pertama untuk ditambahkan
        b: Angka kedua untuk ditambahkan

    Returns:
        Jumlah dari a dan b
    """
    return a + b
```

### 2. Refactoring Kode
Mari tingkatkan keterbacaan kode:

```python
# Kode awal di data_processor.py
def process_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result
```

Perintah:
```bash
python agent.py "Ubah perulangan for di process_data menjadi list comprehension"
```

Agen akan merefaktor menjadi:
```python
def process_data(items):
    return [item * 2 for item in items if item > 0]
```

## Contoh Menengah

### 1. Menambahkan Penanganan Error
Menambahkan penanganan error yang kuat ke kode yang ada:

```python
# Kode awal di user_service.py
def get_user(user_id):
    data = database.query(f"SELECT * FROM users WHERE id = {user_id}")
    return data
```

Perintah:
```bash
python agent.py "Tambahkan penanganan error yang tepat ke fungsi get_user termasuk ID tidak valid dan error koneksi database"
```

Agen akan meningkatkan kode dengan penanganan error yang tepat:
```python
def get_user(user_id):
    """
    Mengambil data pengguna dari database.

    Args:
        user_id: ID pengguna yang akan diambil

    Returns:
        dict: Data pengguna jika ditemukan

    Raises:
        ValueError: Jika user_id tidak valid
        DatabaseError: Jika koneksi database gagal
        UserNotFoundError: Jika pengguna tidak ditemukan
    """
    try:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("ID pengguna tidak valid")
        
        data = database.query(f"SELECT * FROM users WHERE id = %s", (user_id,))
        if not data:
            raise UserNotFoundError(f"Pengguna dengan ID {user_id} tidak ditemukan")
        
        return data
    except DatabaseError as e:
        logger.error(f"Error database saat mengambil pengguna {user_id}: {e}")
        raise DatabaseError(f"Gagal mengambil data pengguna: {e}") from e
```

## Contoh Lanjutan

### 1. Refactoring Kompleks
Mengubah fungsi sinkron menjadi asinkron:

Perintah:
```bash
python agent.py "Ubah fungsi fetch_user_data menjadi async dan gunakan aiohttp alih-alih requests"
```

Agen akan menangani transformasi kompleks, termasuk:
- Mengubah signature fungsi
- Memperbarui dependensi
- Mengkonversi ke sintaks async/await
- Mempertahankan penanganan error
- Memperbarui pemanggilan fungsi terkait

### 2. Menambahkan Fitur Baru
Menambahkan fungsionalitas baru sambil mempertahankan kode yang ada:

Perintah:
```bash
python agent.py "Tambahkan dukungan caching ke fungsi get_weather menggunakan Redis dengan waktu kadaluarsa 30 menit"
```

Agen akan:
1. Menambahkan dependensi Redis
2. Mengimplementasikan logika caching
3. Mempertahankan penanganan error yang ada
4. Menambahkan invalidasi cache

## Praktik Terbaik

1. **Mulai dengan Tujuan yang Jelas**
   - Spesifik tentang apa yang ingin diubah
   - Sebutkan nama file jika memungkinkan
   - Jelaskan hasil yang diinginkan

2. **Tinjau Perubahan**
   - Gunakan `--dry-run` untuk perubahan kompleks
   - Periksa kode yang dihasilkan dengan teliti
   - Verifikasi penanganan error

3. **Pengembangan Bertahap**
   - Buat satu perubahan pada satu waktu
   - Uji setelah setiap modifikasi
   - Bangun menuju perubahan kompleks

## Tips Lanjutan

1. **Menggunakan Beberapa File**
   ```bash
   python agent.py "Perbarui semua fungsi endpoint API di api/*.py untuk menyertakan pembatasan rate"
   ```

2. **Gaya Konsisten**
   ```bash
   python agent.py "Format semua fungsi di utils.py agar mengikuti PEP 8"
   ```

3. **Pola Kompleks**
   ```bash
   python agent.py "Implementasikan pola observer untuk kelas UserService"
   ```

## Langkah Selanjutnya

- Jelajahi [Penggunaan Lanjutan](advanced-usage.md) untuk skenario yang lebih kompleks
- Lihat [Referensi API](api-reference.md) untuk opsi perintah terperinci
- Bergabung dengan komunitas kami untuk berbagi kasus penggunaan dan tips

Ingat: AI Code Agent adalah alat yang kuat, tetapi selalu tinjau hasilnya. Ini dirancang untuk membantu, bukan menggantikan, keahlian pengembangan Anda.