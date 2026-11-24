import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from kbdash import charts as C, theme as T
from kbdash.data import muat_json, ASSETS

T.pasang_halaman("Suara Masyarakat tentang Alat KB", kicker="Apa yang dibicarakan warganet di YouTube",
                 ringkas="Ribuan komentar YouTube tentang alat dan obat kontrasepsi (alokon) dibaca dan dikelompokkan: apa perasaan mereka, "
                         "apa yang mereka tanyakan, dan apakah pertanyaannya terjawab. Komentar asli tidak ditampilkan; hanya ringkasannya.",
                 warna=("#e6a400", "#d6336c"))
H = muat_json("p3_hasil.json")
NM = H["alokon_nama"]
R = H["ringkas"]
SB = H["sentimen_bert"]
TOT = sum(SB.values())
NADA = {"negatif": "Negatif", "netral": "Netral", "positif": "Positif"}
WNADA = {NADA[k]: v for k, v in T.WARNA_SENTIMEN.items()}
JENIS = {"pertanyaan": "Bertanya", "keluhan": "Mengeluh", "testimoni": "Bercerita pengalaman", "mitos": "Menyebut kabar/mitos", "informasi": "Memberi informasi", "lainnya": "Komentar lain"}


def idn(n):
    return f"{n:,}".replace(",", ".")


neg = SB["negatif"] / TOT * 100
T.intinya(
    f"Dari <b>{idn(R['komentar'])} komentar</b>, sekitar <b>{neg / 10:.0f} dari 10 bernada negatif</b> (mengeluh atau khawatir), terutama soal <b>haid</b> dan "
    f"<b>proses pemasangan</b>. Hampir separuh komentar ({R['pertanyaan_pct']:.0f}%) berupa pertanyaan, dan <b>{H['belum_dibalas_pct']:.0f}% pertanyaan tidak dibalas</b>. "
    "Artinya ada kebutuhan informasi yang belum terpenuhi.")

t1, t2, t3, t4, t5, t6 = st.tabs(["📊 Gambaran umum", "💬 Perasaan mereka", "❓ Yang ditanyakan", "🧩 Topik pembicaraan", "💡 Saran tindak lanjut", "📌 Catatan"])

# ======================================================================== 1. GAMBARAN
with t1:
    T.kpi_baris([("Komentar dibaca", idn(R["komentar"]), f"dari {idn(R['mentah'])} komentar mentah", T.BIRU),
                 ("Video", str(R["video"]), "video YouTube tentang KB", T.UNGU),
                 ("Tahun komentar", f"{R['awal'][:4]}–{R['akhir'][:4]}", "rentang waktu", T.EMAS),
                 ("Berupa pertanyaan", f"{R['pertanyaan_pct']}%", "dari seluruh komentar", T.PINK)])
    a, b = st.columns(2)
    with a:
        n = pd.Series(H["alokon_n"]).rename(index=NM).sort_values()
        st.plotly_chart(C.bar_horizontal(n.index.to_series(), n, (T.SKALA_BIRU, 0, 750), "Jumlah komentar menurut alat KB yang dibicarakan", teks=n.map(idn)), width="stretch")
    with b:
        pil = st.selectbox("Jenis komentar untuk", ["Semua alat KB"] + [NM[k] for k in H["jenis_per_alokon"]], key="sm_jenis")
        if pil == "Semua alat KB":
            tot = sum(H["jenis_n"].values())
            v = pd.Series({JENIS[k]: H["jenis_n"][k] / tot * 100 for k in H["jenis_urut"]})
        else:
            kk = [k for k in H["jenis_per_alokon"] if NM[k] == pil][0]
            v = pd.Series({JENIS[k]: x for k, x in zip(H["jenis_urut"], H["jenis_per_alokon"][kk])})
        st.plotly_chart(C.bar_horizontal(v.index.to_series(), v, (T.SKALA_PINK, 0, 60), f"Isi komentar: {pil.lower()} (% komentar)",
                                         teks=v.map(lambda x: f"{x:.0f}%")), width="stretch")
    T.cara_baca("Satu komentar bisa dihitung ke satu jenis saja. <b>Bertanya</b> adalah yang terbanyak, terutama untuk IUD.")
    T.awas(f"Sebagian besar label alat KB (54,5%) diambil dari kata kunci judul video, bukan dari isi komentar. Karena itu bagian 'Perasaan mereka' memuat pengecekan ulang "
           "hanya pada komentar yang jelas menyebut alat KB.", "Tentang data")
    with st.expander("Bagaimana data dibersihkan sebelum dianalisis?"):
        s = pd.Series({k: v for k, v in H["cleaning"]})
        fig = go.Figure(go.Bar(y=s.index, x=s.values, orientation="h", marker=dict(color=T.BIRU), text=[idn(v) for v in s.values], textposition="outside", cliponaxis=False))
        fig.update_layout(height=340, margin=dict(l=0, r=50, t=10, b=0), yaxis=dict(autorange="reversed"), xaxis=dict(range=[2400, 3250], title="komentar yang tersisa"))
        st.plotly_chart(fig, width="stretch")

