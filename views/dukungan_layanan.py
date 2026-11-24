import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from kbdash import charts as C, theme as T
from kbdash.data import muat_gabungan, muat_json, hitung_woa

T.pasang_halaman("Dukungan Layanan KB", kicker="Apakah tempat layanan, penyuluh, dan stok alat KB sudah memadai?",
                 ringkas="Di mana dukungan layanan KB lemah, apakah daerah itu juga yang capaiannya rendah, dan alat KB apa yang stoknya menipis? "
                         "Halaman ini menunjukkan kesenjangan dan prioritas, bukan sebab-akibat.",
                 warna=("#7048e8", "#d6336c"))
df = muat_gabungan()
H = muat_json("p2_hasil.json")
BULAN = ["Sep", "Okt", "Nov", "Des"]
BKOL = {"Sep": "kritis_sep", "Okt": "kritis_okt", "Nov": "kritis_nov", "Des": "kritis_des"}
WIL = dict(zip(df["nama"], df["wilayah"]))
menetap = df[df["menetap"]]["nama"].tolist()
dijaga = df[df["tip"] == "C"]["nama"].tolist()
r_, p_ = H["kesesuaian"]["capaian_vs_dukungan"]

T.intinya(
    "Daerah yang <b>capaian KB-nya rendah</b> belum tentu yang <b>dukungan layanannya lemah</b> (dan sebaliknya): keduanya hampir tidak berkaitan di data ini. "
    f"Namun ada <b>{len(menetap)} daerah</b> yang stok alat KB-nya menipis terus-menerus selama September–Desember 2025, dan {len(dijaga)} daerah "
    "berstatus <b>perlu dijaga</b> (capaian masih tinggi tetapi dukungannya lemah).")

t1, t2, t3, t4, t5 = st.tabs(["🗺️ Peta dukungan", "⚖️ Dukungan vs capaian", "📦 Stok alat KB", "🎯 Prioritas penguatan", "📌 Catatan"])

