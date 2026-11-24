import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from kbdash import charts as C, theme as T
from kbdash.data import muat_gabungan, muat_json, prioritas_per_indikator

T.pasang_css()
df = muat_gabungan()
p1, p2, p3 = muat_json("p1_hasil.json"), muat_json("p2_hasil.json"), muat_json("p3_hasil.json")
SB = p3["sentimen_bert"]
neg = SB["negatif"] / sum(SB.values()) * 100
WIL = dict(zip(df["nama"], df["wilayah"]))

T.hero("Potret KB Jawa Timur 2025",
       "Seberapa merata capaian KB di 38 kabupaten/kota, apakah layanan sudah mendukung, dan apa kata masyarakat di media sosial? "
       "Jelajahi ceritanya lewat peta, grafik, dan pilihan interaktif di bawah.", "Data storytelling · BKKBN Provinsi Jawa Timur")

T.kpi_baris([("Kabupaten/kota", "38", "seluruh Jawa Timur", T.BIRU),
             ("Perlu perhatian khusus", f"{int((df['klaster'] == 'K3').sum())} daerah", "capaian KB lemah di hampir semua ukuran", T.PINK),
             ("Stok alat KB menipis terus", f"{int(df['menetap'].sum())} daerah", "Sep–Des 2025", T.EMAS),
             ("Komentar bernada negatif", f"{neg:.0f}%", f"dari {p3['ringkas']['komentar']:,} komentar YouTube".replace(",", "."), T.UNGU)])

# ---------------------------------------------------------------- cari daerah
st.write("")
T.headline("Mulai dari daerah Anda", "Coba sekarang", T.UNGU)
nama_urut = sorted(df["nama"])
pil = st.selectbox("Pilih kabupaten/kota", nama_urut, index=nama_urut.index("Kota Surabaya"), key="br_daerah")
r = df[df["nama"] == pil].iloc[0]
a, b = st.columns([1, 1.15])
with a:
    st.plotly_chart(C.peta_kategori(df, "kategori", T.WARNA_KATEGORI, "Tingkat capaian KB (garis tebal = daerah pilihan)",
                                    teks=df["nama"] + "<br>Capaian " + df["kategori"].str.lower(), urutan=["Tinggi", "Sedang", "Rendah"],
                                    sorot=WIL[pil], tinggi=380), width="stretch")
with b:
    st.markdown(f"### {pil}")
    st.markdown(T.chip(f"Capaian {r['kategori'].lower()}", T.WARNA_KATEGORI[r["kategori"]]) + T.chip(T.NAMA_KLASTER[r["klaster"]], T.WARNA_KLASTER[r["klaster"]]) +
                T.chip(f"Kawasan {r['kawasan']}", T.WARNA_KAWASAN[r["kawasan"]]), unsafe_allow_html=True)
    T.kpi_baris([("Peringkat capaian", f"{int(r['peringkat'])} / 38", "1 = terbaik", T.BIRU),
                 ("Prioritas penguatan", f"{int(r['rank_prioritas'])} / 38", "1 = paling diprioritaskan", T.PINK),
                 ("Stok alat KB kritis", f"{int(r['stok_kritis_nov'])} / 8", "jenis, Nov 2025", T.EMAS)])
    prio = [r[f"prioritas{i}"] for i in (1, 2, 3) if r[f"prioritas{i}"] != "-"]
    st.markdown("**Yang perlu dibenahi lebih dulu:** " + ("; ".join(prio) if prio else "semua ukuran sudah lebih baik dari angka Jatim."))
    st.markdown("**Catatan dukungan layanan:** " + r["rekomendasi"])
    st.page_link("views/profil_daerah.py", label="Buka profil lengkap daerah ini", icon=":material/arrow_forward:")

# ---------------------------------------------------------------- bab 1
st.divider()
T.headline("Capaian KB timpang: Madura paling tertinggal.", "Cerita 1 · Capaian", T.BIRU)
a, b = st.columns([1.25, 1])
with a:
    st.plotly_chart(C.peta_kontinu(df, "indeks", "Skor gabungan capaian KB", T.SKALA_DIVERGING, zmin=-1.5, zmax=1.5,
                                   teks=df["nama"] + "<br>Skor " + df["indeks"].round(2).astype(str), colorbar_judul="skor", tinggi=380), width="stretch")
with b:
    med = p1["kruskal_kawasan"]["median"]
    st.plotly_chart(C.bar_horizontal(pd.Series(med).index.to_series(), pd.Series(med), pd.Series(med).index.map(T.WARNA_KAWASAN).tolist(),
                                     "Skor tengah tiap kawasan", teks=pd.Series(med).round(2).astype(str), rentang=[-1.9, 0.7]), width="stretch")
    prio = prioritas_per_indikator(df)
    st.markdown(f"Ukuran yang paling sering jadi masalah utama: **{prio.index[0]}** ({prio.iloc[0]} daerah) dan **{prio.index[1]}** ({prio.iloc[1]} daerah).")
    T.catatan("Pembanding adalah angka Provinsi Jatim, bukan target resmi per daerah.")
    st.page_link("views/capaian_kb.py", label="Jelajahi capaian KB", icon=":material/arrow_forward:")

