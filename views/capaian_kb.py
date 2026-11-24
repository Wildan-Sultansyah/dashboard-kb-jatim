import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.decomposition import PCA

from kbdash import charts as C, stats as S, theme as T
from kbdash.data import muat_p1, muat_json, prioritas_per_indikator, INDIKATOR, LABEL, NAIK_BAIK, KAWASAN_URUT
from kbdash.teks import INDIKATOR_AWAM, UJI, NAMA_UJI

T.pasang_halaman("Capaian KB di Jawa Timur", kicker="Seberapa jauh program KB menjangkau tiap daerah",
                 ringkas="Lima ukuran keberhasilan KB tahun 2025 digabung menjadi satu skor untuk 38 kabupaten/kota, "
                         "lalu dibandingkan dengan angka Provinsi Jawa Timur. Klik, pilih, dan geser untuk menjelajah.")
df = muat_p1()
H = muat_json("p1_hasil.json")
jatim = muat_json("p1_jatim.json")
NAMA_IND = {c: INDIKATOR_AWAM[c][0] for c in INDIKATOR}
WIL = dict(zip(df["nama"], df["wilayah"]))


def p_txt(p: float) -> str:
    return "< 0,001" if p < 0.001 else T.fmt(p, 3)


med = H["kruskal_kawasan"]["median"]
k3 = df[df["klaster"] == "K3"]
T.intinya(
    f"Capaian KB di Jawa Timur <b>tidak merata</b>. Kawasan <b>Madura</b> paling tertinggal, dan {len(k3)} daerah "
    f"({', '.join(k3['nama'].head(4))}, dll.) perlu perhatian khusus karena lemah di hampir semua ukuran. "
    f"Kota dan kabupaten ternyata <b>tidak</b> selalu berbeda: yang membedakan terutama kawasan dan pemakaian KB jangka panjang.")

t1, t2, t3, t4, t5, t6 = st.tabs(["🗺️ Peta capaian", "🎯 Daerah yang perlu perhatian", "👥 Kelompok daerah",
                                  "🔬 Apa kata statistik?", "🧪 Coba sendiri", "📌 Catatan"])

