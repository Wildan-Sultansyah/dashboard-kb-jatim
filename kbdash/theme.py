"""Palet, CSS, dan komponen tampilan bersama."""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

# ---- Palet (lolos validator warna: jarak antar warna aman untuk buta warna)
BIRU, EMAS, PINK, UNGU = "#1c7ed6", "#e6a400", "#d6336c", "#7048e8"
HIJAU = "#0ca678"
PUCAT = "#dbe4ff"          # latar peta/ sel "tidak signifikan" (biru muda, bukan abu-abu)
TEKS2 = "#4a5170"
INDIGO = "#1864ab"

# Makna konsisten di seluruh dashboard: biru = baik, emas = sedang, pink-merah = perlu perhatian
WARNA_KATEGORI = {"Tinggi": BIRU, "Sedang": EMAS, "Rendah": PINK}
WARNA_SENTIMEN = {"negatif": PINK, "netral": EMAS, "positif": BIRU}
WARNA_KLASTER = {"K1": BIRU, "K2": EMAS, "K3": PINK}
NAMA_KLASTER = {"K1": "K1 · Pemakaian KB kuat", "K2": "K2 · Unggul di KB jangka panjang", "K3": "K3 · Perlu perhatian khusus"}
WARNA_TIPOLOGI = {"A": PINK, "B": UNGU, "C": EMAS, "D": BIRU}
NAMA_TIPOLOGI = {
    "A": "A · Capaian rendah, dukungan rendah",
    "B": "B · Capaian rendah, dukungan cukup",
    "C": "C · Capaian tinggi, dukungan rendah (perlu dijaga)",
    "D": "D · Capaian tinggi, dukungan cukup",
}
WARNA_KAWASAN = {"Mataraman": BIRU, "Arek": HIJAU, "Tapal Kuda": EMAS, "Madura": PINK}
WARNA_POLA = {"Kelompok kuat": BIRU, "Kelompok lemah": PINK, "Daerah yang berbeda dari tetangga": UNGU, "Tidak ada pola": PUCAT}