# ======================================================================== 1. PETA DUKUNGAN
with t1:
    st.markdown("**Skor dukungan** (0–1) menggabungkan tiga hal dengan bobot sama: jumlah tempat layanan KB, jumlah penyuluh KB (PKB), dan kecukupan stok alat KB.")
    c = st.columns([1.6, 1.2, 1.2])
    lap = c[0].selectbox("Yang ingin dilihat", ["Skor dukungan", "Tempat layanan KB (per 10.000 pasangan usia subur)",
                                                "Penyuluh KB (per 10.000 pasangan usia subur)", "Jumlah jenis alat KB yang stoknya kritis"], key="dk_lap")
    sorot = c[1].selectbox("Sorot satu daerah", ["(tidak ada)"] + sorted(df["nama"]), key="dk_sorot")
    bln = c[2].select_slider("Bulan (untuk stok)", BULAN, value="Nov", key="dk_bln", disabled=not lap.startswith("Jumlah"))
    wsor = WIL.get(sorot)
    tek = (df["nama"] + "<br>Skor dukungan " + df["dukungan"].round(2).astype(str) + "<br>Tempat layanan " + df["layanan_per10k"].astype(str) +
           " · Penyuluh " + df["pkb_per10k"].astype(str) + " per 10.000 PUS<br>Stok kritis (Nov): " + df["stok_kritis_nov"].astype(str) + " jenis")
    a, b = st.columns([1.2, 1])
    with a:
        if lap.startswith("Skor"):
            fig = C.peta_kontinu(df, "dukungan", "Skor dukungan layanan", T.SKALA_BIRU, teks=tek, colorbar_judul="skor", sorot=wsor)
            kol, asc, jud = "dukungan", True, "Skor dukungan terendah"
        elif lap.startswith("Tempat"):
            fig = C.peta_kontinu(df, "layanan_per10k", "Tempat layanan KB per 10.000 PUS", T.SKALA_BIRU, teks=tek, colorbar_judul="per 10.000", sorot=wsor)
            kol, asc, jud = "layanan_per10k", True, "Tempat layanan paling sedikit"
        elif lap.startswith("Penyuluh"):
            fig = C.peta_kontinu(df, "pkb_per10k", "Penyuluh KB per 10.000 PUS", T.SKALA_BIRU, teks=tek, colorbar_judul="per 10.000", sorot=wsor)
            kol, asc, jud = "pkb_per10k", True, "Penyuluh paling sedikit"
        else:
            kol = BKOL[bln]
            fig = C.peta_kontinu(df, kol, f"Stok kritis, {bln} 2025", T.SKALA_PINK, zmin=0, zmax=8,
                                 teks=df["nama"] + f"<br>{bln}: " + df[kol].astype(str) + " dari 8 jenis kritis", colorbar_judul="jenis", sorot=wsor)
            asc, jud = False, f"Stok kritis terbanyak ({bln})"
        st.plotly_chart(fig, width="stretch")
    with b:
        n = st.slider("Tampilkan berapa daerah", 5, 20, 10, key="dk_n")
        d = df.sort_values(kol, ascending=asc).head(n)
        warna = T.PINK if asc else (T.SKALA_PINK, 0, 8)
        st.plotly_chart(C.bar_horizontal(d["nama"], d[kol], warna, f"{jud}: {n} daerah", tinggi=max(300, 24 * n + 70),
                                         teks=d[kol].round(2).astype(str)), width="stretch")
    T.cara_baca("Stok disebut <b>kritis</b> bila gudang kabupaten/kota hanya punya kurang dari satu bulan kebutuhan (ini asumsi penelitian). "
                "Ada 8 jenis alat KB yang dipantau, jadi angka 8 berarti semuanya kritis.")
    with st.expander("Apakah daerah yang lemah mengelompok (berdekatan)?"):
        lisa_map = {"High-High": "Kelompok kuat", "Low-Low": "Kelompok lemah", "High-Low": "Daerah yang berbeda dari tetangga",
                    "Low-High": "Daerah yang berbeda dari tetangga", "Tidak signifikan": "Tidak ada pola"}
        gi_map = {"Hotspot dukungan kuat": "Kelompok kuat", "Coldspot dukungan lemah": "Kelompok lemah", "Tidak signifikan": "Tidak ada pola"}
        dd = df.assign(pola1=df["lisa"].map(lisa_map), pola2=df["gi"].map(gi_map))
        x, y = st.columns(2)
        x.plotly_chart(C.peta_kategori(dd, "pola1", T.WARNA_POLA, "Daerah yang mirip dengan tetangganya", teks=dd["nama"] + "<br>" + dd["pola1"],
                                       urutan=list(T.WARNA_POLA), tinggi=420), width="stretch")
        y.plotly_chart(C.peta_kategori(dd, "pola2", T.WARNA_POLA, "Gugus daerah dengan dukungan kuat/lemah", teks=dd["nama"] + "<br>" + dd["pola2"],
                                       urutan=["Kelompok kuat", "Kelompok lemah", "Tidak ada pola"], tinggi=420), width="stretch")
        st.markdown(f"Hasil: **hampir tidak ada pola** (kemiripan antar tetangga {H['moran_dukungan']['I']:.3f}, nyaris nol). Artinya masalah dukungan "
                    "tersebar di berbagai daerah, bukan menumpuk di satu wilayah. Daerah dengan kelompok lemah: " +
                    (", ".join(df[df["lisa"] == "Low-Low"]["nama"]) or "tidak ada") + ".")

