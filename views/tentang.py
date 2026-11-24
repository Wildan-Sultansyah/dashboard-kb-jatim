import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import streamlit as st
from kbdash import theme as T

T.pasang_halaman("Tentang & Metode", kicker="Dokumentasi",
                 ringkas="Skema Magang Mandiri – Data Analyst, BKKBN Perwakilan Provinsi Jawa Timur (Timja Perencanaan dan Keuangan).")

st.subheader("Tiga proyek")
st.markdown(
    "| Proyek | Pertanyaan | Metode utama | Sumber data |\n|---|---|---|---|\n"
    "| 1 · Capaian KB | Di mana capaian KB tertinggal dan indikator apa yang perlu ditingkatkan? | Indeks z-score, PCA + K-Medoids, uji nonparametrik | SiPerindu 2025, Buku Saku Parameter Kependudukan |\n"
    "| 2 · Dukungan layanan | Apakah dukungan layanan sejalan dengan capaian? Di mana stok kritis? | Moran, LISA, Gi*, tipologi, WOA + sensitivitas | Data faskes/PKB/PUS kantor, SIRIKA/SIGA, hasil Proyek 1 |\n"
    "| 3 · Suara publik | Apa yang dibicarakan publik tentang alokon? | Cleaning teks, IndoRoBERTa + InSet, BERTopic, aturan jenis percakapan | Komentar YouTube (scraping) |")

st.subheader("Cara membaca dashboard")
st.markdown(
    "- **Indeks capaian**: rata-rata z-score lima indikator (arah dibalik bila turun = baik); 0 = rata-rata 38 daerah.\n"
    "- **Prioritas** berarti lebih rendah dari nilai Provinsi Jatim, bukan \"target tidak tercapai\" (target per daerah belum tersedia).\n"
    "- **Kesesuaian** dan **prioritas** bukan sebab-akibat. Bobot dan ambang adalah asumsi peneliti yang diuji sensitivitasnya.\n"
    "- Hasil Proyek 3 berasal dari komentar YouTube, bukan seluruh publik, dan tidak memiliki lokasi.")

st.subheader("Alur pengembangan aplikasi")
st.markdown(
    "1. **Preparation**: data hasil analisis dikemas sebagai CSV/JSON/GeoJSON di folder `data/`; kode dipisah menjadi modul `kbdash/` dan halaman `views/`.\n"
    "2. **Testing**: `pytest` memeriksa integritas data (38 daerah, kecocokan indeks dan peringkat, hitung ulang uji Kruskal-Wallis, skor WOA) dan menjalankan tiap halaman Streamlit (`AppTest`) untuk memastikan tidak ada galat.\n"
    "3. **Deployment**: aplikasi dijalankan dengan `streamlit run app.py`, dapat di-deploy ke Streamlit Community Cloud dari repositori GitHub.\n"
    "4. **CI**: GitHub Actions (`.github/workflows/ci.yml`) menjalankan pengujian pada setiap push dan pull request.")
st.caption("Catatan: dashboard menampilkan hasil agregat. Model sentimen dijalankan di notebook Proyek 3, bukan di dalam aplikasi ini.")

st.subheader("Asal data aplikasi")
st.markdown("Tabel per kab/kota dan batas wilayah dipulihkan dari keluaran notebook (peta interaktif) dan dicocokkan ulang dengan hasil yang tercetak "
            "(indeks, peringkat, klaster, skor prioritas). Hasil uji, tabel, dan ringkasan Proyek 3 disalin dari keluaran notebook. "
            "Batas wilayah: geoBoundaries (CC BY 4.0), tidak menggantikan batas resmi. Untuk memakai file asli, ekspor ulang dari notebook ke format yang sama di folder `data/` (lihat README).")
