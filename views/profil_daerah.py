import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from kbdash import charts as C, theme as T
from kbdash.data import muat_gabungan, muat_json, INDIKATOR, NAIK_BAIK
from kbdash.teks import INDIKATOR_AWAM

T.pasang_halaman("Profil Daerah", kicker="Satu kabupaten/kota dalam satu halaman",
                 ringkas="Pilih daerah untuk melihat capaian KB, ukuran yang perlu dibenahi, dan dukungan layanannya. Bisa dibandingkan dengan daerah lain.",
                 warna=("#1c7ed6", "#7048e8"))
df = muat_gabungan()
jatim = muat_json("p1_jatim.json")
NAMA = {c: INDIKATOR_AWAM[c][0] for c in INDIKATOR}
urut = sorted(df["nama"])

c = st.columns(2)
pilih = c[0].selectbox("Kabupaten/kota", urut, index=urut.index("Kab. Bangkalan"), key="pf_a")
band = c[1].selectbox("Bandingkan dengan (opsional)", ["(tidak ada)"] + [n for n in urut if n != pilih], key="pf_b")
r = df[df["nama"] == pilih].iloc[0]
rb = df[df["nama"] == band].iloc[0] if band != "(tidak ada)" else None

st.markdown(T.chip(f"Capaian {r['kategori'].lower()}", T.WARNA_KATEGORI[r["kategori"]]) + T.chip(T.NAMA_KLASTER[r["klaster"]], T.WARNA_KLASTER[r["klaster"]]) +
            T.chip(T.NAMA_TIPOLOGI[r["tip"]], T.WARNA_TIPOLOGI[r["tip"]]), unsafe_allow_html=True)
st.caption(f"{r['tipe']} · kawasan {r['kawasan']}")
T.kpi_baris([("Skor capaian", T.fmt(r["indeks"]), "0 = rata-rata 38 daerah", T.PINK if r["indeks"] < 0 else T.BIRU),
             ("Peringkat capaian", f"{int(r['peringkat'])} / 38", "1 = terbaik", T.BIRU),
             ("Prioritas penguatan", f"{int(r['rank_prioritas'])} / 38", "1 = paling diprioritaskan", T.UNGU),
             ("Alat KB stok kritis", f"{int(r['stok_kritis_nov'])} / 8", "jenis, November 2025", T.EMAS)])

a, b = st.columns([1.35, 1])
with a:
    st.subheader("Lima ukuran KB dibanding angka Jatim")
    baris = []
    for k in INDIKATOR:
        v = r[k]
        d = 2 if k == "TFR" else 1
        if pd.isna(v):
            baris.append({"Ukuran": NAMA[k], "Daerah": "data kosong", "Jatim": jatim[k], "Selisih": "", "Status": "–"})
            continue
        buruk = (v < jatim[k]) if NAIK_BAIK[k] else (v > jatim[k])
        baris.append({"Ukuran": NAMA[k], "Daerah": round(v, d), "Jatim": round(jatim[k], d), "Selisih": f"{v - jatim[k]:+.{d}f}".replace(".", ","),
                      "Status": ("🔴 perlu " + ("dinaikkan" if NAIK_BAIK[k] else "diturunkan")) if buruk else "🔵 lebih baik dari Jatim"})
    st.dataframe(pd.DataFrame(baris), hide_index=True, width="stretch", column_config={"Status": st.column_config.TextColumn(width="large"), "Ukuran": st.column_config.TextColumn(width="medium")})
    prio = [r[f"prioritas{i}"] for i in (1, 2, 3) if r[f"prioritas{i}"] != "-"]
    st.markdown("**Dibenahi lebih dulu:** " + ("; ".join(prio) if prio else "semua ukuran sudah lebih baik dari angka Jatim."))
    fig = go.Figure()
    zs = {pilih: r}
    if rb is not None:
        zs[band] = rb
    for i, (nm, rr) in enumerate(zs.items()):
        z = [rr[f"z_{k}"] for k in INDIKATOR]
        fig.add_trace(go.Bar(y=[NAMA[k] for k in INDIKATOR], x=z, orientation="h", name=nm,
                             marker=dict(color=(T.BIRU if i == 0 else T.EMAS), line=dict(color="white", width=1.2)),
                             hovertemplate=nm + " · %{y}: %{x:.2f}<extra></extra>"))
    fig.add_vline(x=0, line_color=T.INDIGO)
    fig.update_layout(title=dict(text="Posisi dibanding rata-rata 38 daerah (kanan = lebih baik)", x=0, font=dict(size=14)), barmode="group", height=330 if rb is not None else 280,
                      margin=dict(l=0, r=0, t=34, b=0), xaxis=dict(range=[-3.3, 3.3], gridcolor="rgba(120,130,190,.18)"), yaxis=dict(autorange="reversed"),
                      showlegend=rb is not None, legend=dict(orientation="h", y=-0.18))
    st.plotly_chart(fig, width="stretch")
