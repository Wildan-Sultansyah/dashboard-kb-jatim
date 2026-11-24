import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from kbdash import charts as C, theme as T
from kbdash.data import muat_gabungan, muat_json, hitung_woa

T.pasang_halaman("Proyek 2 · Dukungan Layanan KB dan Kesesuaiannya dengan Capaian", kicker="Analisis Geospasial + Analitik Media Sosial",
                 ringkas="Di mana dukungan layanan KB (tempat layanan, penyuluh, stok alokon) lemah, dan apakah daerah itu juga yang capaiannya rendah? "
                         "Klaim: kesesuaian, kesenjangan, dan prioritas. Bukan pengaruh atau sebab-akibat.")
df = muat_gabungan()
H = muat_json("p2_hasil.json")
BULAN = ["Sep", "Okt", "Nov", "Des"]

tabs = st.tabs(["Indeks dukungan", "Pola spasial", "Kesesuaian", "Stok kritis", "Prioritas (WOA)", "Catatan"])

# ------------------------------------------------------------ Indeks dukungan
with tabs[0]:
    st.markdown("Indeks dukungan (0–1) = rata-rata tiga komponen berbobot sama: tempat layanan KB per 10.000 PUS, penyuluh (PKB) per 10.000 PUS, "
                "dan stok alokon (dibalik: makin banyak jenis kritis, makin lemah). Pembanding bobot entropi, PCA, dan geometrik "
                f"berkorelasi tinggi (Spearman {H['spearman_indeks_alt']['entropi']:.2f}, {H['spearman_indeks_alt']['PCA']:.2f}, {H['spearman_indeks_alt']['geometrik']:.2f}).")
    a, b = st.columns([1.2, 1])
    with a:
        tek = df["nama"] + "<br>Dukungan " + df["dukungan"].round(2).astype(str) + "<br>Layanan " + df["layanan_per10k"].astype(str) + " · PKB " + df["pkb_per10k"].astype(str) + " per 10.000 PUS"
        st.plotly_chart(C.peta_kontinu(df, "dukungan", "Indeks dukungan (gelap = lebih kuat)", T.SKALA_BIRU, teks=tek, colorbar_judul="indeks"), width="stretch")
    with b:
        d = df.sort_values("dukungan")
        st.plotly_chart(C.bar_horizontal(d["nama"], d["dukungan"], T.BIRU, "Indeks dukungan per daerah", tinggi=820), width="stretch")
    k = df.sort_values("dukungan").head(5)
    st.markdown("**Lima dukungan terendah:** " + "; ".join(f"{r.nama} ({r.dukungan:.2f}; {r.stok_kritis_nov} jenis kritis)" for r in k.itertuples()))

# ------------------------------------------------------------ Pola spasial
with tabs[1]:
    st.markdown(f"Moran's I indeks dukungan = **{H['moran_dukungan']['I']:.3f}** (p = {H['moran_dukungan']['p']:.3f}): tidak ada autokorelasi spasial global yang nyata. "
                "LISA dan Getis-Ord Gi* hanya menandai sedikit daerah (p < 0,05).")
    a, b = st.columns(2)
    lisa = df.assign(grup=df["lisa"].replace({"High-Low": "Outlier (HL/LH)", "Low-High": "Outlier (HL/LH)"}))
    wl = {"High-High": T.BIRU, "Low-Low": T.ORANYE, "Outlier (HL/LH)": T.AQUA, "Tidak signifikan": T.ABU}
    with a:
        tek = df["nama"] + "<br>LISA: " + df["lisa"]
        st.plotly_chart(C.peta_kategori(lisa, "grup", wl, "LISA indeks dukungan (p < 0,05)", teks=tek, urutan=list(wl)), width="stretch")
    with b:
        wg = {"Hotspot dukungan kuat": T.BIRU, "Coldspot dukungan lemah": T.ORANYE, "Tidak signifikan": T.ABU}
        tek = df["nama"] + "<br>Gi*: " + df["gi"]
        st.plotly_chart(C.peta_kategori(df, "gi", wg, "Getis-Ord Gi* (p < 0,05)", teks=tek, urutan=list(wg)), width="stretch")
    c1, c2 = st.columns(2)
    c1.markdown("**Low-Low (dukungan lemah mengelompok):** " + (", ".join(df[df["lisa"] == "Low-Low"]["nama"]) or "-"))
    c2.markdown("**Coldspot Gi*:** " + (", ".join(df[df["gi"].str.startswith("Coldspot")]["nama"]) or "-"))

