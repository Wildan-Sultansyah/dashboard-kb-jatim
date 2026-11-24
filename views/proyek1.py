import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.decomposition import PCA

from kbdash import charts as C, theme as T
from kbdash.data import muat_p1, muat_json, prioritas_per_indikator, INDIKATOR, LABEL, NAIK_BAIK, KAWASAN_URUT

T.pasang_halaman("Proyek 1 · Capaian KB per Kab/Kota", kicker="Statistika Nonparametrik + Sains Data & Analisis Kebijakan",
                 ringkas="Indeks capaian dari lima indikator SiPerindu 2025 (CPR modern, MKJP, unmet need, DCR, TFR), "
                         "dibanding nilai Provinsi Jatim. Bukan target resmi per daerah.")
df = muat_p1()
H = muat_json("p1_hasil.json")
jatim = muat_json("p1_jatim.json")

t1, t2, t3, t4, t5 = st.tabs(["Capaian & peta", "Prioritas per daerah", "Klaster", "Uji nonparametrik", "Catatan"])

# ------------------------------------------------------------ Capaian & peta
with t1:
    opsi = {"Indeks capaian": "indeks", "Kategori (tercile)": "kategori", "Klaster": "klaster"}
    opsi.update({LABEL[c]: c for c in INDIKATOR})
    pil = st.radio("Lapisan peta", list(opsi), horizontal=True)
    kol = opsi[pil]
    a, b = st.columns([1.2, 1])
    with a:
        teks = df["nama"] + "<br>Indeks " + df["indeks"].round(2).astype(str) + " · " + df["kategori"] + " · klaster " + df["klaster"]
        if kol == "indeks":
            fig = C.peta_kontinu(df, "indeks", "Indeks capaian (rata-rata z)", T.SKALA_DIVERGING, zmin=-2.5, zmax=2.5, teks=teks, colorbar_judul="indeks")
        elif kol == "kategori":
            fig = C.peta_kategori(df, "kategori", T.WARNA_KATEGORI, "Kategori capaian (tercile indeks)", teks=teks, urutan=["Tinggi", "Sedang", "Rendah"])
        elif kol == "klaster":
            fig = C.peta_kategori(df, "klaster", T.WARNA_KLASTER, "Klaster daerah (K-Medoids)", teks=teks, urutan=["K1", "K2", "K3"])
        else:
            tek = df["nama"] + f"<br>{LABEL[kol]}: " + df[kol].round(2).astype(str) + f" (Jatim {jatim[kol]})"
            fig = C.peta_kontinu(df.assign(zz=df["z_" + kol]), "zz", f"{LABEL[kol]}: skor z ({'tinggi' if NAIK_BAIK[kol] else 'rendah'} = baik; biru = lebih baik)",
                                 T.SKALA_DIVERGING, zmin=-3, zmax=3, teks=tek, colorbar_judul="z")
        st.plotly_chart(fig, width="stretch")
    with b:
        d = df.sort_values("indeks")
        st.plotly_chart(C.bar_horizontal(d["nama"], d["indeks"], d["kategori"].map(T.WARNA_KATEGORI), "Indeks per daerah",
                                         tinggi=820, rentang=[-2.6, 1.3]), width="stretch")
    z = df.sort_values("indeks", ascending=False).set_index("nama")[["z_" + c for c in INDIKATOR]]
    z.columns = [LABEL[c] for c in INDIKATOR]
    st.plotly_chart(C.heatmap(z, T.SKALA_DIVERGING, "Skor z per indikator (biru = lebih baik, abu = rata-rata, merah = lebih rendah)",
                              zmin=-3, zmax=3, tinggi=900, colorbar_judul="z"), width="stretch")
    T.catatan(f"Ketahanan indeks: korelasi Spearman dengan indeks relatif-Jatim {H['ketahanan']['spearman_relatif_jatim']:.2f}; "
              f"dengan indeks tanpa TFR {H['ketahanan']['spearman_tanpa_tfr']:.2f}. DCR Kota Kediri kosong; indeksnya dari empat indikator.")