with b:
    st.plotly_chart(C.peta_kategori(df, "kategori", T.WARNA_KATEGORI, "Letak di Jawa Timur", teks=df["nama"] + "<br>" + df["kategori"], urutan=["Tinggi", "Sedang", "Rendah"],
                                    sorot=r["wilayah"], tinggi=400), width="stretch")

st.subheader("Dukungan layanan")
a, b = st.columns(2)
with a:
    st.markdown(f"> {r['rekomendasi']}")
    st.markdown(
        f"- Skor dukungan **{T.fmt(r['dukungan'])}** (nilai tengah daerah {T.fmt(df['dukungan'].median())})\n"
        f"- Tempat layanan KB **{T.fmt(r['layanan_per10k'], 1)}** per 10.000 pasangan usia subur (nilai tengah {T.fmt(df['layanan_per10k'].median(), 1)})\n"
        f"- Penyuluh KB **{T.fmt(r['pkb_per10k'], 1)}** per 10.000 pasangan usia subur (nilai tengah {T.fmt(df['pkb_per10k'].median(), 1)})\n"
        f"- Alat KB yang stoknya habis (Nov): **{r['alokon_kosong_nov'] or 'tidak ada'}**"
        + ("\n- **Stok menipis terus-menerus** selama September–Desember" if r["menetap"] else "")
        + ("\n- **Prioritas konsisten**: selalu masuk 10 besar walau asumsi diubah" if r["tangguh"] else ""))
with b:
    bl = ["Sep", "Okt", "Nov", "Des"]
    fig = go.Figure(go.Bar(x=bl, y=[r["kritis_sep"], r["kritis_okt"], r["kritis_nov"], r["kritis_des"]], marker=dict(color=T.PINK),
                           text=[r["kritis_sep"], r["kritis_okt"], r["kritis_nov"], r["kritis_des"]], textposition="outside", name=pilih,
                           hovertemplate="%{x}: %{y} jenis<extra></extra>"))
    if rb is not None:
        fig.add_trace(go.Bar(x=bl, y=[rb["kritis_sep"], rb["kritis_okt"], rb["kritis_nov"], rb["kritis_des"]], marker=dict(color=T.EMAS), name=band,
                             hovertemplate=band + " · %{x}: %{y} jenis<extra></extra>"))
    fig.update_layout(title=dict(text="Jenis alat KB yang stoknya kurang dari 1 bulan (dari 8)", x=0, font=dict(size=14)), barmode="group", height=290,
                      margin=dict(l=0, r=0, t=34, b=0), yaxis=dict(range=[0, 8.8], gridcolor="rgba(120,130,190,.18)"), bargap=0.4,
                      showlegend=rb is not None, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, width="stretch")
T.catatan("Prioritas bersifat relatif (kesenjangan terhadap daerah lain), bukan sebab-akibat. Angka Jatim dari SiPerindu 2025.")
