# Dashboard KB Jawa Timur 2025

Dashboard Streamlit dari tiga proyek magang BKKBN Jatim:

| Halaman | Isi |
|---|---|
| Beranda | Cerita tiga bab + daftar daerah sorotan lintas proyek |
| Profil Daerah | Satu kab/kota: capaian, prioritas indikator, dukungan layanan |
| Capaian KB | Peta, daerah prioritas, kelompok daerah, 8 pertanyaan statistik (dihitung langsung), simulasi bobot |
| Dukungan Layanan | Skor dukungan, tipologi, stok alat KB, prioritas dengan bobot interaktif |
| Suara Masyarakat | Nada komentar, pertanyaan publik, topik, saran KIE |
| Panduan & Istilah | Arti warna, glosarium, asal data |

## Menjalankan
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Menguji
```bash
pip install -r requirements-dev.txt
pytest -q
```
Tes memeriksa 38 daerah, hitung ulang indeks dan uji Kruskal-Wallis terhadap hasil notebook, skor WOA, dan menjalankan semua halaman.

## Deploy
1. Dorong folder ini ke repositori GitHub (CI di `.github/workflows/ci.yml` otomatis jalan).
2. Di https://share.streamlit.io pilih repositori, file utama `app.py`.

## Struktur
```
app.py            navigasi
views/            halaman
kbdash/           data.py (muat data, WOA), charts.py (grafik, peta), theme.py (warna, CSS)
data/             p1_wilayah.csv, p2_wilayah.csv, *_hasil.json, jatim_kabkota.geojson
assets/           gambar dari notebook Proyek 3
tests/            pytest
```

## Asal data
File CSV/GeoJSON mentah tidak tersedia saat aplikasi dibuat, jadi tabel per kab/kota dan batas wilayah **dipulihkan dari keluaran notebook** (peta interaktif) lalu dicocokkan dengan hasil tercetak; angka uji dan ringkasan Proyek 3 disalin dari keluaran sel. Nilai indikator SiPerindu dan nilai Proyek 2 tersimpan dengan ketepatan seperti tampil di notebook (1-2 desimal).
Untuk memakai data asli, ekspor ulang dengan nama kolom yang sama ke `data/` (lihat header CSV). Komentar YouTube individual sengaja tidak disertakan.

## Batasan
- Model sentimen (IndoRoBERTa) dijalankan di notebook, bukan di aplikasi; akurasinya belum dievaluasi terhadap label manual.
- Prioritas = lebih rendah dari nilai Jatim, bukan target resmi. Kesesuaian dan prioritas bukan sebab-akibat.
