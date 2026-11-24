"""Pemuatan data. Semua file ada di folder data/ (CSV, JSON, GeoJSON)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ASSETS = ROOT / "assets"

INDIKATOR = ["CPR", "MKJP", "UnmetNeed", "DCR", "TFR"]
LABEL = {"CPR": "CPR modern", "MKJP": "MKJP", "UnmetNeed": "Unmet need",
         "DCR": "DCR (putus pakai)", "TFR": "TFR"}
NAIK_BAIK = {"CPR": True, "MKJP": True, "UnmetNeed": False, "DCR": False, "TFR": False}
KAWASAN_URUT = ["Mataraman", "Arek", "Tapal Kuda", "Madura"]


def judul_nama(w: str) -> str:
    """'KAB. BANGKALAN' -> 'Kab. Bangkalan'."""
    return str(w).title()


@st.cache_data
def muat_geojson() -> dict:
    return json.loads((DATA / "jatim_kabkota.geojson").read_text(encoding="utf-8"))


@st.cache_data
def muat_json(nama: str) -> dict:
    return json.loads((DATA / nama).read_text(encoding="utf-8"))


@st.cache_data
def muat_p1() -> pd.DataFrame:
    df = pd.read_csv(DATA / "p1_wilayah.csv")
    df["nama"] = df["wilayah"].map(judul_nama)
    return df


@st.cache_data
def muat_p2() -> pd.DataFrame:
    df = pd.read_csv(DATA / "p2_wilayah.csv")
    df["alokon_kosong_nov"] = df["alokon_kosong_nov"].fillna("")
    df["tip"] = df["tipologi"].str[0]
    return df


@st.cache_data
def muat_gabungan() -> pd.DataFrame:
    """Satu tabel per kab/kota: hasil Proyek 1 + Proyek 2."""
    a = muat_p1()
    b = muat_p2()
    return a.merge(b, on="wilayah", how="left")


def prioritas_per_indikator(df: pd.DataFrame) -> pd.Series:
    """Jumlah daerah menurut indikator di 'Prioritas 1' (teks diawali nama indikator)."""
    s = df["prioritas1"].str.split(":").str[0]
    return s[s != "-"].value_counts()


def hitung_woa(df: pd.DataFrame, bobot: dict[str, float]) -> pd.DataFrame:
    """Skor prioritas WOA (Proyek 2): layer dinormalkan min-max, lalu dijumlah berbobot.

    Dengan bobot bawaan (0,40/0,15/0,15/0,30) hasilnya identik dengan notebook.
    """
    def mm(s):
        return (s - s.min()) / (s.max() - s.min())

    layer = pd.DataFrame({
        "capaian_rendah": 1 - mm(df["capaian"]),
        "layanan_rendah": 1 - mm(df["layanan_per10k"]),
        "pkb_rendah": 1 - mm(df["pkb_per10k"]),
        "stok_kritis": mm(df["stok_kritis_nov"]),
    }, index=df.index)
    total = sum(bobot.values()) or 1.0
    kontribusi = pd.DataFrame({k: layer[k] * bobot[k] / total for k in layer.columns})
    out = kontribusi.copy()
    out["skor"] = kontribusi.sum(axis=1)
    out["peringkat"] = out["skor"].rank(ascending=False, method="min").astype(int)
    return out