# ======================================================================== 2. PERASAAN
with t2:
    st.markdown("Setiap komentar dinilai **nada**-nya oleh komputer: negatif (mengeluh/khawatir), netral, atau positif.")
    c = st.columns([1.3, 1.7])
    mode = c[1].radio("Data yang dipakai", ["Semua komentar", "Hanya yang jelas menyebut alat KB di teksnya"], horizontal=True, key="sm_mode",
                      help="Pengecekan ulang: komentar yang alat KB-nya hanya diketahui dari judul video dikeluarkan.")
    sumber = H["sentimen_per_alokon"] if mode == "Semua komentar" else H["sentimen_per_alokon_teks"]
    opsi = ["Semua alat KB"] + [NM[k] for k in sumber]
    pil = c[0].selectbox("Alat KB", opsi, key="sm_alokon")
    if pil == "Semua alat KB":
        p = {NADA[s]: SB[s] / TOT * 100 for s in ["negatif", "netral", "positif"]}
    else:
        kk = [k for k in sumber if NM[k] == pil][0]
        p = dict(zip(NADA.values(), sumber[kk]))
    a, b = st.columns([1, 1.3])
    with a:
        st.plotly_chart(C.waffle(p, WNADA, "Dari 100 komentar"), width="stretch")
        st.caption(f"Setiap kotak = 1 dari 100 komentar tentang {pil.lower()}. Negatif = mengeluh atau khawatir.")
    with b:
        d = pd.DataFrame(sumber, index=list(NADA.values())).T
        d.index = [NM[i] for i in d.index]
        d = d.sort_values(NADA["negatif"])
        st.plotly_chart(C.stacked_pct(d, WNADA, "Perbandingan antar alat KB", sumbu="% komentar"), width="stretch")
    pr = max(p, key=p.get)
    T.verdict(pr.startswith("Negatif"), f"Paling banyak: {pr.split(' (')[0].lower()} ({p[pr]:.0f}%)", f"Paling banyak: {pr.split(' (')[0].lower()} ({p[pr]:.0f}%)",
              "Pil KB paling netral; suntik, IUD, dan implan paling banyak dikeluhkan." if pil == "Semua alat KB" else "")
    T.awas("Nada dinilai komputer dan <b>belum dicocokkan dengan penilaian manusia</b>, jadi anggap sebagai gambaran umum, bukan angka pasti. "
           "Pertanyaan hampir selalu dinilai negatif (77%) padahal bertanya belum tentu mengeluh, sehingga angka negatif kemungkinan agak berlebih.")
    with st.expander("Nada komentar menurut jenis komentar"):
        j = pd.DataFrame(H["sentimen_per_jenis"], index=list(NADA.values())).T
        j.index = [JENIS[i] for i in j.index]
        st.plotly_chart(C.stacked_pct(j.sort_values(NADA["negatif"]), WNADA, "Nada menurut isi komentar", tinggi=360), width="stretch")
    with st.expander("Seberapa sepakat dua cara penilaian komputer?"):
        mt = H["kesepakatan_metode"]
        m = pd.DataFrame(mt["matriks"], index=list(NADA.values())).T
        m.index = [f"Kamus kata: {i.lower()}" for i in m.index]
        m.columns = [f"Model bahasa: {c_.lower()}" for c_ in m.columns]
        st.plotly_chart(C.heatmap(m, T.SKALA_BIRU, f"Dua cara menilai sepakat pada {mt['sama_persis']}% komentar (baris = 100%)", zmin=0, zmax=100, fmt=".0f", tinggi=260, colorbar_judul="%"), width="stretch")
        st.caption("Cara kamus kata menilai nada dari kata-kata tertentu, sedangkan model bahasa memahami kalimat. Keduanya tidak selalu sepakat, itulah sebabnya hasil perlu dicek manusia.")