# ------------------------------------------------------------ Kesesuaian
with tabs[2]:
    ks = H["kesesuaian"]
    k = st.columns(3)
    k[0].metric("Spearman capaian vs dukungan", f"ρ = {ks['capaian_vs_dukungan'][0]:.3f}", f"p = {ks['capaian_vs_dukungan'][1]:.3f}", delta_color="off")
    k[1].metric("Bivariate Moran", f"I = {ks['bivariate_moran'][0]:.3f}", f"p = {ks['bivariate_moran'][1]:.3f}", delta_color="off")
    k[2].metric("Tipologi A / B / C / D", " / ".join(str(int((df['tip'] == t).sum())) for t in "ABCD"))
    st.markdown(f"Per komponen: tempat layanan ρ = {ks['layanan'][0]:+.3f} (p = {ks['layanan'][1]:.3f}), penyuluh ρ = {ks['pkb'][0]:+.3f} (p = {ks['pkb'][1]:.3f}), "
                f"stok (dibalik) ρ = {ks['stok'][0]:+.3f} (p = {ks['stok'][1]:.3f}). Korelasi mendekati nol: dalam data ini dukungan dan capaian tidak selaras; ini bukan bukti dukungan tak penting.")
    a, b = st.columns([1.1, 1])
    with a:
        fig = go.Figure()
        simbol = {"A": "circle", "B": "square", "C": "triangle-up", "D": "diamond"}
        for t, sub in df.groupby("tip"):
            fig.add_trace(go.Scatter(x=sub["dukungan"], y=sub["indeks"], mode="markers", name=T.NAMA_TIPOLOGI[t], text=sub["nama"],
                                     marker=dict(size=11, color=T.WARNA_TIPOLOGI[t], symbol=simbol[t], line=dict(color="white", width=1.2)),
                                     hovertemplate="%{text}<br>dukungan %{x:.2f} · capaian %{y:.2f}<extra></extra>"))
        fig.add_hline(y=df["indeks"].median(), line_dash="dash", line_color=T.ABU_TENGAH)
        fig.add_vline(x=df["dukungan"].median(), line_dash="dash", line_color=T.ABU_TENGAH)
        fig.update_layout(height=470, margin=dict(l=0, r=0, t=10, b=0), xaxis_title="Indeks dukungan (0–1)", yaxis_title="Indeks capaian (Proyek 1)",
                          legend=dict(orientation="h", y=-0.2, font=dict(size=11)))
        st.plotly_chart(fig, width="stretch")
    with b:
        tek = df["nama"] + "<br>" + df["tipologi"]
        st.plotly_chart(C.peta_kategori(df, "tip", T.WARNA_TIPOLOGI, "Peta tipologi kesesuaian", teks=tek, urutan=list("ABCD"), nama_legenda=T.NAMA_TIPOLOGI), width="stretch")
    pilih = st.selectbox("Lihat daerah menurut tipologi", [T.NAMA_TIPOLOGI[t] for t in "ABCD"])
    sub = df[df["tip"] == pilih[0]].sort_values("dukungan")
    st.write(", ".join(sub["nama"]))
    st.markdown("> " + sub["rekomendasi"].iloc[0])
    sens = H["sensitivitas_tipologi"]
    st.markdown("**Sensitivitas tipologi** (daerah yang berpindah tipe jika indeks dukungan diganti): " +
                "; ".join(f"{k_}: {len(v)} daerah ({', '.join(v)})" for k_, v in sens.items()) +
                ". Daerah ini dekat batas median dan sensitif terhadap asumsi.")

# ------------------------------------------------------------ Stok kritis
with tabs[3]:
    st.markdown("Stok **kritis** = stok gudang kab/kota kurang dari 1 bulan konsumsi (asumsi). Hanya September–Desember 2025 yang dipakai karena cakupan laporan stock opname bulan lain rendah; "
                "potret utama November (100% gudang melapor).")
    a, b = st.columns([1, 1.1])
    with a:
        z = df.set_index("nama")[["kritis_sep", "kritis_okt", "kritis_nov", "kritis_des"]]
        z.columns = BULAN
        z = z.assign(r=z.mean(axis=1)).sort_values("r", ascending=False).drop(columns="r")
        st.plotly_chart(C.heatmap(z, T.SKALA_ORANYE, "Jumlah jenis alokon stok kritis per bulan (0–8)", zmin=0, zmax=8, fmt=".0f", tinggi=900, colorbar_judul="jenis"), width="stretch")
    with b:
        nol = pd.DataFrame(H["stok_nol"], index=BULAN).T
        nol = nol.loc[nol.mean(axis=1).sort_values(ascending=False).index]
        st.plotly_chart(C.heatmap(nol, T.SKALA_ORANYE, "Kab/kota dengan stok = 0, per jenis alokon (dari 38)", zmin=0, zmax=38, fmt=".0f", tinggi=380, colorbar_judul="daerah"), width="stretch")
        mt = df[df["menetap"]].sort_values("kritis_des", ascending=False)
        fig = go.Figure()
        for r in mt.itertuples():
            fig.add_trace(go.Scatter(x=BULAN, y=[r.kritis_sep, r.kritis_okt, r.kritis_nov, r.kritis_des], mode="lines+markers", name=r.nama,
                                     hovertemplate=r.nama + ": %{y} jenis<extra></extra>"))
        fig.update_layout(title=dict(text="Daerah dengan stok kritis menetap (≥3 jenis di semua bulan)", x=0, font=dict(size=14)),
                          height=360, margin=dict(l=0, r=0, t=34, b=0), yaxis=dict(range=[0, 8], title="Jenis alokon kritis"), legend=dict(font=dict(size=10)))
        st.plotly_chart(fig, width="stretch")
    mo = H["moran_kritis_bulanan"]
    st.markdown("Moran's I jumlah jenis kritis per bulan: " + "; ".join(f"{k_} I = {v[0]:+.3f} (p = {v[1]:.2f})" for k_, v in mo.items()) +
                ". Tidak ada pengelompokan spasial. " +
                "Perbaikan terbesar Sep→Des: " + ", ".join(f"{k_} ({v})" for k_, v in H["membaik"].items()) +
                ". Pemburukan terbesar: " + ", ".join(f"{k_} (+{v})" for k_, v in H["memburuk"].items()) + ".")