# ======================================================================== 1. PETA
with t1:
    c1, c2, c3 = st.columns([1.6, 1.2, 1.2])
    opsi = {"Skor gabungan": "indeks", "Tingkat capaian (tinggi / sedang / rendah)": "kategori", "Kelompok daerah": "klaster"}
    opsi.update({NAMA_IND[c]: c for c in INDIKATOR})
    pil = c1.selectbox("Yang ingin dilihat di peta", list(opsi), key="ck_lapisan")
    sorot = c2.selectbox("Sorot satu daerah", ["(tidak ada)"] + sorted(df["nama"]), key="ck_sorot")
    kaw = c3.selectbox("Daftar daerah menurut kawasan", ["Semua kawasan"] + KAWASAN_URUT, key="ck_kawasan")
    kol = opsi[pil]
    wsor = WIL.get(sorot)
    teks = df["nama"] + "<br>Skor " + df["indeks"].round(2).astype(str) + " · " + df["kategori"] + " · " + df["klaster"].map(T.NAMA_KLASTER)
    a, b = st.columns([1.25, 1])
    with a:
        if kol == "indeks":
            fig = C.peta_kontinu(df, "indeks", "Skor gabungan capaian KB", T.SKALA_DIVERGING,
                                 zmin=-1.5, zmax=1.5, teks=teks, colorbar_judul="skor", sorot=wsor)
        elif kol == "kategori":
            fig = C.peta_kategori(df, "kategori", T.WARNA_KATEGORI, "Tingkat capaian", teks=teks,
                                  urutan=["Tinggi", "Sedang", "Rendah"], sorot=wsor)
        elif kol == "klaster":
            fig = C.peta_kategori(df, "klaster", T.WARNA_KLASTER, "Kelompok daerah", teks=teks,
                                  urutan=["K1", "K2", "K3"], nama_legenda=T.NAMA_KLASTER, sorot=wsor)
        else:
            d_ = 2 if kol == "TFR" else 1
            tek = df["nama"] + f"<br>{NAMA_IND[kol]}: " + df[kol].round(d_).astype(str) + f" (Jatim {jatim[kol]})"
            fig = C.peta_kontinu(df.assign(zz=df["z_" + kol]), "zz",
                                 NAMA_IND[kol],
                                 T.SKALA_DIVERGING, zmin=-3, zmax=3, teks=tek, colorbar_judul="lebih baik →", sorot=wsor)
        st.plotly_chart(fig, width="stretch")
        if kol in INDIKATOR:
            st.caption(f"**{NAMA_IND[kol]}** — {INDIKATOR_AWAM[kol][1]} {INDIKATOR_AWAM[kol][2]}. Angka Jatim: {T.fmt(jatim[kol], 2 if kol == 'TFR' else 1)}.")
    with b:
        if wsor:
            r = df[df["nama"] == sorot].iloc[0]
            st.markdown(T.chip(f"Capaian {r['kategori'].lower()}", T.WARNA_KATEGORI[r["kategori"]]) +
                        T.chip(T.NAMA_KLASTER[r["klaster"]], T.WARNA_KLASTER[r["klaster"]]) +
                        T.chip(r["kawasan"], T.WARNA_KAWASAN[r["kawasan"]]), unsafe_allow_html=True)
            T.kpi_baris([("Peringkat", f"{int(r['peringkat'])} dari 38", "1 = terbaik", T.BIRU),
                         ("Skor gabungan", T.fmt(r["indeks"]), "0 = rata-rata daerah", T.PINK if r["indeks"] < 0 else T.BIRU)])
            prio = [r[f"prioritas{i}"] for i in (1, 2, 3) if r[f"prioritas{i}"] != "-"]
            st.markdown("**Yang perlu dibenahi lebih dulu:** " + ("; ".join(prio) if prio else "tidak ada, semua ukuran sudah lebih baik dari angka Jatim."))
        d = df if kaw == "Semua kawasan" else df[df["kawasan"] == kaw]
        d = d.sort_values("indeks")
        st.plotly_chart(C.bar_horizontal(d["nama"], d["indeks"], d["kategori"].map(T.WARNA_KATEGORI),
                                         "Skor gabungan per daerah (warna = tingkat capaian)", tinggi=max(320, 22 * len(d) + 70),
                                         rentang=[-2.6, 1.3]), width="stretch")
    T.cara_baca("Skor <b>0</b> berarti sama dengan rata-rata 38 daerah. Skor <b>positif</b> (biru) berarti lebih baik, skor <b>negatif</b> (merah muda) berarti lebih rendah. "
                "Arahkan kursor ke daerah di peta untuk melihat angkanya.")
    with st.expander("Lihat rapor lengkap: skor tiap daerah pada tiap ukuran"):
        z = df.sort_values("indeks", ascending=False).set_index("nama")[["z_" + c for c in INDIKATOR]]
        z.columns = [NAMA_IND[c] for c in INDIKATOR]
        st.plotly_chart(C.heatmap(z, T.SKALA_DIVERGING, "Biru = lebih baik dari rata-rata, merah muda = lebih rendah (diurutkan dari skor tertinggi)",
                                  zmin=-3, zmax=3, tinggi=900, colorbar_judul="skor"), width="stretch")
        st.caption(f"Ketahanan skor: bila dihitung dengan cara lain (relatif terhadap angka Jatim, atau tanpa TFR), urutan daerah tetap sangat mirip "
                   f"(kemiripan {H['ketahanan']['spearman_relatif_jatim']:.2f} dan {H['ketahanan']['spearman_tanpa_tfr']:.2f} dari maksimum 1).")

