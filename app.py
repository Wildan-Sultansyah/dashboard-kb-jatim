"""Titik masuk aplikasi: navigasi antar halaman."""
import base64
import pathlib

import streamlit as st

st.set_page_config(page_title="Potret KB Jawa Timur 2025", page_icon=":material/monitoring:", layout="wide")

LOGO = pathlib.Path(__file__).parent / "assets" / "logo_bkkbn.png"

# CSS sidebar: satu blok saja, tombol « tetap ada, sidebar naik sedikit.
CSS_SIDEBAR = """
<style>
[data-testid="stSidebarHeader"]{height:2.5rem;padding:0.5rem 1rem;margin-bottom:0;}
[data-testid="stSidebarUserContent"]{padding-top:0.5rem;}
</style>
"""


@st.cache_data(show_spinner=False)
def _sidebar_html() -> str:
    """Dibuat sekali lalu disimpan, jadi tidak dihitung ulang tiap pindah halaman."""
    img = ""
    if LOGO.exists():
        b64 = base64.b64encode(LOGO.read_bytes()).decode()
        img = f'<img class="brand-logo" alt="Logo" src="data:image/png;base64,{b64}">'
    return (CSS_SIDEBAR
            + f'<div class="brand">{img}<div class="brand-text"><b>Kementerian Kependudukan dan Pembangunan Keluarga/BKKBN</b>'
              '<span>Perwakilan BKKBN<br>Provinsi Jawa Timur</span></div></div>'
              '<div class="side-brand">Potret KB Jawa Timur 2025</div>'
              '<div class="side-note">Data storytelling. Pilih menu di bawah, lalu pilih, klik, dan geser untuk menjelajah.</div>')


halaman = st.navigation([
    st.Page("views/beranda.py", title="Beranda", icon=":material/home:", default=True),
    st.Page("views/profil_daerah.py", title="Profil Daerah", icon=":material/location_on:"),
    st.Page("views/capaian_kb.py", title="Capaian KB", icon=":material/bar_chart:"),
    st.Page("views/dukungan_layanan.py", title="Dukungan Layanan", icon=":material/map:"),
    st.Page("views/suara_masyarakat.py", title="Suara Masyarakat", icon=":material/forum:"),
    st.Page("views/panduan.py", title="Panduan & Istilah", icon=":material/help:"),
])
with st.sidebar:
    st.markdown(_sidebar_html(), unsafe_allow_html=True)
halaman.run()
