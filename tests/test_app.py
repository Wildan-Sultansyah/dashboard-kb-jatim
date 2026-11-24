"""Menjalankan tiap halaman Streamlit dan beberapa interaksi, memastikan tidak ada galat."""
import pathlib

import pytest
from streamlit.testing.v1 import AppTest

from kbdash.teks import UJI

ROOT = pathlib.Path(__file__).resolve().parents[1]
HALAMAN = ["beranda", "profil_daerah", "capaian_kb", "dukungan_layanan", "suara_masyarakat", "panduan"]


def buka(nama):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120).run()
    if nama != "beranda":
        at.switch_page(f"views/{nama}.py").run()
    assert not at.exception, [e.value for e in at.exception]
    return at


@pytest.mark.parametrize("nama", HALAMAN)
def test_halaman_tanpa_galat(nama):
    buka(nama)


def test_semua_uji_statistik_bisa_dipilih():
    at = buka("capaian_kb")
    for kunci in UJI:
        at.selectbox(key="uji_pil").select(kunci).run()
        assert not at.exception, (kunci, [e.value for e in at.exception])


def test_peta_capaian_semua_lapisan():
    at = buka("capaian_kb")
    for opsi in at.selectbox(key="ck_lapisan").options:
        at.selectbox(key="ck_lapisan").select(opsi).run()
        assert not at.exception, (opsi, [e.value for e in at.exception])
    at.selectbox(key="ck_sorot").select("Kab. Bangkalan").run()
    assert not at.exception


def test_coba_sendiri_bobot_nol():
    at = buka("capaian_kb")
    for c in ["CPR", "MKJP", "UnmetNeed", "DCR"]:
        at.slider(key=f"w_{c}").set_value(0).run()
    assert not at.exception


def test_dukungan_layanan_interaksi():
    at = buka("dukungan_layanan")
    for opsi in at.selectbox(key="dk_lap").options:
        at.selectbox(key="dk_lap").select(opsi).run()
        assert not at.exception, (opsi, [e.value for e in at.exception])
    at.slider(key="wo_a").set_value(0.9).run()
    assert not at.exception


def test_suara_masyarakat_interaksi():
    at = buka("suara_masyarakat")
    for opsi in at.selectbox(key="sm_alokon").options:
        at.selectbox(key="sm_alokon").select(opsi).run()
        assert not at.exception, (opsi, [e.value for e in at.exception])
    at.radio(key="sm_mode").set_value("Hanya yang jelas menyebut alat KB di teksnya").run()
    assert not at.exception


def test_sidebar_tanpa_kata_proyek():
    at = buka("beranda")
    teks = " ".join(m.value for m in at.sidebar.markdown)
    assert "Proyek" not in teks
