import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import streamlit as st

from kbdash import theme as T
from kbdash.teks import GLOSARIUM, INDIKATOR_AWAM

T.pasang_halaman("Panduan & Istilah", kicker="Cara membaca dashboard ini",
                 ringkas="Bingung dengan sebuah istilah atau warna? Semua dijelaskan di sini dengan bahasa sehari-hari.",
                 warna=("#0ca678", "#1c7ed6"))

st.subheader("Arti warna")
c = st.columns(3)
for col, (w, judul, isi) in zip(c, [(T.BIRU, "Biru = baik", "Capaian tinggi, dukungan kuat, atau komentar positif."),
                                    (T.EMAS, "Kuning = sedang / netral", "Capaian tengah-tengah atau komentar netral."),
                                    (T.PINK, "Merah muda = perlu perhatian", "Capaian rendah, dukungan lemah, stok menipis, atau komentar negatif.")]):
    col.markdown(f'<div class="kpi" style="--c:{w}"><div class="l">{judul}</div><div class="n" style="font-size:.95rem">{isi}</div></div>', unsafe_allow_html=True)

st.subheader("Cara membaca")
T.cara_baca("<b>Skor gabungan</b> menyatukan lima ukuran KB. Angka <b>0</b> berarti sama dengan rata-rata 38 daerah; <b>plus</b> berarti lebih baik; <b>minus</b> berarti lebih rendah.<br>"
            "<b>Tertinggal</b> berarti di bawah angka Provinsi Jatim, bukan gagal mencapai target (target per daerah belum tersedia).<br>"
            "<b>Hubungan</b> antara dua hal tidak otomatis berarti sebab-akibat. Dashboard ini menunjukkan kesenjangan dan prioritas.<br>"
            "<b>Nilai p</b> di bawah 0,05 berarti perbedaan dianggap nyata, bukan kebetulan.", "Singkatnya")

st.subheader("Lima ukuran capaian KB")
for k, (nm, isi, arah) in INDIKATOR_AWAM.items():
    with st.container(border=True):
        st.markdown(f"**{nm}** ({k}) — {isi} *{arah}.*")

st.subheader("Daftar istilah")
q = st.text_input("Cari istilah", placeholder="mis. PUS, klaster, median", key="gl_q")
hasil = [(a, b) for a, b in GLOSARIUM if q.lower() in a.lower() or q.lower() in b.lower()]
if not hasil:
    st.info("Istilah tidak ditemukan.")
for a, b in hasil:
    st.markdown(f"**{a}** — {b}")

st.subheader("Asal data")
st.markdown("- **Capaian KB**: SiPerindu 2025 (CPR modern, MKJP, unmet need, DCR, TFR), Buku Saku Parameter Kependudukan, serta iBangga dan rata-rata lama sekolah (RLS 2025).\n"
            "- **Dukungan layanan**: data tempat layanan, penyuluh KB, dan pasangan usia subur kantor perwakilan; stok alat KB dari SIRIKA/SIGA gudang kabupaten/kota (Sep–Des 2025).\n"
            "- **Suara masyarakat**: komentar publik pada 59 video YouTube tentang alat KB, dikumpulkan lalu dibersihkan; hanya hasil ringkasan yang ditampilkan.\n"
            "- **Peta**: batas wilayah dari geoBoundaries (CC BY 4.0), gambaran umum dan bukan batas resmi.")

with st.expander("Tentang penyusunan"):
    st.markdown("Dashboard ini disusun dari tiga analisis pada program Magang Mandiri – Data Analyst, BKKBN Perwakilan Provinsi Jawa Timur (Tim Kerja Perencanaan dan Keuangan): "
                "capaian KB per kabupaten/kota, dukungan layanan dan stok alat KB, serta analisis komentar publik. Hasil bersifat gambaran untuk diskusi, bukan keputusan resmi.")

with st.expander("Untuk pengembang"):
    st.markdown("- Data hasil analisis dikemas sebagai CSV/JSON/GeoJSON di folder `data/`; kode ada di `kbdash/` dan halaman di `views/`.\n"
                "- Uji statistik di halaman Capaian KB dihitung langsung dari data dan dicocokkan dengan hasil notebook; skor prioritas di Dukungan Layanan juga dihitung ulang.\n"
                "- `pytest` memeriksa integritas data dan menjalankan tiap halaman (AppTest); GitHub Actions menjalankannya pada setiap push.\n"
                "- Tabel per kab/kota dan batas wilayah dipulihkan dari keluaran notebook dan dicocokkan ulang dengan hasil yang tercetak. Lihat README untuk mengganti dengan data asli.\n"
                "- Penilaian nada komentar dijalankan di notebook, bukan di dalam aplikasi ini.")