# ======================================================================== 3. PERTANYAAN
with t3:
    T.kpi_baris([("Pertanyaan masuk", idn(H["pertanyaan_total"]), "komentar berupa pertanyaan", T.BIRU),
                 ("Belum dibalas", f"{H['belum_dibalas_pct']}%", "tidak ada jawaban", T.PINK),
                 ("Tema terbanyak", H["tema"][0][0], f"{H['tema'][0][2]}% pertanyaan", T.EMAS)])
    c = st.columns([1.3, 1])
    pil = c[0].selectbox("Pertanyaan tentang", ["Semua alat KB"] + [NM[k] for k in H["tema_pertanyaan_per_alokon"]], key="sm_q")
    tk = H["tema_kolom"]
    if pil == "Semua alat KB":
        t = pd.DataFrame(H["tema"], columns=["Tema", "n", "pct", "bd"]).sort_values("pct")
        nilai, warna = t["pct"], (T.SKALA_PINK, 20, 50)
        teks = t.apply(lambda r: f"{r['pct']:.0f}%<br>({r['bd']:.0f}% tak dibalas)", axis=1)
        jud = "Tema pertanyaan (% pertanyaan). Makin pekat = makin sering tak dibalas"
        nama = t["Tema"]
    else:
        kk = [k for k in H["tema_pertanyaan_per_alokon"] if NM[k] == pil][0]
        s = pd.Series(H["tema_pertanyaan_per_alokon"][kk], index=tk).sort_values()
        nilai, warna, teks, nama = s, T.BIRU, s.map(lambda v: f"{v:.0f}%"), s.index.to_series()
        jud = f"Tema pertanyaan tentang {pil.lower()} (% pertanyaan)"
    with c[1]:
        st.write("")
    a, b = st.columns([1.4, 1])
    with a:
        st.plotly_chart(C.bar_horizontal(nama, nilai, warna, jud, teks=teks, rentang=[0, max(nilai) * 2.0], tinggi=420), width="stretch")
    with b:
        urut = sorted(H["tema"], key=lambda r: -r[3] if r[1] >= 100 else 0)[:3]
        T.intinya("<br>".join(f"• <b>{r[0]}</b>: {r[3]:.0f}% pertanyaannya belum dibalas" for r in urut), "Paling sering terabaikan")
        T.cara_baca("Satu pertanyaan bisa menyentuh lebih dari satu tema, jadi persentase tidak berjumlah 100%.")
    with st.expander("Kekhawatiran dan kabar burung yang muncul"):
        rm = pd.DataFrame(H["rumor"], columns=["Pola kata", "Jumlah komentar", "% dari semua komentar"])
        rm["Pola kata"] = rm["Pola kata"].map({"mandul / susah hamil / tidak subur": "Takut mandul / sulit hamil", "kanker / tumor": "Takut kanker / tumor",
                                               "katanya / kata orang / dengar": "\"Katanya\" / \"kata orang\"", "mitos / hoax": "Menyebut mitos / hoaks"})
        st.dataframe(rm, hide_index=True, width="stretch")
        st.caption("Dicari lewat kata kunci, bukan dibuktikan benar-salahnya. Kebenaran suatu klaim harus dicek ke sumber resmi (BKKBN, Kemenkes, tenaga kesehatan).")