# ------------------------------------------------------------ Prioritas
with t2:
    c = st.columns(3)
    f_kaw = c[0].multiselect("Kawasan", KAWASAN_URUT, default=KAWASAN_URUT)
    f_kat = c[1].multiselect("Kategori", ["Rendah", "Sedang", "Tinggi"], default=["Rendah", "Sedang", "Tinggi"])
    f_kls = c[2].multiselect("Klaster", ["K1", "K2", "K3"], default=["K1", "K2", "K3"])
    d = df[df["kawasan"].isin(f_kaw) & df["kategori"].isin(f_kat) & df["klaster"].isin(f_kls)].sort_values("peringkat")
    tab = d[["peringkat", "nama", "indeks", "kategori", "klaster", "prioritas1", "prioritas2", "prioritas3"]].copy()
    tab["indeks"] = tab["indeks"].round(2)
    tab.columns = ["Peringkat", "Kab/Kota", "Indeks", "Kategori", "Klaster", "Prioritas 1", "Prioritas 2", "Prioritas 3"]
    st.dataframe(tab, hide_index=True, width="stretch", height=520)
    T.catatan("Prioritas = indikator yang lebih buruk dari nilai Jatim, maksimal tiga, diurutkan dari skor z terendah. "
              "Format: nilai daerah (nilai Jatim) → arah dan besar perbaikan.")
    p = prioritas_per_indikator(d)
    if len(p):
        st.plotly_chart(C.bar_horizontal(p.index.to_series(), p, T.BIRU, "Indikator pada 'Prioritas 1' (daerah terpilih)",
                                         teks=p.astype(str)), width="stretch")
    pp = H["tambahan_peserta"]
    s = pd.Series(pp).rename(index=lambda w: w.title())
    st.plotly_chart(C.bar_horizontal(s.index.to_series(), s, T.ORANYE, "Perkiraan tambahan peserta KB agar CPR daerah menyamai Jatim (10 terbesar)",
                                     teks=s.map(lambda v: f"{v:,.0f}".replace(",", "."))), width="stretch")
    T.catatan("Pendekatan kasar: selisih CPR terhadap Jatim × PUS 2025. Bukan target resmi.")

# ------------------------------------------------------------ Klaster
with t3:
    st.markdown(f"**PCA + K-Medoids (PAM, jarak Manhattan)**, k = {H['k_terpilih']} dipilih dari silhouette, Calinski-Harabasz, Davies-Bouldin "
                f"(syarat k ≥ 3 dan klaster terkecil ≥ 3). Stabilitas subsampling ARI rata-rata {H['ari_stabilitas']['rata']:.2f} "
                f"(persentil 5% = {H['ari_stabilitas']['p5']:.2f}); kesesuaian dengan Ward ARI {H['ari_ward']:.2f}.")
    a, b = st.columns([1.2, 1])
    with a:
        X = df[["z_" + c for c in INDIKATOR]].fillna(0).values
        pca = PCA(n_components=2).fit(X)
        sc = pca.transform(X)
        fig = go.Figure()
        simb = {"K1": "circle", "K2": "square", "K3": "triangle-up"}
        for k_ in ["K1", "K2", "K3"]:
            m = (df["klaster"] == k_).values
            fig.add_trace(go.Scatter(x=sc[m, 0], y=sc[m, 1], mode="markers", name=k_, text=df["nama"][m],
                                     marker=dict(size=11, color=T.WARNA_KLASTER[k_], symbol=simb[k_], line=dict(color="white", width=1.2)),
                                     hovertemplate="%{text}<extra>" + k_ + "</extra>"))
            med = H["medoid"][k_]
            i = int(np.where(df["nama"] == med)[0][0])
            fig.add_trace(go.Scatter(x=[sc[i, 0]], y=[sc[i, 1]], mode="markers+text", text=[f"Medoid {k_}: {med}"], textposition="top center",
                                     marker=dict(size=19, symbol="star", color=T.WARNA_KLASTER[k_], line=dict(color="#222", width=1)),
                                     showlegend=False, hovertemplate=med + "<extra>medoid</extra>"))
        fig.update_layout(height=470, margin=dict(l=0, r=0, t=10, b=0),
                          xaxis_title=f"PC1 ({pca.explained_variance_ratio_[0]:.0%})", yaxis_title=f"PC2 ({pca.explained_variance_ratio_[1]:.0%})",
                          legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, width="stretch")
        T.catatan("Proyeksi dua komponen pertama dari z-score; pembentukan klaster memakai tiga komponen (varians kumulatif 93%).")
    with b:
        prof = df.groupby("klaster")[INDIKATOR + ["indeks"]].mean().round(2)
        prof.insert(0, "Jumlah", df["klaster"].value_counts())
        prof.columns = ["Jumlah"] + [LABEL[c] for c in INDIKATOR] + ["Indeks rata-rata"]
        prof["Medoid"] = pd.Series(H["medoid"])
        st.dataframe(prof, width="stretch")
        for k_ in ["K1", "K2", "K3"]:
            pk = H["profil_klaster"][k_]
            with st.expander(f"{k_}: {pk['n']} daerah · indikator lemah: {pk['lemah']} · kuat: {pk['kuat']}"):
                st.write(", ".join(df[df["klaster"] == k_]["nama"]))
        st.markdown(f"Variabel eksternal (tidak dipakai membentuk klaster): iBangga H = {H['kruskal_klaster_eksternal']['iBangga']['H']:.2f} "
                    f"(p = {H['kruskal_klaster_eksternal']['iBangga']['p']:.4f}); RLS H = {H['kruskal_klaster_eksternal']['RLS_2025']['H']:.2f} "
                    f"(p = {H['kruskal_klaster_eksternal']['RLS_2025']['p']:.4f}).")
        st.markdown("**Daerah di perbatasan klaster** (silhouette < 0,1): " + ", ".join(H["perbatasan"]))
    v = pd.DataFrame(H["validasi_klaster"]).rename(columns={"k": "k", "silhouette": "Silhouette", "ch": "Calinski-Harabasz", "db": "Davies-Bouldin", "terkecil": "Klaster terkecil"})
    st.dataframe(v, hide_index=True, width="stretch")