# ======================================================================== 2. DUKUNGAN VS CAPAIAN
with t2:
    st.markdown("Setiap titik adalah satu daerah. **Kanan** = dukungan lebih kuat, **atas** = capaian lebih tinggi. Garis putus-putus menunjukkan nilai tengah.")
    sor = st.selectbox("Sorot satu daerah", ["(tidak ada)"] + sorted(df["nama"]), key="vs_sorot")
    a, b = st.columns([1.15, 1])
    with a:
        fig = go.Figure()
        simbol = {"A": "circle", "B": "square", "C": "triangle-up", "D": "diamond"}
        for t, sub in df.groupby("tip"):
            fig.add_trace(go.Scatter(x=sub["dukungan"], y=sub["indeks"], mode="markers", name=T.NAMA_TIPOLOGI[t], text=sub["nama"],
                                     marker=dict(size=12, color=T.WARNA_TIPOLOGI[t], symbol=simbol[t], line=dict(color="white", width=1.2)),
                                     hovertemplate="%{text}<br>dukungan %{x:.2f} · capaian %{y:.2f}<extra></extra>"))
        if sor != "(tidak ada)":
            rr = df[df["nama"] == sor].iloc[0]
            fig.add_trace(go.Scatter(x=[rr["dukungan"]], y=[rr["indeks"]], mode="markers+text", text=[sor], textposition="top center", showlegend=False,
                                     marker=dict(size=24, color="rgba(0,0,0,0)", line=dict(color="#0b2a5b", width=3)), hoverinfo="skip"))
        fig.add_hline(y=df["indeks"].median(), line_dash="dash", line_color=T.INDIGO, opacity=.5)
        fig.add_vline(x=df["dukungan"].median(), line_dash="dash", line_color=T.INDIGO, opacity=.5)
        fig.update_layout(height=470, margin=dict(l=0, r=0, t=10, b=0), xaxis_title="Skor dukungan layanan (0–1)  →  lebih kuat",
                          yaxis_title="Skor capaian KB  →  lebih tinggi", legend=dict(orientation="h", y=-0.22, font=dict(size=11)))
        fig.update_xaxes(gridcolor="rgba(120,130,190,.15)")
        fig.update_yaxes(gridcolor="rgba(120,130,190,.15)")
        st.plotly_chart(fig, width="stretch")
    with b:
        st.plotly_chart(C.peta_kategori(df, "tip", T.WARNA_TIPOLOGI, "Peta tipologi daerah", teks=df["nama"] + "<br>" + df["tipologi"],
                                        urutan=list("ABCD"), nama_legenda=T.NAMA_TIPOLOGI, sorot=WIL.get(sor), tinggi=470), width="stretch")
    T.kpi_baris([(T.NAMA_TIPOLOGI[t].split(" · ")[1], f"{int((df['tip'] == t).sum())} daerah", f"Tipe {t}", T.WARNA_TIPOLOGI[t]) for t in "ABCD"])
    pilih = st.radio("Lihat daerah menurut tipe", list("ABCD"), format_func=lambda t: T.NAMA_TIPOLOGI[t], horizontal=True, key="vs_tip")
    sub = df[df["tip"] == pilih].sort_values("dukungan")
    st.markdown("**" + ", ".join(sub["nama"]) + "**")
    st.markdown("> " + sub["rekomendasi"].iloc[0])
    ks = H["kesesuaian"]
    T.cara_baca(f"Jika dukungan selalu menentukan capaian, titik-titik akan naik dari kiri bawah ke kanan atas. Kenyataannya titik-titik <b>tersebar acak</b> "
                f"(kekuatan hubungan hanya {T.fmt(r_)} dari maksimum 1, tidak nyata; nilai p = {T.fmt(p_)}). Ini <b>bukan</b> bukti bahwa dukungan tidak penting; "
                "mungkin alasan capaian rendah ada di sisi permintaan (budaya, pengetahuan), bukan pasokan.")
    with st.expander("Seberapa kuat pembagian tipe ini?"):
        sens = H["sensitivitas_tipologi"]
        st.markdown("Beberapa daerah berada dekat batas sehingga tipenya bisa berubah jika skor dukungan dihitung dengan cara lain: " +
                    "; ".join(f"cara **{k_}**: {', '.join(v)}" for k_, v in sens.items()) + ".")
        st.markdown(f"Hubungan per komponen (juga lemah): tempat layanan {T.fmt(ks['layanan'][0])}, penyuluh {T.fmt(ks['pkb'][0])}, stok {T.fmt(ks['stok'][0])}.")

