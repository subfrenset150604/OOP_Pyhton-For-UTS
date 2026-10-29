# Jawaban UTS Pemrograman Berorientasi Objek - Python

## Isi folder

- `main.py`: program utama, berisi class, aturan bisnis, pembacaan JSON, dan laporan.
- `employee.json`: data 30 pegawai dari soal.
- `sensor_logs.json`: data 30 pembacaan sensor dari soal.

## Cara menjalankan

Pastikan Python 3.10 atau lebih baru sudah terpasang. Ketiga file tersebut harus berada di folder yang sama.

```bash
python main.py
```

Program ini tidak membutuhkan library eksternal; hanya memakai library bawaan Python.

## Penerapan konsep OOP

1. **Inheritance (pewarisan):** `PermanentEmployee` dan `ContractEmployee` mewarisi `Employee`; `DangerSensor`, `WarningSensor`, dan `NormalSensor` mewarisi `SensorReading`.
2. **Method overriding:** kelas turunan mengimplementasikan ulang `calculate_bonus()` atau `recommended_action()`.
3. **Polymorphism:** program memanggil method yang sama pada objek berbeda; hasilnya mengikuti kelas objek tersebut.
4. **Rule-based:** bonus dihitung berdasarkan status pegawai dan kode bonus, sedangkan status sensor diklasifikasikan berdasarkan temperatur.

## Asumsi aturan yang perlu diketahui

PDF soal memberikan data JSON, tetapi tidak mencantumkan besaran bonus maupun batas temperatur. Untuk membuat program dapat diuji, digunakan asumsi berikut di `main.py`:

- `PERF2026`: bonus 10% dari gaji pokok.
- `SENIOR10`: bonus 10% dari gaji pokok.
- `LEAD2026`: bonus 15% dari gaji pokok.
- Bonus diberikan hanya kepada pegawai tetap. Pegawai tanpa kode bonus tidak memperoleh bonus.
- Temperatur >= 85 C diklasifikasikan `DANGER`; temperatur >= 65 C dan < 85 C diklasifikasikan `WARNING`; temperatur < 65 C diklasifikasikan `NORMAL`.
- Status hasil klasifikasi temperatur dibandingkan dengan status di JSON untuk memeriksa konsistensi.

Jika dosen memiliki aturan berbeda, ubah konstanta `BONUS_RATE_BY_CODE`, `DANGER_MIN_TEMPERATURE`, dan `WARNING_MIN_TEMPERATURE` di bagian konfigurasi `main.py`.

## Identitas untuk pengumpulan

Lengkapi identitas berikut sebelum diunggah ke GitHub:

```text
NIM: [isi NIM Anda]
NAMA: [isi nama lengkap Anda]
LINK GITHUB: [isi URL repository GitHub Anda]
```

## Cara mengunggah ke GitHub

Buat repository baru di GitHub, lalu dari terminal pada folder proyek jalankan:

```bash
git init
git add main.py employee.json sensor_logs.json README.md
git commit -m "Jawaban UTS OOP Python"
git branch -M main
git remote add origin https://github.com/USERNAME/NAMA-REPOSITORY.git
git push -u origin main
```

Ganti `USERNAME/NAMA-REPOSITORY` dengan repository Anda sendiri. Jika repository sudah dibuat dan memiliki remote, tidak perlu mengulang `git remote add origin`; periksa remote dengan `git remote -v`.
