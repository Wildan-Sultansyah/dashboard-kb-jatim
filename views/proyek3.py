import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from kbdash import charts as C, theme as T
from kbdash.data import muat_json, ASSETS

T.pasang_halaman("Proyek 3 · Suara Publik tentang Alokon", kicker="Analitik Media Sosial + Data Storytelling",
                 ringkas="Analisis komentar YouTube tentang alat dan obat kontrasepsi: sentimen, topik, dan pertanyaan publik. "
                         "Komentar individual tidak ditampilkan; dashboard hanya memuat hasil agregat.")
H = muat_json("p3_hasil.json")
NM = H["alokon_nama"]
R = H["ringkas"]
SENT = ["negatif", "netral", "positif"]

def idn(n): return f"{n:,}".replace(",", ".")

tabs = st.tabs(["Data", "Sentimen", "Topik", "Pertanyaan publik", "Rekomendasi", "Catatan"])

# ------------------------------------------------------------ Data
with tabs[0]:
    k = st.columns(4)
    k[0].metric("Komentar dianalisis", idn(R["komentar"]), help=f"Dari {idn(R['mentah'])} komentar mentah")
    k[1].metric("Video", R["video"])
    k[2].metric("Tahun komentar", f"{R['awal'][:4]}–{R['akhir'][:4]}", help=f"{R['awal']} s.d. {R['akhir']}")
    k[3].metric("Berbentuk pertanyaan", f"{R['pertanyaan_pct']}%")
    a, b = st.columns(2)
    with a:
        cl = H["cleaning"]
        s = pd.Series({n: v for n, v in cl})
        fig = go.Figure(go.Bar(y=s.index, x=s.values, orientation="h", marker=dict(color=T.BIRU), text=[idn(v) for v in s.values],
                               textposition="outside", cliponaxis=False, hovertemplate="%{y}: %{x}<extra></extra>"))
        fig.update_layout(title=dict(text="Pembersihan data: komentar tersisa tiap langkah", x=0, font=dict(size=14)), height=340,
                          margin=dict(l=0, r=40, t=34, b=0), yaxis=dict(autorange="reversed"), xaxis=dict(range=[2400, 3200], gridcolor="rgba(128,128,128,.18)"))
        st.plotly_chart(fig, width="stretch")
    with b:
        src = H["alokon_sumber"]
        urut = sorted(src, key=lambda k_: -sum(src[k_]))
        fig = go.Figure()
        fig.add_trace(go.Bar(y=[NM[k_] for k_ in urut], x=[src[k_][0] for k_ in urut], orientation="h", name="Terdeteksi dari teks komentar",
                             marker=dict(color=T.BIRU, line=dict(color="white", width=1.5))))
        fig.add_trace(go.Bar(y=[NM[k_] for k_ in urut], x=[src[k_][1] for k_ in urut], orientation="h", name="Dari kata kunci video",
                             marker=dict(color=T.ORANYE, line=dict(color="white", width=1.5))))
        fig.update_layout(barmode="stack", title=dict(text="Komentar per alokon dan sumber label", x=0, font=dict(size=14)), height=340,
                          margin=dict(l=0, r=0, t=34, b=0), yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=-0.15),
                          xaxis=dict(gridcolor="rgba(128,128,128,.18)"))
        st.plotly_chart(fig, width="stretch")
    T.catatan("Sebesar 54,5% label alokon berasal dari kata kunci video, bukan dari isi komentar. Karena itu hasil per alokon diuji ulang pada komentar yang menyebut alokon di teks (tab Sentimen).")
    st.image(str(ASSETS / "p3_01_ringkasan.png"), caption="Ringkasan data dari notebook, termasuk kontribusi video (bias sumber data)")