# ---------------------------------------------------------------- bab 2
st.divider()
T.headline("Layanan yang kuat belum tentu berarti capaian tinggi, tetapi stok alat KB di beberapa daerah terus menipis.", "Cerita 2 · Dukungan layanan", T.UNGU)
a, b = st.columns([1.1, 1])
with a:
    fig = go.Figure()
    simbol = {"A": "circle", "B": "square", "C": "triangle-up", "D": "diamond"}
    for t, sub in df.groupby("tip"):
        fig.add_trace(go.Scatter(x=sub["dukungan"], y=sub["indeks"], mode="markers", name=T.NAMA_TIPOLOGI[t], text=sub["nama"],
                                 marker=dict(size=11, color=T.WARNA_TIPOLOGI[t], symbol=simbol[t], line=dict(color="white", width=1.2)),
                                 hovertemplate="%{text}<br>dukungan %{x:.2f} · capaian %{y:.2f}<extra></extra>"))
    fig.add_hline(y=df["indeks"].median(), line_dash="dash", line_color=T.INDIGO, opacity=.5)
    fig.add_vline(x=df["dukungan"].median(), line_dash="dash", line_color=T.INDIGO, opacity=.5)
    fig.update_layout(height=430, margin=dict(l=0, r=0, t=10, b=0), xaxis_title="Dukungan layanan  →  lebih kuat", yaxis_title="Capaian KB  →  lebih tinggi",
                      legend=dict(orientation="h", y=-0.24, font=dict(size=11)))
    st.plotly_chart(fig, width="stretch")
with b:
    dijaga = df[df["tip"] == "C"]["nama"].tolist()
    menetap = df[df["menetap"]]["nama"].tolist()
    st.markdown(f"- Titik-titik **tersebar acak**: dukungan layanan dan capaian KB hampir tidak berkaitan di data ini.\n"
                f"- **{len(dijaga)} daerah perlu dijaga** (capaian masih tinggi tetapi dukungan lemah): {', '.join(dijaga)}.\n"
                f"- Stok alat KB menipis terus-menerus selama Sep–Des 2025 di **{len(menetap)} daerah**: {', '.join(menetap)}.")
    T.catatan("Yang disimpulkan adalah kesenjangan dan prioritas, bukan sebab-akibat.")
    st.page_link("views/dukungan_layanan.py", label="Jelajahi dukungan layanan", icon=":material/arrow_forward:")

# ---------------------------------------------------------------- bab 3
st.divider()
T.headline("Warganet lebih sering bertanya dan mengeluh daripada memuji, dan hampir separuh pertanyaan tak dibalas.", "Cerita 3 · Suara masyarakat", T.PINK)
a, b = st.columns([1, 1.1])
with a:
    nada = {"Negatif": SB["negatif"] / sum(SB.values()) * 100, "Netral": SB["netral"] / sum(SB.values()) * 100, "Positif": SB["positif"] / sum(SB.values()) * 100}
    st.plotly_chart(C.waffle(nada, {"Negatif": T.PINK, "Netral": T.EMAS, "Positif": T.BIRU}, "Dari 100 komentar tentang alat KB"), width="stretch")
with b:
    tema = p3["tema"]
    st.markdown(f"- **{p3['belum_dibalas_pct']:.0f}%** dari {p3['pertanyaan_total']:,} pertanyaan belum dibalas.".replace(",", ".") + "\n"
                f"- Tema pertanyaan terbanyak: **{tema[0][0]}** ({tema[0][2]:.0f}%) dan **{tema[1][0]}** ({tema[1][2]:.0f}%).\n"
                "- Suntik, IUD, dan implan paling banyak dikeluhkan; pil KB paling netral.")
    T.catatan("Nada komentar dinilai komputer dan belum dicocokkan dengan penilaian manusia; komentar YouTube tidak memuat lokasi.")
    st.page_link("views/suara_masyarakat.py", label="Jelajahi suara masyarakat", icon=":material/arrow_forward:")

# ---------------------------------------------------------------- sorotan
st.divider()
T.headline("Daerah sorotan: capaian lemah sekaligus prioritas penguatan tinggi.", "Menyatukan temuan", T.EMAS)
f = st.radio("Tampilkan", ["Semua sorotan", "Capaian KB lemah", "10 besar prioritas penguatan"], horizontal=True, key="br_filter")
sor = df[(df["klaster"] == "K3") | (df["rank_prioritas"] <= 10)].copy()
if f == "Capaian KB lemah":
    sor = sor[sor["klaster"] == "K3"]
elif f.startswith("10 besar"):
    sor = sor[sor["rank_prioritas"] <= 10]
sor = sor.sort_values("rank_prioritas")
st.dataframe(pd.DataFrame({"Kab/Kota": sor["nama"], "Peringkat prioritas": sor["rank_prioritas"], "Peringkat capaian": sor["peringkat"],
                           "Tipe dukungan": sor["tipologi"].str[0], "Jenis alat KB kritis (Nov)": sor["stok_kritis_nov"],
                           "Stok menipis terus": sor["menetap"].map({True: "ya", False: ""})}), hide_index=True, width="stretch")
st.markdown("**Arah tindak lanjut yang didukung data**")
c = st.columns(2)
with c[0].container(border=True):
    st.markdown("**Capaian rendah, dukungan cukup** (tipe B, mis. Bangkalan, Sampang)\n\nKaji sisi permintaan: penyuluhan dan budaya setempat, sebelum menambah pasokan.")
with c[1].container(border=True):
    st.markdown("**Capaian rendah dan dukungan rendah** (tipe A, mis. Jember, Kota Malang)\n\nPulihkan stok, optimalkan penyuluh dan tempat layanan.")
with c[0].container(border=True):
    st.markdown("**Perlu dijaga** (tipe C: capaian tinggi, dukungan rendah)\n\nJaga stok dan tenaga agar capaian tinggi tidak turun.")
with c[1].container(border=True):
    st.markdown("**Materi edukasi**\n\nSiapkan FAQ tentang haid serta pemasangan/pelepasan, dan alur balasan komentar yang rutin.")
T.catatan("Draf untuk didiskusikan dengan tim kerja dan tenaga kesehatan; hasil menunjukkan kesenjangan dan prioritas, bukan sebab-akibat.")
