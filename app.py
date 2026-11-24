"""Titik masuk aplikasi: navigasi antar halaman."""
import base64
import pathlib

import streamlit as st

st.set_page_config(page_title="Potret KB Jawa Timur 2025", page_icon=":material/monitoring:", layout="wide")

# Logo opsional: taruh berkas logo resmi di assets/logo_bkkbn.png (PNG, sebaiknya berlatar transparan).
# Logo ditampilkan di atas kartu putih bersudut bulat di samping nama instansi. Bila berkas tidak ada, hanya teks yang tampil.
LOGO = pathlib.Path(__file__).parent / "assets" / "logo_bkkbn.png"


def _logo_b64() -> str:
    return base64.b64encode(LOGO.read_bytes()).decode() if LOGO.exists() else ""


def _brand_html() -> str:
    return ('<div class="brand"><div class="brand-text"><b>Kementerian Kependudukan dan Pembangunan Keluarga/BKKBN</b>'
            '<span>Perwakilan BKKBN<br>Provinsi Jawa Timur</span></div></div>')


def _logo_bawah_html() -> str:
    b64 = _logo_b64()
    if not b64:
        return ""
    return ('<style>.logo-bawah{display:flex;justify-content:center;margin:2.5rem 0 1rem 0;}'
            '.logo-bawah img{width:75%;max-width:260px;height:auto;}</style>'
            f'<div class="logo-bawah"><img alt="Logo BKKBN" src="data:image/png;base64,{b64}"></div>')

halaman = st.navigation([
    st.Page("views/beranda.py", title="Beranda", icon=":material/home:", default=True),
    st.Page("views/profil_daerah.py", title="Profil Daerah", icon=":material/location_on:"),
    st.Page("views/capaian_kb.py", title="Capaian KB", icon=":material/bar_chart:"),
    st.Page("views/dukungan_layanan.py", title="Dukungan Layanan", icon=":material/map:"),
    st.Page("views/suara_masyarakat.py", title="Suara Masyarakat", icon=":material/forum:"),
    st.Page("views/panduan.py", title="Panduan & Istilah", icon=":material/help:"),
])
with st.sidebar:
    st.markdown(_brand_html(), unsafe_allow_html=True)
    st.markdown('<div class="side-brand">Potret KB Jawa Timur 2025</div>'
                '<div class="side-note">Data storytelling. Pilih menu di bawah, lalu pilih, klik, dan geser untuk menjelajah.</div>', unsafe_allow_html=True)
    st.markdown(_logo_bawah_html(), unsafe_allow_html=True)
halaman.run()
