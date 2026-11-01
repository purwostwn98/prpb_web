# Catatan: Respons API IoT Tekanan Filter Solar Terlalu Lambat

**Dari:** Tim Sofipremas (sofipremas.ums.ac.id)
**Tanggal pengukuran:** 1 November 2026
**Endpoint:** `GET https://iot.ums-biroti.id/api/S01/?device_id=<device_id>`

## Ringkasan

Endpoint di atas membutuhkan **sekitar 20 detik sebelum mulai mengirim data**, lalu mengirim **seluruh riwayat perangkat (sekitar 30 MB)**. Total waktu satu permintaan sekitar **51 detik**. Akibatnya grafik tekanan filter solar di dashboard Sofipremas dan di aplikasi driver tidak bisa tampil, karena aplikasi berhenti menunggu setelah 15 detik.

Token yang kami pakai valid (respons `200`), dan jaringan kami tidak bermasalah. Jadi yang lambat adalah pemrosesan di sisi server API.

## Hasil pengukuran

Contoh perangkat: `ACL-0002-AT`. Diukur dengan `curl` dari komputer pengembang. Uji tanpa token juga dijalankan dari server aplikasi Sofipremas, dengan hasil yang sama cepatnya. Dari server aplikasi, permintaan dengan token juga habis waktu setelah 15 detik.

| Permintaan | Status | Waktu sampai byte pertama | Total waktu | Ukuran respons |
|---|---|---|---|---|
| Tanpa token | 401 | — | 0,09–0,31 detik | — |
| Dengan token | 200 | **20,4 detik** | **51,4 detik** | **29.956.423 byte (~30 MB)** |
| Dengan token + `&limit=1` | 200 | 22,2 detik | — | tetap mengirim data penuh |
| Dengan token + `&page_size=1` | 200 | 22,2 detik | — | tetap mengirim data penuh |
| Dengan token + `&ordering=-id&limit=1` | 200 | 24,2 detik | — | tetap mengirim data penuh |

Pada tiga baris terakhir pengukuran kami hentikan setelah 40 detik. Waktu sampai byte pertama yang tidak berubah menunjukkan parameter `limit`, `page_size`, dan `ordering` **diabaikan** oleh endpoint.

Cara mengulang pengukuran:

```bash
curl -s -o /dev/null \
  -H "Authorization: Token <TOKEN>" \
  -w "status=%{http_code} ttfb=%{time_starttransfer}s total=%{time_total}s size=%{size_download}\n" \
  "https://iot.ums-biroti.id/api/S01/?device_id=ACL-0002-AT"
```

## Data yang sebenarnya kami butuhkan

Sofipremas hanya memakai field `timestamp` dan `pressure_value`, untuk dua keperluan:

1. **Pembacaan terakhir per perangkat**, untuk kartu tekanan filter di dashboard truk. Cukup 1 data.
2. **Pembacaan 7 hari terakhir per perangkat**, untuk grafik tren di aplikasi driver. Cukup data dalam rentang tanggal tersebut.

## Permintaan perbaikan

Salah satu dari pilihan berikut sudah cukup untuk kami:

1. **Endpoint pembacaan terakhir.** Misalnya `GET /api/S01/latest/?device_id=...`, yang mengembalikan satu data terbaru.
2. **Filter rentang waktu.** Misalnya `GET /api/S01/?device_id=...&from=2026-10-25&to=2026-11-01`, yang hanya mengembalikan data dalam rentang tersebut.
3. **Pagination dan urutan.** Dukungan `limit` atau `page_size` dan `ordering=-timestamp`, supaya kami bisa mengambil N data terbaru.

Kami juga menyarankan menambah index database pada kolom `device_id` dan `timestamp`. Waktu tunggu 20 detik sebelum byte pertama mengarah pada query yang membaca seluruh tabel.

Targetnya, satu permintaan selesai di bawah **2 detik**. Batas tunggu aplikasi kami 15 detik.

## Kontak

Kalau perlu informasi tambahan atau ingin menguji perubahan bersama, silakan hubungi tim Sofipremas.

---

## Lampiran internal: mengaktifkan kembali fitur tekanan IoT

> Bagian ini untuk tim Sofipremas. Hapus bagian ini sebelum catatan dikirim ke pengelola API IoT.

Sejak 1 November 2026, fitur tekanan filter dari IoT **dinonaktifkan**. Selama nonaktif:

- Aplikasi tidak memanggil API IoT sama sekali.
- Dashboard truk menampilkan pemberitahuan "dinonaktifkan sementara".
- Endpoint `/api/pressure-cart-data/` di aplikasi driver mengembalikan 7 titik bernilai 0.

Fitur ini dikendalikan oleh satu saklar di `.env`, yaitu `IOT_PRESSURE_ENABLED`. Nilai bawaannya `False`.

### 1. Pastikan API IoT sudah cepat

Jalankan perintah pengukuran di atas. Lanjutkan hanya jika `ttfb` dan `total` sudah di bawah ±2 detik.

Kalau pengelola menyediakan endpoint atau parameter baru, misalnya `latest` atau `from`/`to`, sesuaikan dulu kodenya:

- `core/utils.py`, fungsi `get_fuel_filter_pressure_from_api`. Saat ini fungsi ini membaca data pertama dari array sebagai pembacaan terbaru.
- `api/serializers.py`, `PressureChartDataSerializer`. Grafik 7 hari aplikasi driver saat ini membaca `response['results']`, padahal fungsi di atas hanya mengembalikan satu data. Bagian ini perlu diubah agar memakai data 7 hari dari endpoint yang baru.

### 2. Aktifkan di server

```bash
ssh prpb@10.3.11.102
cd ~/manajemen_aset

# token harus sudah ada (hasilnya harus 1)
grep -c '^IOT_API_TOKEN=' .env

# nyalakan saklar
echo 'IOT_PRESSURE_ENABLED=True' >> .env

# env_file hanya dibaca saat container dibuat; "restart" saja tidak cukup
docker compose up -d --force-recreate
```

### 3. Periksa hasilnya

```bash
docker compose exec -T web python manage.py shell -c "
from django.conf import settings
from core.utils import get_fuel_filter_pressure_from_api
print('enabled:', settings.IOT_PRESSURE_ENABLED)
print(get_fuel_filter_pressure_from_api('ACL-0002-AT'))
"
```

Hasilnya harus `enabled: True` dan sebuah data berisi `pressure_value` dan `timestamp`, bukan `None`. Setelah itu buka Dashboard Truck untuk truk yang memakai perangkat `ACL-0002-AT`. Grafik tekanan seharusnya muncul dan bertambah setiap 10 detik.

### Menonaktifkan lagi

Ubah baris tadi menjadi `IOT_PRESSURE_ENABLED=False`, atau hapus barisnya, lalu jalankan lagi `docker compose up -d --force-recreate`.