# ------------------------------------------------------------ Sentimen
with tabs[1]:
    sb = H["sentimen_bert"]; tot = sum(sb.values())
    k = st.columns(3)
    for col, s in zip(k, SENT):
        col.metric(s.capitalize(), f"{sb[s] / tot * 100:.1f}%", f"{idn(sb[s])} komentar", delta_color="off")
    st.markdown("Metode utama **IndoRoBERTa** (pretrained, tanpa pelatihan ulang), dibanding baseline kamus **InSet**. "
                "**Belum ada evaluasi terhadap label manual** (0 komentar berlabel), sehingga akurasi belum diketahui; angka di bawah adalah keluaran model.")
    mode = st.radio("Data", ["Semua komentar", "Hanya alokon terdeteksi dari teks (uji ketahanan)"], horizontal=True)
    sumber = H["sentimen_per_alokon"] if mode == "Semua komentar" else H["sentimen_per_alokon_teks"]
    d = pd.DataFrame(sumber, index=SENT).T
    d.index = [NM[i] for i in d.index]
    d = d.sort_values("negatif")
    a, b = st.columns([1.3, 1])
    with a:
        st.plotly_chart(C.stacked_pct(d, T.WARNA_SENTIMEN, "Sentimen per alokon"), width="stretch")
    with b:
        q = pd.DataFrame(H["sentimen_pertanyaan"], index=SENT).T
        st.plotly_chart(C.stacked_pct(q, T.WARNA_SENTIMEN, "Pertanyaan vs bukan pertanyaan", tinggi=230), width="stretch")
        j = pd.DataFrame(H["sentimen_per_jenis"], index=SENT).T.sort_values("negatif")
        st.plotly_chart(C.stacked_pct(j, T.WARNA_SENTIMEN, "Sentimen per jenis percakapan", tinggi=330), width="stretch")
    st.info("Pertanyaan hampir selalu dilabeli negatif oleh model (77,5%), padahal pedoman pelabelan menempatkan pertanyaan informatif sebagai netral. "
            "Ini salah satu alasan angka negatif perlu dibaca hati-hati dan divalidasi dengan label manual.")
    a, b = st.columns(2)
    with a:
        mt = H["kesepakatan_metode"]
        m = pd.DataFrame(mt["matriks"], index=SENT).T
        m.index = [f"Lexicon: {i}" for i in m.index]; m.columns = [f"IndoRoBERTa: {c}" for c in m.columns]
        st.plotly_chart(C.heatmap(m, T.SKALA_BIRU, f"Kesepakatan dua metode (sama persis {mt['sama_persis']}%)", zmin=0, zmax=100, fmt=".0f", tinggi=300, colorbar_judul="%"), width="stretch")
    with b:
        lx = H["sentimen_lexicon"]; lt = sum(lx.values())
        st.markdown("**Baseline lexicon (InSet)** menilai " + ", ".join(f"{s} {lx[s] / lt * 100:.0f}%" for s in SENT) + ". Lexicon cenderung membaca kata keluhan (mis. sakit, tidak) sebagai negatif.")
    st.image(str(ASSETS / "p3_02_per_bulan.png"), caption="Proporsi sentimen per bulan (bulan dengan n ≥ 30). Perubahan banyak dipengaruhi video yang ramai, bukan tren publik.")
    st.image(str(ASSETS / "p3_03_kata_khas.png"), caption="Kata yang paling khas di komentar negatif vs positif")

# ------------------------------------------------------------ Topik
with tabs[2]:
    st.markdown("Topik dari **BERTopic** (embedding multilingual + K-Means, 10 topik). Nama topik masih otomatis (kata kunci teratas); penamaan manual belum dilakukan.")
    tp = H["topik"]
    kol = H["topik_kolom_alokon"]
    d = pd.DataFrame({"Topik": [f"T{i + 1}: {t['kata']}" for i, t in enumerate(tp)], "Komentar": [t["n"] for t in tp]})
    fig = go.Figure(go.Bar(y=d["Topik"], x=d["Komentar"], orientation="h", marker=dict(color=T.BIRU), text=d["Komentar"], textposition="outside",
                           cliponaxis=False, hovertemplate="%{y}: %{x}<extra></extra>"))
    fig.update_layout(title=dict(text=f"Ukuran topik (komentar tak terkelompok/terlalu pendek: {H['topik_tak_terkelompok']})", x=0, font=dict(size=14)),
                      height=380, margin=dict(l=0, r=40, t=34, b=0), yaxis=dict(autorange="reversed"), xaxis=dict(gridcolor="rgba(128,128,128,.18)"))
    st.plotly_chart(fig, width="stretch")
    z = pd.DataFrame([t["alokon"] for t in tp], index=[f"T{i + 1}: {t['kata']}" for i, t in enumerate(tp)], columns=[NM[k_] for k_ in kol])
    z = z[[NM[k_] for k_ in ["iud", "suntik", "implan", "pil", "steril", "lebih_dari_satu", "tidak_teridentifikasi", "kondom"]]]
    st.plotly_chart(C.heatmap(z, T.SKALA_BIRU, "Komposisi alokon dalam tiap topik (% komentar topik; tiap baris = 100%)", zmin=0, zmax=60, tinggi=420, colorbar_judul="%"), width="stretch")
    st.info("Topik 'hadir / keb / kader / tpk' (67% pil) dan 'link / post / tes' (100% pil) kemungkinan didorong satu-dua video tertentu, bukan keluhan substantif. "
            "Topik berbasis kata 'haid', 'bulan', 'pasang' mendominasi dan tumpang tindih; baca sebagai tema umum, bukan kategori tegas.")
    st.image(str(ASSETS / "p3_04_wordcloud.jpg"), caption="Word cloud per alokon (pelengkap)")