# ------------------------------------------------------------ Uji
with t4:
    st.markdown("Taraf signifikansi α = 0,05. Uji nonparametrik dipilih karena sebagian indikator tidak normal (Shapiro-Wilk) dan n = 38.")
    uji = st.selectbox("Pilih uji", [
        "Normalitas (Shapiro-Wilk)", "1 sampel: Wilcoxon vs Jatim/Renstra", "2 sampel independen: kota vs kabupaten (Mann-Whitney)",
        "k sampel: antar kawasan (Kruskal-Wallis + Dunn)", "Hubungan: Spearman vs iBangga dan RLS",
        "k sampel berpasangan biner: Cochran's Q", "Independensi kategorik: chi-square dan Fisher",
        "2 sampel dependen: prevalensi KB aktif 2023 vs 2025"])
    if uji.startswith("Normalitas"):
        d = pd.DataFrame(H["shapiro"]).rename(columns={"v": "Variabel", "mean": "Rata-rata", "sd": "SD", "p": "p Shapiro"})
        d["Normal (p > 0,05)"] = np.where(d["p Shapiro"] > .05, "ya", "tidak")
        st.dataframe(d, hide_index=True, width="stretch")
        st.info("CPR, MKJP, dan DCR tidak normal; unmet need tepat di batas (p = 0,050). Uji berbasis peringkat lebih aman.")
    elif uji.startswith("1 sampel"):
        d = pd.DataFrame(H["wilcoxon"], columns=["Indikator", "Pembanding", "Nilai", "Median 38 daerah", "W", "p"])
        d["Keputusan"] = np.where(d["p"] < .05, "tolak H0", "gagal tolak H0")
        st.dataframe(d, hide_index=True, width="stretch")
        st.info("Hanya DCR terhadap target Renstra (18,7) yang signifikan: median daerah (22,2) lebih tinggi dari target provinsi. "
                "Terhadap nilai Jatim hasilnya tidak signifikan karena Jatim adalah rata-rata tertimbang daerahnya sendiri.")
    elif uji.startswith("2 sampel independen"):
        d = pd.DataFrame(H["mannwhitney"], columns=["Variabel (z)", "Median kota", "Median kabupaten", "U", "p"])
        d["Keputusan"] = np.where(d["p"] < .05, "tolak H0", "gagal tolak H0")
        st.dataframe(d, hide_index=True, width="stretch")
        fig = go.Figure()
        for t_, w in [("Kabupaten", T.BIRU), ("Kota", T.ORANYE)]:
            s = df[df["tipe"] == t_]
            fig.add_trace(go.Box(y=s["indeks"], name=t_, boxpoints="all", jitter=.4, pointpos=0, marker=dict(color=w, size=6), line=dict(color=w),
                                 text=s["nama"], hovertemplate="%{text}: %{y:.2f}<extra></extra>"))
        fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="Indeks capaian", showlegend=False)
        st.plotly_chart(fig, width="stretch")
        st.info("Indeks keseluruhan tidak berbeda antara kota dan kabupaten (p = 0,410). Perbedaan nyata hanya pada MKJP (kota lebih tinggi, p = 0,002).")
    elif uji.startswith("k sampel: antar kawasan"):
        kw = H["kruskal_kawasan"]
        st.markdown(f"Indeks ~ kawasan: **H = {kw['H']:.3f}, p = {kw['p']:.4f}** → tolak H0.")
        fig = go.Figure()
        warna = dict(zip(KAWASAN_URUT, [T.BIRU, T.ORANYE, T.AQUA, T.MERAH]))
        for k_ in KAWASAN_URUT:
            s = df[df["kawasan"] == k_]
            fig.add_trace(go.Box(y=s["indeks"], name=k_, boxpoints="all", jitter=.4, pointpos=0, marker=dict(color=warna[k_], size=6),
                                 line=dict(color=warna[k_]), text=s["nama"], hovertemplate="%{text}: %{y:.2f}<extra></extra>"))
        fig.update_layout(height=360, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="Indeks capaian", showlegend=False)
        st.plotly_chart(fig, width="stretch")
        a, b = st.columns(2)
        a.markdown("**Per indikator (Kruskal-Wallis)**")
        a.dataframe(pd.DataFrame(kw["per_indikator"], columns=["Indikator", "H", "p"]), hide_index=True, width="stretch")
        b.markdown("**Uji lanjut Dunn (p terkoreksi Bonferroni)**")
        b.dataframe(pd.DataFrame(kw["dunn"]).round(4), width="stretch")
        st.info("Madura berbeda dari Mataraman (p = 0,0097) dan Tapal Kuda (p = 0,017). Kawasan Madura hanya n = 4, jadi daya uji rendah; pembagian kawasan adalah asumsi umum.")
    elif uji.startswith("Hubungan"):
        d = pd.DataFrame(H["spearman"], columns=["Variabel", "Pembanding", "ρ", "p"])
        d["Signifikan"] = np.where(d["p"] < .05, "ya", "tidak")
        st.dataframe(d, hide_index=True, width="stretch")
        st.info("MKJP berkorelasi positif kuat dengan iBangga dan RLS (ρ ≈ 0,62); TFR berkorelasi negatif (ρ ≈ −0,43). Indeks keseluruhan tidak signifikan. Komponen iBangga bisa memuat indikator KB, sehingga sebagian korelasi melingkar.")
    elif uji.startswith("k sampel berpasangan"):
        cq = H["cochran"]
        s = pd.Series(cq["lebih_buruk"])
        st.plotly_chart(C.bar_horizontal(s.index.to_series(), s, T.BIRU, f"Jumlah daerah lebih buruk dari Jatim (n lengkap = {cq['n']})", teks=s.astype(str), rentang=[0, 26]), width="stretch")
        st.markdown(f"Cochran's Q = **{cq['Q']:.3f}**, df = {cq['df']}, p = **{cq['p']:.4f}** → gagal tolak H0.")
        st.info("Proporsi daerah yang tertinggal tidak berbeda nyata antar indikator, walau MKJP paling banyak (21 dari 37).")
    elif uji.startswith("Independensi"):
        ch = H["chi2"]
        st.dataframe(pd.DataFrame(ch["tabel"]).T, width="stretch")
        st.markdown(f"Chi-square = {ch['chi2']:.3f}, p = {ch['p']:.4f}; frekuensi harapan minimum {ch['min_expected']} (< 5, kurang andal). "
                    f"Fisher exact (Rendah vs bukan Rendah × tipe): OR = {ch['fisher_or']:.3f}, p = {ch['fisher_p']:.4f}.")
        st.info("Kategori capaian tidak berhubungan dengan tipe wilayah (kota/kabupaten).")
    else:
        pv = H["prevalensi"]
        k = st.columns(4)
        k[0].metric("Median 2023", f"{pv['median_2023']}%")
        k[1].metric("Median 2025", f"{pv['median_2025']}%")
        k[2].metric("Daerah yang turun", f"{pv['turun']} dari {pv['n']}")
        k[3].metric("Median selisih", f"{pv['median_selisih']} poin")
        st.markdown(f"Wilcoxon signed-rank 2023 vs 2025: W = {pv['W']:.0f}, p = {pv['p']:.1e}. Konsistensi dengan CPR SiPerindu: Spearman {pv['spearman_cpr']} (p = {pv['spearman_p']}).")
        st.info("Prevalensi KB aktif turun nyata dari 2023 ke 2025. Kab. Lamongan dikeluarkan (PUS 2023 diduga salah cetak); PUS KB 2024 tidak dipakai karena tidak konsisten.")

# ------------------------------------------------------------ Catatan
with t5:
    st.subheader("Keterbatasan")
    for i, s in enumerate(H["keterbatasan"], 1):
        st.markdown(f"{i}. {s}")