# ------------------------------------------------------------ WOA
with tabs[4]:
    st.markdown("**Weighted Overlay Analysis**: skor prioritas penguatan = jumlah berbobot empat layer (0–1). Bobot adalah **asumsi peneliti**; ubah di bawah untuk melihat dampaknya pada peringkat.")
    b0 = H["bobot_woa"]
    c = st.columns(4)
    w = {"capaian_rendah": c[0].slider("Capaian rendah", 0.0, 1.0, b0["capaian_rendah"], 0.05),
         "layanan_rendah": c[1].slider("Tempat layanan sedikit", 0.0, 1.0, b0["layanan_rendah"], 0.05),
         "pkb_rendah": c[2].slider("Penyuluh sedikit", 0.0, 1.0, b0["pkb_rendah"], 0.05),
         "stok_kritis": c[3].slider("Stok alokon kritis", 0.0, 1.0, b0["stok_kritis"], 0.05)}
    if sum(w.values()) == 0:
        st.warning("Setidaknya satu bobot harus lebih dari 0.")
        st.stop()
    total = sum(w.values())
    st.caption("Bobot dinormalkan otomatis (jumlah = 1): " + ", ".join(f"{k_.replace('_', ' ')} {v / total:.2f}" for k_, v in w.items()))
    res = hitung_woa(df, w)
    top_n = st.slider("Tampilkan N daerah teratas", 5, 20, 15)
    d = df.assign(skor=res["skor"], peringkat_baru=res["peringkat"]).sort_values("skor", ascending=False)
    top = d.head(top_n)
    a, b = st.columns([1.2, 1])
    with a:
        nama = {"capaian_rendah": "Capaian rendah (Proyek 1)", "layanan_rendah": "Tempat layanan KB sedikit", "pkb_rendah": "Penyuluh sedikit", "stok_kritis": "Stok alokon kritis"}
        warna = {"capaian_rendah": T.BIRU, "layanan_rendah": T.ORANYE, "pkb_rendah": T.AQUA, "stok_kritis": "#eda100"}
        fig = go.Figure()
        for k_ in nama:
            fig.add_trace(go.Bar(y=top["nama"], x=res.loc[top.index, k_], name=nama[k_], orientation="h",
                                 marker=dict(color=warna[k_], line=dict(color="white", width=1.5)),
                                 hovertemplate="%{y}<br>" + nama[k_] + ": %{x:.3f}<extra></extra>"))
        fig.update_layout(barmode="stack", title=dict(text=f"Komposisi skor prioritas, {top_n} daerah teratas", x=0, font=dict(size=14)),
                          height=max(340, 28 * top_n + 130), margin=dict(l=0, r=0, t=34, b=0), yaxis=dict(autorange="reversed"),
                          xaxis_title="Skor prioritas", legend=dict(orientation="h", y=-0.12, font=dict(size=11)))
        st.plotly_chart(fig, width="stretch")
    with b:
        tek = d["nama"] + "<br>Skor " + d["skor"].round(2).astype(str) + " · peringkat " + d["peringkat_baru"].astype(str)
        st.plotly_chart(C.peta_kontinu(d, "skor", "Skor prioritas penguatan (gelap = lebih tinggi)", T.SKALA_ORANYE, teks=tek, colorbar_judul="skor", tinggi=440), width="stretch")
    tab = pd.DataFrame({"Peringkat": top["peringkat_baru"], "Kab/Kota": top["nama"], "Skor": top["skor"].round(2), "Tipologi": top["tip"],
                        "Peringkat bawaan": top["rank_prioritas"], "Stok kritis (Nov)": top["stok_kritis_nov"],
                        "Tangguh": top["tangguh"].map({True: "ya", False: ""})})
    st.dataframe(tab, hide_index=True, width="stretch")
    if w == b0:
        st.success("Bobot bawaan: peringkat identik dengan notebook.")
    st.subheader("Uji sensitivitas (dari notebook)")
    sk = pd.DataFrame(H["skenario_woa"], columns=["Skenario", "Spearman vs skor utama", "Irisan 10 besar (dari 10)"])
    st.dataframe(sk, hide_index=True, width="stretch")
    tg = df[df["tangguh"]].sort_values("rank_prioritas")["nama"]
    st.markdown("**Prioritas tangguh** (10 besar di semua empat skenario utama): " + ", ".join(tg))

# ------------------------------------------------------------ Catatan
with tabs[5]:
    st.subheader("Keterbatasan")
    for i, s in enumerate(H["keterbatasan"], 1):
        st.markdown(f"{i}. {s}")