# ======================================================================== 2. PRIORITAS
with t2:
    st.markdown("Daerah mana yang masih di bawah angka Jatim, dan pada ukuran apa? Pilih filter di bawah.")
    c = st.columns(3)
    f_kaw = c[0].multiselect("Kawasan", KAWASAN_URUT, default=KAWASAN_URUT, key="pr_kaw")
    f_kat = c[1].multiselect("Tingkat capaian", ["Rendah", "Sedang", "Tinggi"], default=["Rendah", "Sedang", "Tinggi"], key="pr_kat")
    f_kls = c[2].multiselect("Kelompok", ["K1", "K2", "K3"], default=["K1", "K2", "K3"], format_func=lambda k: T.NAMA_KLASTER[k], key="pr_kls")
    d = df[df["kawasan"].isin(f_kaw) & df["kategori"].isin(f_kat) & df["klaster"].isin(f_kls)].sort_values("peringkat")
    st.markdown(f"**{len(d)} daerah** sesuai filter.")
    tab = d[["peringkat", "nama", "kawasan", "kategori", "indeks", "prioritas1", "prioritas2", "prioritas3"]].copy()
    tab["indeks"] = tab["indeks"].round(2)
    tab.columns = ["Peringkat", "Kab/Kota", "Kawasan", "Tingkat capaian", "Skor", "Dibenahi pertama", "Kedua", "Ketiga"]
    st.dataframe(tab, hide_index=True, width="stretch", height=430,
                 column_config={"Skor": st.column_config.ProgressColumn("Skor", min_value=-2.6, max_value=1.3, format="%.2f"),
                                  "Dibenahi pertama": st.column_config.TextColumn(width="large"),
                                  "Kedua": st.column_config.TextColumn(width="large"),
                                  "Ketiga": st.column_config.TextColumn(width="large")})
    T.cara_baca("Kolom <b>Dibenahi pertama–ketiga</b> memuat ukuran yang lebih buruk dari angka Jatim, paling tertinggal lebih dulu. "
                "Format: nilai daerah (angka Jatim) → arah dan besar perbaikan yang dibutuhkan.")
    a, b = st.columns(2)
    with a:
        p = prioritas_per_indikator(d)
        if len(p):
            st.plotly_chart(C.bar_horizontal(p.index.to_series(), p, T.PINK, "Ukuran yang paling sering jadi masalah utama (daerah terpilih)",
                                             teks=p.astype(str)), width="stretch")
        else:
            st.info("Tidak ada daerah dengan masalah utama pada filter ini.")
    with b:
        s = pd.Series(H["tambahan_peserta"]).rename(index=lambda w: w.title())
        st.plotly_chart(C.bar_horizontal(s.index.to_series(), s, (T.SKALA_BIRU, 0, 40000), "Perkiraan tambahan peserta KB agar pemakai KB daerah setara Jatim",
                                         teks=s.map(lambda v: f"{v:,.0f}".replace(",", "."))), width="stretch")
    T.awas("Angka tambahan peserta adalah perkiraan kasar (selisih pemakai KB dengan Jatim × jumlah pasangan usia subur), bukan target resmi.")

# ======================================================================== 3. KELOMPOK
with t3:
    st.markdown("Daerah dikelompokkan otomatis berdasarkan kemiripan pola capaiannya. Hasilnya **tiga kelompok**.")
    isi = {"K1": "Pemakaian KB sudah kuat; banyak yang butuh KB sudah terlayani dan sedikit yang berhenti memakai.",
           "K2": "Unggul pada KB jangka panjang (IUD, implan, steril), ukuran lain rata-rata.",
           "K3": "Lemah pada pemakaian KB, KB jangka panjang, kebutuhan yang belum terlayani, dan putus pakai."}
    cols = st.columns(3)
    for col, k_ in zip(cols, ["K1", "K2", "K3"]):
        pk = H["profil_klaster"][k_]
        with col.container(border=True):
            st.markdown(T.chip(T.NAMA_KLASTER[k_], T.WARNA_KLASTER[k_]), unsafe_allow_html=True)
            st.markdown(f"### {pk['n']} daerah")
            st.markdown(isi[k_])
            st.caption("Contoh paling mewakili: " + H["medoid"][k_])
            with st.expander("Lihat daerahnya"):
                st.write(", ".join(df[df["klaster"] == k_]["nama"]))
    a, b = st.columns([1.25, 1])
    with a:
        X = df[["z_" + c for c in INDIKATOR]].fillna(0).values
        pca = PCA(n_components=2).fit(X)
        sc = pca.transform(X)
        fig = go.Figure()
        simb = {"K1": "circle", "K2": "square", "K3": "triangle-up"}
        for k_ in ["K1", "K2", "K3"]:
            m = (df["klaster"] == k_).values
            fig.add_trace(go.Scatter(x=sc[m, 0], y=sc[m, 1], mode="markers", name=T.NAMA_KLASTER[k_], text=df["nama"][m],
                                     marker=dict(size=12, color=T.WARNA_KLASTER[k_], symbol=simb[k_], line=dict(color="white", width=1.2)),
                                     hovertemplate="%{text}<extra>" + T.NAMA_KLASTER[k_] + "</extra>"))
            i = int(np.where(df["nama"] == H["medoid"][k_])[0][0])
            fig.add_trace(go.Scatter(x=[sc[i, 0]], y=[sc[i, 1]], mode="markers+text", text=[H["medoid"][k_]], textposition="top center",
                                     marker=dict(size=20, symbol="star", color=T.WARNA_KLASTER[k_], line=dict(color="#0b2a5b", width=1.2)),
                                     showlegend=False, hovertemplate=H["medoid"][k_] + "<extra>contoh mewakili</extra>"))
        fig.update_layout(height=470, margin=dict(l=0, r=0, t=34, b=0), title=dict(text="Peta kemiripan daerah (makin dekat = polanya makin mirip)", x=0, font=dict(size=14)),
                          xaxis_title="capaian: lebih rendah → lebih tinggi", yaxis_title=None,
                          legend=dict(orientation="h", y=-0.2))
        fig.update_xaxes(showticklabels=False, gridcolor="rgba(120,130,190,.18)")
        fig.update_yaxes(showticklabels=False, gridcolor="rgba(120,130,190,.18)")
        st.plotly_chart(fig, width="stretch")
        st.caption("Bintang = daerah yang paling mewakili kelompoknya. Daerah di perbatasan antar kelompok: " + ", ".join(H["perbatasan"]) + ".")
    with b:
        pilih = st.radio("Apakah kelompok ini juga berbeda dalam hal lain?", ["Kualitas keluarga (iBangga)", "Lama sekolah (tahun)"], key="kl_ekstra")
        kolx = "iBangga" if pilih.startswith("Kualitas") else "RLS_2025"
        g = df.groupby("klaster")[kolx].mean().reindex(["K1", "K2", "K3"])
        st.plotly_chart(C.bar_horizontal(g.index.map(T.NAMA_KLASTER).to_series(), g, g.index.map(T.WARNA_KLASTER).tolist(), f"Rata-rata {pilih.split(' (')[0].lower()} per kelompok",
                                         teks=g.round(1).astype(str), urut=False), width="stretch")
        pe = H["kruskal_klaster_eksternal"]["iBangga" if kolx == "iBangga" else "RLS_2025"]
        T.verdict(pe["p"] < .05, "Ya, kelompok ini berbeda nyata", "Tidak berbeda nyata", f"nilai p = {p_txt(pe['p'])}")
        T.catatan("Kelompok K2 punya kualitas keluarga dan lama sekolah tertinggi, jadi pengelompokan mencerminkan kondisi nyata, bukan sekadar hitungan.")
    with st.expander("Detail teknis pengelompokan (untuk yang ingin tahu)"):
        v = pd.DataFrame(H["validasi_klaster"]).rename(columns={"k": "Jumlah kelompok", "silhouette": "Silhouette", "ch": "Calinski-Harabasz", "db": "Davies-Bouldin", "terkecil": "Kelompok terkecil"})
        st.dataframe(v, hide_index=True, width="stretch")
        st.markdown(f"Metode PCA + K-Medoids dengan {H['k_terpilih']} kelompok. Kestabilan ketika data diacak sebagian: {H['ari_stabilitas']['rata']:.2f} (maks 1); "
                    f"kecocokan dengan metode lain (Ward): {H['ari_ward']:.2f}.")