# ======================================================================== 4. TOPIK
with t4:
    st.markdown("Komputer juga mengelompokkan komentar berdasarkan kata-kata yang sering muncul bersama. Hasilnya **10 kelompok pembicaraan**. "
                "Nama kelompok belum diberi label manual, jadi yang tampil adalah kata kunci utamanya.")
    tp = H["topik"]
    kol = H["topik_kolom_alokon"]
    nm_t = [f"Kelompok {i + 1}: {t['kata']}" for i, t in enumerate(tp)]
    pil = st.selectbox("Pilih kelompok", range(len(tp)), format_func=lambda i: f"{nm_t[i]}  ({tp[i]['n']} komentar)", key="sm_topik")
    a, b = st.columns([1, 1])
    with a:
        sz = pd.Series([t["n"] for t in tp], index=nm_t)
        wr = ["#1c7ed6" if i != pil else "#d6336c" for i in range(len(tp))]
        fig = go.Figure(go.Bar(y=[f"Kelompok {i + 1}" for i in range(len(tp))], x=sz.values, orientation="h", marker=dict(color=wr), text=sz.values, textposition="outside",
                               cliponaxis=False, hovertemplate="%{y}: %{x} komentar<extra></extra>"))
        fig.update_layout(title=dict(text="Besar tiap kelompok (yang dipilih berwarna pink)", x=0, font=dict(size=14)), height=380, margin=dict(l=0, r=40, t=34, b=0),
                          yaxis=dict(autorange="reversed"), xaxis=dict(range=[0, 520], gridcolor="rgba(120,130,190,.18)"))
        st.plotly_chart(fig, width="stretch")
    with b:
        comp = pd.Series(tp[pil]["alokon"], index=[NM[k] for k in kol]).sort_values()
        comp = comp[comp > 0]
        st.plotly_chart(C.bar_horizontal(comp.index.to_series(), comp, (T.SKALA_BIRU, 0, 60), f"Alat KB yang dibicarakan dalam kelompok {pil + 1} (%)",
                                         teks=comp.map(lambda v: f"{v:.0f}%"), tinggi=380), width="stretch")
    T.awas("Kelompok 9 (hadir/keb/kader/tpk) dan kelompok 10 (link/post/tes) kemungkinan dibentuk oleh satu-dua video tertentu, bukan keluhan yang sebenarnya. "
           "Kelompok dengan kata 'haid', 'bulan', 'pasang' saling tumpang tindih, jadi baca sebagai tema umum, bukan kotak yang tegas.")
    with st.expander("Kata yang paling sering muncul per alat KB"):
        st.image(str(ASSETS / "p3_04_wordcloud.jpg"), caption="Semakin besar kata, semakin sering muncul")
    with st.expander("Kata yang khas di komentar negatif dan positif"):
        st.image(str(ASSETS / "p3_03_kata_khas.png"))

# ======================================================================== 5. SARAN
with t5:
    st.markdown("Draf saran materi edukasi (KIE) untuk tiap alat KB, disusun dari temuan di halaman ini. **Perlu ditinjau tenaga kesehatan/BKKBN** sebelum dipakai.")
    pil = st.multiselect("Tampilkan alat KB", [NM[r["alokon"]] for r in H["rekomendasi"]], default=[NM[r["alokon"]] for r in H["rekomendasi"]], key="sm_rek")
    cols = st.columns(2)
    i = 0
    for r in H["rekomendasi"]:
        if NM[r["alokon"]] not in pil:
            continue
        with cols[i % 2].container(border=True):
            st.markdown(f"### {NM[r['alokon']]}")
            st.markdown(T.chip(f"{idn(r['n'])} komentar", T.BIRU) + T.chip(f"{r['pct_q']}% bertanya", T.UNGU) + T.chip(f"{r['pct_neg']}% negatif", T.PINK), unsafe_allow_html=True)
            st.markdown("**Yang paling sering ditanyakan:**")
            for tm, n, u in r["tema"]:
                st.markdown(f"- {tm} ({n} pertanyaan, {u}% belum dibalas)")
            st.markdown(f"**Saran:** buat konten penjelas atau FAQ tentang *{r['tema'][0][0].lower()}* dan *{r['tema'][1][0].lower()}*, "
                        "lalu prioritaskan membalas pertanyaan yang belum terjawab.")
        i += 1
    T.intinya(f"{H['belum_dibalas_pct']:.0f}% pertanyaan belum dibalas. Siapkan FAQ dan alur balasan komentar yang rutin di kanal resmi.", "Saran umum")

# ======================================================================== 6. CATATAN
with t6:
    st.markdown("Hal-hal yang perlu diingat saat membaca halaman ini:")
    cat = ["Sumbernya hanya komentar YouTube (cenderung perempuan dewasa yang mencari konsultasi), bukan seluruh masyarakat.",
           f"Data berasal dari {R['video']} video terpilih; video yang ramai sangat memengaruhi hasil.",
           "Jenis komentar ditentukan dengan aturan sederhana, dan nada komentar dinilai model komputer yang belum dicocokkan dengan penilaian manusia.",
           "Label alat KB sebagian besar (54,5%) berasal dari kata kunci judul video, bukan isi komentar; pengecekan ulang dilakukan pada komentar yang menyebut alat KB.",
           "Perubahan nada dari bulan ke bulan banyak dipengaruhi video mana yang sedang ramai, bukan tren masyarakat.",
           "Komentar YouTube tidak memuat lokasi, jadi tidak bisa dipetakan per kabupaten/kota."]
    for i, s in enumerate(cat, 1):
        st.markdown(f"**{i}.** {s}")
    st.caption("Penilaian nada dan pengelompokan kata dijalankan di notebook analisis; dashboard ini menampilkan hasil akhirnya.")