# ======================================================================== 3. STOK ALAT KB
with t3:
    st.markdown("Stok alat dan obat KB di gudang kabupaten/kota, **September–Desember 2025** (bulan lain tidak dipakai karena laporan stoknya belum lengkap).")
    a, b = st.columns([1.1, 1])
    with a:
        z = df.set_index("nama")[list(BKOL.values())]
        z.columns = BULAN
        z = z.assign(r=z.mean(axis=1)).sort_values("r", ascending=False).drop(columns="r")
        mn = st.slider("Tampilkan daerah dengan rata-rata jenis kritis minimal", 0, 6, 3, key="st_min")
        z2 = z[z.mean(axis=1) >= mn]
        st.plotly_chart(C.heatmap(z2, T.SKALA_PINK, f"Jenis alat KB yang stoknya kritis, per bulan (0–8) · {len(z2)} daerah", zmin=0, zmax=8, fmt=".0f",
                                  tinggi=max(260, 22 * len(z2) + 110), colorbar_judul="jenis"), width="stretch")
    with b:
        alok = list(H["stok_nol"])
        pil = st.selectbox("Pilih alat KB", alok, index=alok.index("Suntik kombinasi"), key="st_alok")
        v = H["stok_nol"][pil]
        fig = go.Figure(go.Bar(x=BULAN, y=v, marker=dict(color=T.PINK), text=v, textposition="outside",
                               hovertemplate="%{x}: %{y} daerah kehabisan<extra></extra>"))
        fig.update_layout(title=dict(text=f"Daerah yang stok {pil} habis (= 0)", x=0, font=dict(size=14)), height=300, margin=dict(l=0, r=0, t=34, b=0),
                          yaxis=dict(range=[0, 40], title="dari 38 daerah"), bargap=0.45)
        st.plotly_chart(fig, width="stretch")
        kos = df[df["alokon_kosong_nov"].str.contains(pil, regex=False)]["nama"].tolist()
        st.markdown(f"**November 2025:** {len(kos)} daerah kehabisan {pil}" + (": " + ", ".join(kos) if kos and len(kos) <= 15 else "."))
        nol = pd.DataFrame(H["stok_nol"], index=BULAN).T
        nol = nol.loc[nol.mean(axis=1).sort_values(ascending=False).index]
        st.plotly_chart(C.heatmap(nol, T.SKALA_PINK, "Daerah yang kehabisan, per jenis alat KB", zmin=0, zmax=38, fmt=".0f", tinggi=380, colorbar_judul="daerah"), width="stretch")
    st.subheader("Daerah dengan stok menipis terus-menerus")
    mt = df[df["menetap"]].sort_values("kritis_des", ascending=False)
    pilih_mt = st.multiselect("Tampilkan daerah", mt["nama"].tolist(), default=mt["nama"].tolist()[:5], key="st_mt")
    fig = go.Figure()
    pal = [T.PINK, T.UNGU, T.EMAS, T.BIRU, T.HIJAU, T.INDIGO, "#e8590c", "#0b7285"]
    for i, nm in enumerate(pilih_mt):
        r = mt[mt["nama"] == nm].iloc[0]
        fig.add_trace(go.Scatter(x=BULAN, y=[r.kritis_sep, r.kritis_okt, r.kritis_nov, r.kritis_des], mode="lines+markers", name=nm,
                                 line=dict(color=pal[i % len(pal)], width=3), marker=dict(size=9, line=dict(color="white", width=1.5)),
                                 hovertemplate=nm + ": %{y} jenis<extra></extra>"))
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(range=[0, 8.5], title="Jenis alat KB kritis"), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, width="stretch")
    st.markdown("**Paling membaik (September → Desember):** " + ", ".join(f"{k_} ({v} jenis pulih)" for k_, v in H["membaik"].items()) +
                ". **Paling memburuk:** " + ", ".join(f"{k_} (+{v})" for k_, v in H["memburuk"].items()) + ".")