# ---- Skala warna
SKALA_BIRU = ["#e7f1fd", "#a5cdf5", "#5ba3e6", "#1c7ed6", "#14589a", "#0b3560"]
SKALA_PINK = ["#fff0f5", "#f9bfd3", "#ec7ea4", "#d6336c", "#9c1f4c", "#5c0f2d"]
SKALA_EMAS = ["#fff8e1", "#ffe08a", "#f6c445", "#e6a400", "#a87500", "#5e4200"]
SKALA_DIVERGING = [[0, PINK], [0.5, "#ffe9a8"], [1, BIRU]]   # merah muda -> krem -> biru

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root {--navy: #0b2a5b; --royal: #1c7ed6; --deep: #1864ab; --sky: #74c0fc; --mist: #e7f1fd; --ice: #f4f8fd; --line: #d7e6f8;}
html, body, [class*="css"], .stMarkdown, button, input {font-family: 'Plus Jakarta Sans', 'Source Sans', sans-serif;}
.stApp {background: radial-gradient(900px 420px at 85% -80px, #dcecff 0%, rgba(220,236,255,0) 70%), var(--ice);}
.block-container {padding-top: 1.6rem; max-width: 1240px;}
h1, h2, h3 {font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.015em; color: var(--navy);}
h1 {font-size: 2rem !important; font-weight: 800 !important;}
h2 {font-size: 1.45rem !important; font-weight: 800 !important;}
h3 {font-size: 1.12rem !important; font-weight: 700 !important;}
/* Sidebar */
section[data-testid="stSidebar"] {background: linear-gradient(190deg, #0b2a5b 0%, #123f80 55%, #1864ab 100%);}
section[data-testid="stSidebar"] * {color: #eaf3ff !important;}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {border-radius: 999px; margin: 3px 0; padding: 4px 8px;}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] {background: #fff; font-weight: 800;}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] * {color: #0b2a5b !important;}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {background: rgba(255,255,255,.14);}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {display: flex; flex-direction: column;}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {order: -3;}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {order: -2; padding-bottom: 14px;}
.brand {display: flex; align-items: center; gap: 12px; padding: 4px 2px 10px; border-bottom: 1px solid rgba(255,255,255,.22); margin-bottom: 8px;}
.brand-logo {width: 58px; height: 58px; object-fit: contain; flex: 0 0 auto;}.brand-text {display: flex; flex-direction: column; line-height: 1.25; color: #fff;}
.brand-text b {font-size: .8rem; font-weight: 800; color: #fff !important;}
.brand-text span {font-size: .72rem; font-weight: 600; color: #fff !important; margin-top: 3px; opacity: .95;}
.side-brand {font-weight: 800; font-size: 1.12rem; line-height: 1.25; padding: .5rem .3rem .2rem; letter-spacing: -.01em;}
.side-note {font-size: .76rem; opacity: .85; padding: .2rem .3rem;}
/* Hero & judul halaman */
.hero {position: relative; overflow: hidden; background: linear-gradient(125deg, #0b2a5b 0%, #1864ab 55%, #1c7ed6 100%); color: #fff; border-radius: 26px;
       padding: 34px 38px; margin-bottom: 20px; box-shadow: 0 18px 40px rgba(11, 42, 91, .25);}
.hero::before {content: ""; position: absolute; right: -70px; top: -90px; width: 340px; height: 340px; border-radius: 50%;
       background: radial-gradient(circle at 35% 35%, rgba(255,255,255,.30), rgba(255,255,255,0) 68%);}
.hero::after {content: ""; position: absolute; right: 120px; bottom: -120px; width: 260px; height: 260px; border-radius: 50%;
       background: radial-gradient(circle at 40% 40%, rgba(116,192,252,.35), rgba(116,192,252,0) 70%);}
.hero > * {position: relative; z-index: 1;}
.hero h1 {color: #fff !important; margin: 0 0 8px 0; font-size: 2.4rem !important; line-height: 1.1;}
.hero p {color: rgba(255,255,255,.92); font-size: 1.05rem; margin: 0; max-width: 760px; line-height: 1.55;}
.hero .kick {display: inline-block; font-size: .74rem; letter-spacing: .1em; text-transform: uppercase; font-weight: 700; margin-bottom: 12px;
       background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.28); border-radius: 999px; padding: 4px 13px;}
.pagehead {position: relative; overflow: hidden; background: linear-gradient(125deg, #0b2a5b 0%, #1864ab 60%, #1c7ed6 100%); color: #fff; border-radius: 22px;
           padding: 22px 28px; margin-bottom: 16px; box-shadow: 0 12px 28px rgba(11, 42, 91, .20);}
.pagehead::before {content: ""; position: absolute; right: -50px; top: -70px; width: 240px; height: 240px; border-radius: 50%;
           background: radial-gradient(circle at 35% 35%, rgba(255,255,255,.26), rgba(255,255,255,0) 68%);}
.pagehead > * {position: relative; z-index: 1;}
.pagehead h1 {color: #fff !important; margin: 0 0 4px 0; font-size: 1.75rem !important;}
.pagehead p {color: rgba(255,255,255,.93); margin: 0; font-size: .98rem; max-width: 820px; line-height: 1.5;}
.pagehead .kick {font-size: .74rem; letter-spacing: .1em; text-transform: uppercase; font-weight: 700; opacity: .9; margin-bottom: 4px;}
/* Kartu angka */
.kpi {min-height: 128px; background: #fff; border-radius: 20px; padding: 16px 18px; border: 1px solid var(--line); border-top: 5px solid var(--royal);
      box-shadow: 0 8px 22px rgba(11, 42, 91, .07); height: 100%;}
.kpi .v {font-size: 1.9rem; font-weight: 800; color: var(--navy); line-height: 1.1; margin-top: 2px;}
.kpi .l {font-size: .74rem; font-weight: 800; color: var(--deep); text-transform: uppercase; letter-spacing: .06em;}
.kpi .n {font-size: .8rem; color: #50658a; margin-top: 4px;}
/* Kotak penjelasan (semua satu keluarga biru) */
.callout {border-radius: 16px; padding: 13px 18px; margin: 8px 0 14px 0; font-size: .96rem; line-height: 1.55;}
.callout b.t {display: block; font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; margin-bottom: 3px;}
.c-intinya {background: linear-gradient(120deg, #e7f1fd, #f4f9ff); border-left: 6px solid var(--royal); color: #0b2a5b;} .c-intinya b.t {color: var(--deep);}
.c-baca {background: #fff; border: 1.5px dashed #8bbcf0; color: #123f80;} .c-baca b.t {color: var(--deep);}
.c-awas {background: #0b2a5b; color: #eaf3ff;} .c-awas b.t {color: var(--sky);}
.headline {font-size: 1.4rem; font-weight: 800; line-height: 1.3; margin: .1rem 0 .7rem 0; color: var(--navy);}
.kicker {display: inline-block; font-size: .7rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase;
         color: #fff; background: linear-gradient(120deg, #1864ab, #1c7ed6); border-radius: 999px; padding: 4px 13px; margin-bottom: 8px;}
.note {font-size: .84rem; color: #50658a;}
.chip {display:inline-block; padding:3px 12px; border-radius:999px; font-size:.8rem; font-weight:700; color:#fff; margin: 0 6px 4px 0;}
.verdict {border-radius: 18px; padding: 15px 20px; font-size: 1.08rem; font-weight: 800; margin: 8px 0 10px 0;}
.verdict.ya {background: linear-gradient(120deg, #0b2a5b, #1864ab); color: #fff; box-shadow: 0 10px 24px rgba(11,42,91,.18);}
.verdict.tidak {background: #fff; color: var(--navy); border: 2px solid var(--royal);}
.verdict small {display:block; font-weight: 500; font-size: .86rem; opacity: .92; margin-top: 3px;}
/* Komponen Streamlit */
.ctitle {font-weight: 800; font-size: .98rem; color: var(--navy); margin: 12px 4px 5px; line-height: 1.3;}
div[data-testid="stPlotlyChart"] {overflow-x: auto; overflow-y: hidden; background: #fff; border-radius: 20px; padding: 8px 10px; border: 1px solid var(--line);
      box-shadow: 0 8px 22px rgba(11, 42, 91, .06);}
div[data-testid="stMetric"] {background: #fff; border-radius: 16px; padding: 12px 16px; border: 1px solid var(--line);}
div[data-testid="stDataFrame"] {border-radius: 16px; overflow: hidden; border: 1px solid var(--line); box-shadow: 0 8px 22px rgba(11, 42, 91, .06);}
div[data-testid="stExpander"] {background: #fff; border-radius: 16px; border: 1px solid var(--line);}
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 18px;}
div[data-baseweb="select"] > div {border-radius: 12px; border-color: var(--line); background: #fff;}
hr {border-color: var(--line) !important;}
/* Tab bentuk pil, bisa digeser kiri-kanan */
[role="tablist"] {flex-wrap: nowrap !important; overflow-x: auto !important; overflow-y: hidden; scrollbar-width: thin; gap: 6px; padding: 6px;
  background: #fff; border: 1px solid var(--line); border-radius: 999px; -webkit-overflow-scrolling: touch; margin-bottom: 10px;}
[role="tablist"] [role="tab"] {flex: 0 0 auto; white-space: nowrap; border-radius: 999px !important; padding: 8px 16px !important; height: auto !important;
  font-weight: 700; font-size: .92rem; color: var(--deep) !important; background: transparent !important; border: 0 !important;}
[role="tablist"] [role="tab"]:hover {background: var(--mist) !important;}
[role="tablist"] [role="tab"][aria-selected="true"] {background: linear-gradient(120deg, #1864ab, #1c7ed6) !important; color: #fff !important;}
[role="tablist"] [role="tab"][aria-selected="true"] p, [role="tablist"] [role="tab"][aria-selected="true"] * {color: #fff !important;}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {display: none !important;}
[role="tablist"]::-webkit-scrollbar {height: 6px;}
[role="tablist"]::-webkit-scrollbar-thumb {background: #a5cdf5; border-radius: 6px;}
</style>
"""


_RESIZE_JS = """<script>
const w = window.parent;
const fire = () => w.dispatchEvent(new Event('resize'));
[200, 800, 2000, 4000].forEach(t => setTimeout(fire, t));
w.document.addEventListener('click', () => { setTimeout(fire, 150); setTimeout(fire, 700); }, true);
</script>"""


def rapikan(fig) -> None:
    """Satu tempat untuk mencegah label terpotong: margin kanan/bawah lebar, margin otomatis, font seragam."""
    m = fig.layout.margin
    t_atas = m.t if m.t is not None else 34
    fig.update_layout(
        margin=dict(l=max(m.l if m.l is not None else 0, 6), r=max(m.r if m.r is not None else 0, 72),
                    t=t_atas, b=max(m.b if m.b is not None else 0, 56)),
        font=dict(family="Plus Jakarta Sans, Source Sans, sans-serif", color="#0b2a5b"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)


def _pasang_plotly() -> None:
    """Semua st.plotly_chart (termasuk lewat kolom) otomatis dirapikan; toolbar Plotly disembunyikan."""
    from streamlit.delta_generator import DeltaGenerator
    if getattr(DeltaGenerator.plotly_chart, "_kb", False):
        return
    asli = DeltaGenerator.plotly_chart

    def plotly_chart(self, figure_or_data, *a, **kw):
        if hasattr(figure_or_data, "update_layout"):
            # judul grafik dipindah ke HTML di atas grafik supaya otomatis turun baris dan tidak pernah terpotong
            judul = figure_or_data.layout.title.text if figure_or_data.layout.title else None
            if judul:
                self.markdown(f'<div class="ctitle">{judul.replace("<br>", " ")}</div>', unsafe_allow_html=True)
                m = figure_or_data.layout.margin
                figure_or_data.update_layout(title_text=None, margin=dict(
                    l=m.l if m.l is not None else 0, r=m.r if m.r is not None else 0,
                    t=max((m.t if m.t is not None else 34) - 24, 14), b=m.b if m.b is not None else 0))
            rapikan(figure_or_data)
        kw.setdefault("config", {"displayModeBar": False})
        return asli(self, figure_or_data, *a, **kw)

    plotly_chart._kb = True
    DeltaGenerator.plotly_chart = plotly_chart
    st.plotly_chart = lambda *a, **kw: plotly_chart(st._main, *a, **kw)


def pasang_css() -> None:
    _pasang_plotly()
    st.markdown(CSS, unsafe_allow_html=True)
    # Memaksa Plotly menghitung ulang lebar setelah tab/halaman tampil (mencegah grafik terpotong di kanan)
    try:
        if hasattr(st, "iframe"):
            st.iframe(_RESIZE_JS, height=1)
        else:
            components.html(_RESIZE_JS, height=0)
    except Exception:  # fitur pelengkap saja; jangan sampai menggagalkan halaman
        pass


def pasang_halaman(judul: str, kicker: str | None = None, ringkas: str | None = None,
                   warna: tuple[str, str] = ("#1c7ed6", "#4263eb")) -> None:
    pasang_css()
    k = f'<div class="kick">{kicker}</div>' if kicker else ""
    p = f"<p>{ringkas}</p>" if ringkas else ""
    st.markdown(f'<div class="pagehead" style="--a:{warna[0]};--b:{warna[1]}">{k}<h1>{judul}</h1>{p}</div>', unsafe_allow_html=True)


def hero(judul: str, ringkas: str, kicker: str = "") -> None:
    pasang_css()
    st.markdown(f'<div class="hero"><div class="kick">{kicker}</div><h1>{judul}</h1><p>{ringkas}</p></div>', unsafe_allow_html=True)


def kpi(label: str, nilai: str, catatan: str = "", warna: str = BIRU) -> str:
    return (f'<div class="kpi" style="--c:{warna}"><div class="l">{label}</div><div class="v">{nilai}</div>'
            f'<div class="n">{catatan}</div></div>')


def kpi_baris(items: list[tuple]) -> None:
    kolom = st.columns(len(items))
    for k, it in zip(kolom, items):
        k.markdown(kpi(*it), unsafe_allow_html=True)


def intinya(teks: str, judul: str = "Intinya") -> None:
    st.markdown(f'<div class="callout c-intinya"><b class="t">{judul}</b>{teks}</div>', unsafe_allow_html=True)


def cara_baca(teks: str, judul: str = "Cara membaca") -> None:
    st.markdown(f'<div class="callout c-baca"><b class="t">{judul}</b>{teks}</div>', unsafe_allow_html=True)


def awas(teks: str, judul: str = "Perlu diingat") -> None:
    st.markdown(f'<div class="callout c-awas"><b class="t">{judul}</b>{teks}</div>', unsafe_allow_html=True)


def headline(teks: str, kicker: str | None = None, warna: str = BIRU) -> None:
    if kicker:
        st.markdown(f'<div class="kicker" style="--c:{warna}">{kicker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="headline">{teks}</div>', unsafe_allow_html=True)


def chip(teks: str, warna: str) -> str:
    ink = "#3d2c00" if warna == EMAS else "#fff"
    return f'<span class="chip" style="background:{warna};color:{ink}">{teks}</span>'


def verdict(nyata: bool, kalimat_ya: str, kalimat_tidak: str, detail: str = "") -> None:
    kal = kalimat_ya if nyata else kalimat_tidak
    st.markdown(f'<div class="verdict {"ya" if nyata else "tidak"}">{kal}<small>{detail}</small></div>', unsafe_allow_html=True)


def catatan(teks: str) -> None:
    st.markdown(f'<div class="note">{teks}</div>', unsafe_allow_html=True)


def fmt(x: float, d: int = 2) -> str:
    """Angka gaya Indonesia (koma desimal)."""
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