# ------------------------------------------------------------ Pertanyaan
with tabs[3]:
    k = st.columns(3)
    k[0].metric("Pertanyaan publik", idn(H["pertanyaan_total"]))
    k[1].metric("Belum dibalas", f"{H['belum_dibalas_pct']}%")
    k[2].metric("Tema terbanyak", H["tema"][0][0], f"{H['tema'][0][2]}% pertanyaan", delta_color="off")
    t = pd.DataFrame(H["tema"], columns=["Tema", "Jumlah", "% dari pertanyaan", "% belum dibalas"]).sort_values("Jumlah")
    a, b = st.columns(2)
    with a:
        fig = go.Figure(go.Bar(y=t["Tema"], x=t["Jumlah"], orientation="h", marker=dict(color=t["% belum dibalas"], colorscale=T.SKALA_ORANYE, cmin=20, cmax=50,
                                                                                    colorbar=dict(title="% belum<br>dibalas", thickness=10)),
                               text=[f"{j}" for j in t["Jumlah"]], textposition="outside", cliponaxis=False,
                               customdata=t[["% belum dibalas"]], hovertemplate="%{y}<br>%{x} pertanyaan · %{customdata[0]}% belum dibalas<extra></extra>"))
        fig.update_layout(title=dict(text="Tema pertanyaan (warna = % belum dibalas)", x=0, font=dict(size=14)), height=400, margin=dict(l=0, r=40, t=34, b=0),
                          xaxis=dict(range=[0, 520], gridcolor="rgba(128,128,128,.18)"))
        st.plotly_chart(fig, width="stretch")
    with b:
        mode = st.radio("Heatmap tema per alokon berdasarkan", ["Pertanyaan saja", "Semua komentar"], horizontal=True)
        src = H["tema_pertanyaan_per_alokon"] if mode == "Pertanyaan saja" else H["isu_per_alokon"]
        z = pd.DataFrame(src, index=H["tema_kolom"]).T
        z.index = [NM[i] for i in z.index]
        z = z.loc[[NM[k_] for k_ in ["iud", "suntik", "implan", "pil", "steril", "lebih_dari_satu"]]]
        st.plotly_chart(C.heatmap(z, T.SKALA_BIRU, "% komentar yang menyentuh tiap tema", zmin=0, zmax=60, fmt=".0f", tinggi=400, colorbar_judul="%"), width="stretch")
    st.image(str(ASSETS / "p3_07_pertanyaan.jpg"), caption="Dari notebook: tema pertanyaan dan % belum dibalas per alokon")
    rm = pd.DataFrame(H["rumor"], columns=["Pola kata kunci", "Komentar", "% dari semua komentar"])
    st.markdown("**Indikasi kekhawatiran/desas-desus** (pencocokan kata kunci, bukan verifikasi)")
    st.dataframe(rm, hide_index=True, width="stretch")
    T.catatan("Apakah suatu klaim memang mitos harus diverifikasi dengan sumber resmi (BKKBN, Kemenkes, tenaga kesehatan), bukan oleh analisis ini.")

# ------------------------------------------------------------ Rekomendasi
with tabs[4]:
    st.markdown("Draf rekomendasi strategi KIE per alokon, disusun otomatis dari temuan di atas. **Wajib ditinjau dan divalidasi tenaga kesehatan/BKKBN** sebelum dipakai.")
    cols = st.columns(2)
    for i, r in enumerate(H["rekomendasi"]):
        with cols[i % 2].container(border=True):
            st.markdown(f"**{NM[r['alokon']]}** · n = {r['n']}")
            st.markdown(f"Pertanyaan {r['pct_q']}% · sentimen negatif {r['pct_neg']}%")
            for tm, n, u in r["tema"]:
                st.markdown(f"- {tm}: {n} pertanyaan, {u}% belum dibalas")
            st.markdown(f"**Draf:** buat konten edukasi/FAQ tentang {r['tema'][0][0].lower()} dan {r['tema'][1][0].lower()}, dan prioritaskan menjawab pertanyaan yang belum dibalas.")
    st.markdown(f"**Umum:** {H['belum_dibalas_pct']:.0f}% pertanyaan belum dibalas, jadi siapkan FAQ dan alur balasan komentar yang rutin.")

# ------------------------------------------------------------ Catatan
with tabs[5]:
    st.subheader("Keterbatasan")
    for i, s in enumerate(H["keterbatasan"], 1):
        st.markdown(f"{i}. {s}")
    st.image(str(ASSETS / "p3_08_metode.png"), caption="Kesepakatan lexicon vs IndoRoBERTa dan sebaran keyakinan model")