# ======================================================================== 4. PRIORITAS
with t4:
    st.markdown("**Daerah mana yang paling perlu diperkuat lebih dulu?** Skor prioritas menggabungkan empat hal. Seberapa penting masing-masing? "
                "Itu **pertimbangan peneliti**, jadi geser sendiri dan lihat apakah daftar teratas berubah.")
    b0 = H["bobot_woa"]
    c = st.columns(4)
    w = {"capaian_rendah": c[0].slider("Capaian KB rendah", 0.0, 1.0, b0["capaian_rendah"], 0.05, key="wo_a"),
         "layanan_rendah": c[1].slider("Tempat layanan sedikit", 0.0, 1.0, b0["layanan_rendah"], 0.05, key="wo_b"),
         "pkb_rendah": c[2].slider("Penyuluh sedikit", 0.0, 1.0, b0["pkb_rendah"], 0.05, key="wo_c"),
         "stok_kritis": c[3].slider("Stok alat KB menipis", 0.0, 1.0, b0["stok_kritis"], 0.05, key="wo_d")}
    if sum(w.values()) == 0:
        st.warning("Setidaknya satu bobot harus lebih dari 0.")
        st.stop()
    total = sum(w.values())
    st.caption("Bobot otomatis disesuaikan hingga berjumlah 100%: " + " · ".join(f"{k_.replace('_', ' ')} {v / total:.0%}" for k_, v in w.items()))
    res = hitung_woa(df, w)
    top_n = st.slider("Tampilkan berapa daerah teratas", 5, 20, 12, key="wo_n")
    d = df.assign(skor=res["skor"], peringkat_baru=res["peringkat"]).sort_values("skor", ascending=False)
    top = d.head(top_n)
    a, b = st.columns([1.2, 1])
    with a:
        nama = {"capaian_rendah": "Capaian KB rendah", "layanan_rendah": "Tempat layanan sedikit", "pkb_rendah": "Penyuluh sedikit", "stok_kritis": "Stok menipis"}
        warna = {"capaian_rendah": T.PINK, "layanan_rendah": T.UNGU, "pkb_rendah": T.EMAS, "stok_kritis": T.BIRU}
        fig = go.Figure()
        for k_ in nama:
            fig.add_trace(go.Bar(y=top["nama"], x=res.loc[top.index, k_], name=nama[k_], orientation="h",
                                 marker=dict(color=warna[k_], line=dict(color="white", width=1.5)),
                                 hovertemplate="%{y}<br>" + nama[k_] + ": %{x:.3f}<extra></extra>"))
        fig.update_layout(barmode="stack", title=dict(text=f"Apa yang membuat {top_n} daerah ini diprioritaskan", x=0, font=dict(size=14)),
                          height=max(340, 28 * top_n + 130), margin=dict(l=0, r=0, t=34, b=0), yaxis=dict(autorange="reversed"),
                          xaxis_title="Skor prioritas (makin panjang makin diprioritaskan)", legend=dict(orientation="h", y=-0.12, font=dict(size=11)))
        st.plotly_chart(fig, width="stretch")
    with b:
        tk = d["nama"] + "<br>Skor " + d["skor"].round(2).astype(str) + " · peringkat " + d["peringkat_baru"].astype(str)
        st.plotly_chart(C.peta_kontinu(d, "skor", "Skor prioritas penguatan", T.SKALA_PINK, teks=tk, colorbar_judul="skor", tinggi=440), width="stretch")
    tab = pd.DataFrame({"Peringkat": top["peringkat_baru"], "Kab/Kota": top["nama"], "Skor": top["skor"].round(2), "Tipe": top["tip"],
                        "Peringkat bawaan": top["rank_prioritas"], "Stok kritis (Nov)": top["stok_kritis_nov"],
                        "Selalu 10 besar": top["tangguh"].map({True: "ya", False: ""})})
    st.dataframe(tab, hide_index=True, width="stretch")
    if w == b0:
        st.success("Bobot bawaan: peringkat sama dengan hasil analisis awal.")
    tg = df[df["tangguh"]].sort_values("rank_prioritas")["nama"]
    T.intinya("Daerah yang <b>selalu masuk 10 besar</b> walau bobotnya diubah-ubah (paling layak diprioritaskan): " + ", ".join(tg) + ".", "Yang konsisten")
    with st.expander("Seberapa goyah daftar ini jika asumsinya berubah?"):
        sk = pd.DataFrame(H["skenario_woa"], columns=["Skenario", "Kemiripan urutan dengan hasil utama (maks 1)", "Dari 10 teratas, yang tetap sama"])
        st.dataframe(sk, hide_index=True, width="stretch")
        st.caption("Semakin dekat ke 1 dan 10, semakin tahan daftar prioritas terhadap perubahan asumsi. Tanpa memasukkan capaian KB, daftar paling berubah.")

# ======================================================================== 5. CATATAN
with t5:
    st.markdown("Hal-hal yang perlu diingat saat membaca halaman ini:")
    cat = ["Bobot, ambang stok kritis, dan pembagian tipe adalah **pertimbangan peneliti**, bukan standar resmi; karena itu diuji dengan beberapa skenario.",
           "Yang boleh disimpulkan: **kesesuaian, kesenjangan, dan prioritas**. Bukan pengaruh atau sebab-akibat.",
           f"Pola menurut letak daerah lemah: kemiripan antar tetangga hanya {H['moran_dukungan']['I']:.3f}, sehingga hanya sedikit daerah yang terdeteksi berkelompok.",
           "Stok hanya dari gudang kabupaten/kota, September–Desember 2025, saat laporan stok cukup lengkap (November 100% gudang melapor).",
           "Hubungan capaian dan dukungan mendekati nol: dalam data ini keduanya tidak selaras, bukan bukti bahwa dukungan tidak penting."]
    for i, s in enumerate(cat, 1):
        st.markdown(f"**{i}.** {s}")