# ======================================================================== 4. STATISTIK
with t4:
    st.markdown("Pilih **pertanyaan** yang ingin dijawab. Setiap jawaban disertai grafik yang bisa diubah-ubah; nama ujinya ada di bagian bawah untuk yang ingin tahu.")
    kunci = st.selectbox("Pertanyaan", list(UJI), format_func=lambda k: UJI[k], key="uji_pil")
    st.markdown(f"## {UJI[kunci]}")
    pilih_var = {"indeks": "Skor gabungan"} | {c: NAMA_IND[c] for c in INDIKATOR}
    BALIK = {v: k for k, v in pilih_var.items()}

    if kunci == "bentuk":
        v = st.selectbox("Ukuran yang diperiksa", list(pilih_var), format_func=lambda k: pilih_var[k], key="u1_var")
        x = df[v].dropna()
        fig = go.Figure(go.Histogram(x=x, nbinsx=12, marker=dict(color=T.BIRU, line=dict(color="white", width=1.5)),
                                     hovertemplate="%{x}: %{y} daerah<extra></extra>"))
        fig.add_vline(x=x.median(), line_color=T.PINK, line_width=3, annotation_text="nilai tengah", annotation_font_color=T.PINK)
        fig.update_layout(height=340, margin=dict(l=0, r=0, t=20, b=0), yaxis_title="jumlah daerah", xaxis_title=pilih_var[v], bargap=0.05)
        st.plotly_chart(fig, width="stretch")
        sh = pd.DataFrame(H["shapiro"])
        sh["Sebaran simetris?"] = np.where(sh["p"] > .05, "ya", "tidak")
        n_tidak = int((sh["p"] <= .05).sum())
        T.verdict(False, f"Sebagian ukuran tidak simetris ({n_tidak} dari {len(sh)})",
                  "Karena itu rata-rata bisa menyesatkan", "Dashboard memakai nilai tengah dan peringkat, bukan rata-rata biasa, supaya daerah ekstrem tidak mendistorsi hasil.")
        with st.expander("Nama uji dan angka teknis"):
            st.caption(f"Uji: {NAMA_UJI['bentuk']}. Simetris bila p > 0,05.")
            st.dataframe(sh.rename(columns={"v": "Ukuran", "mean": "Rata-rata", "sd": "Simpangan baku", "p": "p"}), hide_index=True, width="stretch")

    elif kunci == "acuan":
        c = st.columns([1.2, 1.4, 1])
        v = c[0].selectbox("Ukuran", INDIKATOR, format_func=lambda k: NAMA_IND[k], key="u2_var")
        opsi_acuan = ["Angka Provinsi Jatim", "Atur sendiri"] + (["Target Renstra 2025"] if v in ("DCR", "TFR") else [])
        jenis = c[1].radio("Angka acuan", opsi_acuan, horizontal=True, key="u2_jenis")
        renstra = {"DCR": 18.7, "TFR": 1.98}
        x = df[v].dropna()
        if jenis == "Angka Provinsi Jatim":
            acuan = float(jatim[v])
        elif jenis == "Target Renstra 2025":
            acuan = renstra[v]
        else:
            acuan = c[2].number_input("Angka", value=float(round(x.median(), 2)), step=0.1 if v != "TFR" else 0.01, key="u2_num")
        r = S.wilcoxon_vs_nilai(x, acuan)
        dd = 2 if v == "TFR" else 1
        lebih_buruk = (x < acuan) if NAIK_BAIK[v] else (x > acuan)
        warna = [T.PINK if b_ else T.BIRU for b_ in lebih_buruk]
        o = df.loc[x.index].assign(_w=warna, _y=x)
        o = o.sort_values("_y")
        fig = go.Figure(go.Bar(x=o["nama"], y=o["_y"], marker=dict(color=o["_w"]), hovertemplate="%{x}: %{y}<extra></extra>"))
        fig.add_hline(y=acuan, line_color="#0b2a5b", line_width=2.5, annotation_text=f"acuan {T.fmt(acuan, dd)}", annotation_position="top left")
        fig.update_layout(height=360, margin=dict(l=0, r=0, t=20, b=0), xaxis_tickangle=-60, yaxis_title=NAMA_IND[v], bargap=0.2,
                          xaxis_title=None)
        st.plotly_chart(fig, width="stretch")
        n_buruk = int(lebih_buruk.sum())
        st.markdown(T.chip(f"{n_buruk} daerah lebih buruk dari acuan", T.PINK) + T.chip(f"{len(x) - n_buruk} lebih baik", T.BIRU), unsafe_allow_html=True)
        arah = "lebih tinggi" if r["median"] > acuan else "lebih rendah"
        T.verdict(r["p"] < .05, f"Ya: nilai tengah daerah {arah} dari acuan secara nyata",
                  "Tidak ada perbedaan nyata dari acuan", f"Nilai tengah 38 daerah {T.fmt(r['median'], dd)} vs acuan {T.fmt(acuan, dd)} · nilai p = {p_txt(r['p'])}")
        if jenis == "Angka Provinsi Jatim":
            T.catatan("Angka Jatim adalah gabungan seluruh daerahnya sendiri, jadi wajar bila daerah-daerah umumnya tidak berbeda nyata darinya. "
                      "Coba bandingkan DCR atau TFR dengan target Renstra untuk melihat perbedaan yang nyata.")
        with st.expander("Nama uji dan angka teknis"):
            st.caption(f"Uji: {NAMA_UJI['acuan']}. Statistik W = {r['statistik']:.1f}, n = {r['n']}.")

    elif kunci == "kota":
        v = st.selectbox("Ukuran yang dibandingkan", list(pilih_var), format_func=lambda k: pilih_var[k], key="u3_var")
        r = S.mannwhitney(df[df["tipe"] == "Kota"][v], df[df["tipe"] == "Kabupaten"][v])
        wt = {"Kabupaten": T.BIRU, "Kota": T.PINK}
        st.plotly_chart(C.kotak(df, v, "tipe", ["Kabupaten", "Kota"], wt, f"{pilih_var[v]}: tiap titik adalah satu daerah", pilih_var[v]), width="stretch")
        dd = 2 if v in ("indeks", "TFR") else 1
        T.verdict(r["p"] < .05, "Ya, kota dan kabupaten berbeda nyata", "Tidak ada perbedaan nyata antara kota dan kabupaten",
                  f"Nilai tengah kota {T.fmt(r['median1'], dd)} vs kabupaten {T.fmt(r['median2'], dd)} · nilai p = {p_txt(r['p'])}")
        T.catatan("Temuan utama: untuk skor gabungan, kota dan kabupaten tidak berbeda; perbedaan nyata hanya pada KB jangka panjang (kota lebih tinggi). Pilih 'KB jangka panjang' untuk melihatnya.")
        with st.expander("Nama uji dan angka teknis"):
            st.caption(f"Uji: {NAMA_UJI['kota']}. U = {r['statistik']:.1f}; n kota = {r['n1']}, n kabupaten = {r['n2']}.")

    elif kunci == "kawasan":
        v = st.selectbox("Ukuran yang dibandingkan", list(pilih_var), format_func=lambda k: pilih_var[k], key="u4_var")
        g = {k_: df[df["kawasan"] == k_][v] for k_ in KAWASAN_URUT}
        kw = S.kruskal(g)
        dn = S.dunn(g).loc[KAWASAN_URUT, KAWASAN_URUT]
        a, b = st.columns([1.2, 1])
        a.plotly_chart(C.kotak(df, v, "kawasan", KAWASAN_URUT, T.WARNA_KAWASAN, f"{pilih_var[v]} per kawasan", pilih_var[v]), width="stretch")
        pas = [(x_, y_, dn.loc[x_, y_]) for i, x_ in enumerate(KAWASAN_URUT) for y_ in KAWASAN_URUT[i + 1:]]
        with b:
            fig = go.Figure(go.Heatmap(z=dn.clip(upper=0.1).values, x=KAWASAN_URUT, y=KAWASAN_URUT, zmin=0, zmax=0.1,
                                       colorscale=[[0, T.PINK], [0.5, T.EMAS], [1, T.PUCAT]], showscale=False, xgap=3, ygap=3,
                                       text=[["" if i == j else ("beda nyata" if dn.iloc[i, j] < .05 else "tidak beda") for j in range(4)] for i in range(4)],
                                       texttemplate="%{text}", textfont=dict(size=11, color="#0b2a5b"),
                                       customdata=dn.values, hovertemplate="%{y} vs %{x}<br>nilai p = %{customdata:.4f}<extra></extra>"))
            fig.update_layout(title=dict(text="Pasangan kawasan mana yang berbeda?", x=0, font=dict(size=14)), height=380, margin=dict(l=0, r=0, t=34, b=0))
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, width="stretch")
        T.verdict(kw["p"] < .05, "Ya, ada kawasan yang berbeda nyata", "Tidak ada perbedaan nyata antar kawasan", f"nilai p = {p_txt(kw['p'])}")
        beda = [f"{x_} dan {y_}" for x_, y_, p_ in pas if p_ < .05]
        st.markdown("**Pasangan yang berbeda nyata:** " + (", ".join(beda) if beda else "tidak ada pada ukuran ini."))
        T.awas("Kawasan Madura hanya terdiri dari 4 daerah, sehingga perbandingannya kurang kuat. Pembagian kawasan juga merupakan asumsi umum.")
        with st.expander("Nama uji dan angka teknis"):
            st.caption(f"Uji: {NAMA_UJI['kawasan']} (koreksi Bonferroni). H = {kw['statistik']:.3f}, p = {kw['p']:.4f}.")
            st.dataframe(dn.round(4), width="stretch")

    elif kunci == "kualitas":
        c = st.columns(2)
        v = c[0].selectbox("Ukuran KB", list(pilih_var), format_func=lambda k: pilih_var[k], key="u5_x", index=2)
        yv = c[1].radio("Dibandingkan dengan", ["iBangga", "RLS_2025"], format_func=lambda k: {"iBangga": "Kualitas keluarga (iBangga)", "RLS_2025": "Lama sekolah"}[k],
                        horizontal=True, key="u5_y")
        r = S.spearman(df[v], df[yv])
        fig = go.Figure(go.Scatter(x=df[v], y=df[yv], mode="markers", name="Daerah", text=df["nama"],
                                   marker=dict(size=11, color=T.BIRU, line=dict(color="white", width=1.2)),
                                   hovertemplate="%{text}<br>" + pilih_var[v] + " %{x}<br>" + yv + " %{y}<extra></extra>"))
        d2 = df[[v, yv]].dropna()
        if len(d2) > 2:
            kemiringan, titik0 = np.polyfit(d2[v], d2[yv], 1)
            gx = np.array([d2[v].min(), d2[v].max()])
            fig.add_trace(go.Scatter(x=gx, y=kemiringan * gx + titik0, mode="lines", name="Garis kecenderungan",
                                     line=dict(color="#e03131", width=3), hoverinfo="skip"))
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=20, b=0), xaxis_title=pilih_var[v],
                          yaxis_title={"iBangga": "iBangga (kualitas keluarga)", "RLS_2025": "Lama sekolah (tahun)"}[yv],
                          legend=dict(orientation="h", y=-0.22, x=0))
        st.plotly_chart(fig, width="stretch")
        kuat = "kuat" if abs(r["rho"]) >= .5 else ("sedang" if abs(r["rho"]) >= .3 else "lemah")
        arah = "makin tinggi ukuran KB ini, makin tinggi pula nilai pembandingnya" if r["rho"] > 0 else "makin tinggi ukuran KB ini, makin rendah nilai pembandingnya"
        T.verdict(r["p"] < .05, f"Ya, ada hubungan {kuat}: {arah}", "Tidak ada hubungan yang nyata", f"kekuatan hubungan {T.fmt(r['rho'])} (−1 s/d +1) · nilai p = {p_txt(r['p'])}")
        T.awas("Hubungan tidak berarti sebab-akibat. Sebagian komponen iBangga juga memuat KB, sehingga sebagian hubungan bersifat melingkar.")
        with st.expander("Nama uji dan angka teknis"):
            st.caption(f"Uji: {NAMA_UJI['kualitas']}. ρ = {r['rho']:.3f}, p = {r['p']:.4f}, n = {r['n']}.")
            st.dataframe(pd.DataFrame(H["spearman"], columns=["Ukuran KB", "Pembanding", "ρ", "p"]), hide_index=True, width="stretch")

    elif kunci == "tertinggal":
        cq = H["cochran"]
        s = pd.Series(cq["lebih_buruk"]).rename(index={"CPR modern": NAMA_IND["CPR"], "MKJP": NAMA_IND["MKJP"], "Unmet need": NAMA_IND["UnmetNeed"],
                                                       "DCR": NAMA_IND["DCR"], "TFR": NAMA_IND["TFR"]})
        st.plotly_chart(C.bar_horizontal(s.index.to_series(), s, (T.SKALA_PINK, 8, 26), f"Jumlah daerah yang lebih buruk dari angka Jatim (dari {cq['n']} daerah)",
                                         teks=s.astype(str), rentang=[0, 28]), width="stretch")
        T.verdict(cq["p"] < .05, "Ya, ada ukuran yang lebih sering tertinggal", "Tidak ada ukuran yang nyata lebih sering tertinggal",
                  f"nilai p = {p_txt(cq['p'])}. KB jangka panjang paling banyak tertinggal (21 daerah), tetapi selisihnya belum cukup besar untuk disebut nyata.")
        with st.expander("Nama uji dan angka teknis"):
            st.caption(f"Uji: {NAMA_UJI['tertinggal']}. Q = {cq['Q']:.3f}, df = {cq['df']}, p = {cq['p']:.4f}.")

    elif kunci == "jenis":
        ch = H["chi2"]
        tb = pd.DataFrame(ch["tabel"]).T.loc[["Tinggi", "Sedang", "Rendah"]]
        mode = st.radio("Tampilkan", ["Jumlah daerah", "Persentase"], horizontal=True, key="u7_mode")
        fig = go.Figure()
        for t_ in ["Kabupaten", "Kota"]:
            val = tb[t_] if mode == "Jumlah daerah" else tb[t_] / tb[t_].sum() * 100
            fig.add_trace(go.Bar(x=tb.index, y=val, name=t_, marker=dict(color={"Kabupaten": T.BIRU, "Kota": T.PINK}[t_]),
                                 text=[f"{v:.0f}" + ("%" if mode != "Jumlah daerah" else "") for v in val], textposition="outside",
                                 hovertemplate=t_ + " · %{x}: %{y:.0f}<extra></extra>"))
        fig.update_layout(barmode="group", height=340, margin=dict(l=0, r=0, t=20, b=0), xaxis_title="Tingkat capaian",
                          yaxis_title=mode, legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width="stretch")
        T.verdict(ch["p"] < .05, "Ya, tingkat capaian terkait jenis wilayah", "Tingkat capaian tidak terkait jenis wilayah",
                  f"Kota maupun kabupaten tersebar di semua tingkat capaian · nilai p = {p_txt(ch['p'])}")
        with st.expander("Nama uji dan angka teknis"):
            st.caption(f"Uji: {NAMA_UJI['jenis']}. Chi-square = {ch['chi2']:.3f}, p = {ch['p']:.4f}; frekuensi harapan terkecil {ch['min_expected']} (kurang dari 5, sehingga uji Fisher "
                       f"dipakai sebagai pembanding: OR = {ch['fisher_or']:.3f}, p = {ch['fisher_p']:.4f}).")

    else:
        pv = H["prevalensi"]
        T.kpi_baris([("Nilai tengah 2023", f"{pv['median_2023']}%", "pasangan usia subur ber-KB aktif", T.BIRU),
                     ("Nilai tengah 2025", f"{pv['median_2025']}%", "pasangan usia subur ber-KB aktif", T.PINK),
                     ("Daerah yang turun", f"{pv['turun']} dari {pv['n']}", "menurun dari 2023 ke 2025", T.PINK),
                     ("Perubahan tipikal", f"{T.fmt(pv['median_selisih'], 1)} poin", "nilai tengah selisih", T.EMAS)])
        fig = go.Figure(go.Bar(x=["2023", "2025"], y=[pv["median_2023"], pv["median_2025"]], marker=dict(color=[T.BIRU, T.PINK]),
                               text=[f"{pv['median_2023']}%", f"{pv['median_2025']}%"], textposition="outside"))
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0), yaxis=dict(range=[0, 90], title="% KB aktif (nilai tengah)"), bargap=0.55)
        st.plotly_chart(fig, width="stretch")
        T.verdict(pv["p"] < .05, "Ya, pemakaian KB aktif turun secara nyata", "Tidak ada perubahan nyata", f"nilai p = {p_txt(pv['p'])}")
        T.awas("Kab. Lamongan dikeluarkan (data 2023 diduga salah cetak). Jumlah pasangan usia subur 2024 tidak dipakai karena tidak konsisten.")
        with st.expander("Nama uji dan angka teknis"):
            st.caption(f"Uji: {NAMA_UJI['waktu']}. W = {pv['W']:.0f}, p = {pv['p']:.1e}. Selaras dengan pemakai KB modern di SiPerindu (kemiripan urutan {pv['spearman_cpr']}).")

# ======================================================================== 5. COBA SENDIRI
with t5:
    st.markdown("Skor gabungan dihitung dengan **bobot sama** untuk kelima ukuran. Bagaimana kalau Anda menganggap sebagian ukuran lebih penting? "
                "Geser bobot di bawah dan lihat peringkat berubah.")
    cols = st.columns(5)
    bobot = {c: cols[i].slider(NAMA_IND[c], 0, 5, 1, key=f"w_{c}") for i, c in enumerate(INDIKATOR)}
    if sum(bobot.values()) == 0:
        st.warning("Setidaknya satu ukuran harus punya bobot lebih dari 0.")
    else:
        Z = df[["z_" + c for c in INDIKATOR]]
        W = pd.Series({"z_" + c: bobot[c] for c in INDIKATOR})
        baru = (Z * W).sum(axis=1, skipna=True) / (Z.notna() * W).sum(axis=1)
        rk = baru.rank(ascending=False, method="min").astype(int)
        o = df.assign(skor_baru=baru, rank_baru=rk, geser=df["peringkat"] - rk).sort_values("rank_baru")
        a, b = st.columns([1.2, 1])
        with a:
            n = st.slider("Tampilkan berapa daerah terbawah", 5, 20, 10, key="w_n")
            bw = o.tail(n)
            st.plotly_chart(C.bar_horizontal(bw["nama"], bw["skor_baru"], (T.SKALA_PINK[::-1], bw["skor_baru"].min(), 0.2),
                                             f"{n} daerah dengan skor terendah menurut bobot Anda", tinggi=max(300, 28 * n + 70)), width="stretch")
        with b:
            st.plotly_chart(C.peta_kontinu(o, "skor_baru", "Skor menurut bobot Anda", T.SKALA_DIVERGING, zmin=-1.5, zmax=1.5, colorbar_judul="skor", tinggi=420), width="stretch")
        tb = pd.DataFrame({"Peringkat baru": o["rank_baru"], "Kab/Kota": o["nama"], "Skor baru": o["skor_baru"].round(2),
                           "Peringkat semula": o["peringkat"], "Naik/turun": o["geser"].map(lambda g: f"▲ {g}" if g > 0 else (f"▼ {-g}" if g < 0 else "="))})
        st.dataframe(tb, hide_index=True, width="stretch", height=340)
        if all(v == 1 for v in bobot.values()):
            st.success("Bobot sama: hasilnya persis seperti skor gabungan di halaman ini.")
        else:
            naik = o.sort_values("geser", ascending=False).iloc[0]
            turun = o.sort_values("geser").iloc[0]
            T.intinya(f"Dengan bobot Anda, <b>{naik['nama']}</b> naik paling banyak ({int(naik['geser'])} peringkat) dan <b>{turun['nama']}</b> turun paling banyak "
                      f"({int(-turun['geser'])} peringkat). Daerah yang peringkatnya jarang bergeser adalah daerah yang konsisten.", "Hasilnya")

# ======================================================================== 6. CATATAN
with t6:
    st.markdown("Hal-hal yang perlu diingat saat membaca halaman ini:")
    for i, s in enumerate(H["keterbatasan"], 1):
        st.markdown(f"**{i}.** {s}")
