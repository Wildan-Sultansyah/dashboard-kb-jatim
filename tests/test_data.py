"""Pengujian integritas data dan konsistensi dengan hasil notebook."""
import json
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATA = ROOT / "data"

from kbdash.data import hitung_woa  # noqa: E402


@pytest.fixture(scope="module")
def p1():
    return pd.read_csv(DATA / "p1_wilayah.csv")


@pytest.fixture(scope="module")
def p2():
    return pd.read_csv(DATA / "p2_wilayah.csv")


def test_38_daerah_unik(p1, p2):
    assert len(p1) == 38 and p1["wilayah"].is_unique
    assert set(p1["wilayah"]) == set(p2["wilayah"])


def test_geojson_cocok_dengan_data(p1):
    g = json.loads((DATA / "jatim_kabkota.geojson").read_text(encoding="utf-8"))
    assert {f["properties"]["wilayah"] for f in g["features"]} == set(p1["wilayah"])


def test_indeks_dihitung_ulang_sama_dengan_notebook(p1):
    arah = {"CPR": 1, "MKJP": 1, "UnmetNeed": -1, "DCR": -1, "TFR": -1}
    z = pd.DataFrame({c: (p1[c] - p1[c].mean()) / p1[c].std(ddof=1) * s for c, s in arah.items()})
    indeks = z.mean(axis=1, skipna=True)
    assert np.allclose(indeks, p1["indeks"], atol=1e-3)
    # peringkat identik dengan notebook (1 = indeks tertinggi)
    assert (indeks.rank(ascending=False, method="min").astype(int) == p1["peringkat"]).all()


def test_jumlah_klaster_dan_kategori(p1):
    assert p1["klaster"].value_counts().to_dict() == {"K1": 18, "K2": 12, "K3": 8}
    assert p1["kategori"].value_counts().to_dict() == {"Rendah": 13, "Tinggi": 13, "Sedang": 12}


def test_kruskal_kawasan_sama_dengan_notebook(p1):
    grup = [g["indeks"].values for _, g in p1.groupby("kawasan")]
    h = stats.kruskal(*grup)
    assert h.statistic == pytest.approx(10.916, abs=0.02)
    assert h.pvalue == pytest.approx(0.0122, abs=0.001)


def test_tipologi_dan_stok(p2):
    assert p2["tipologi"].str[0].value_counts().to_dict() == {"A": 10, "D": 10, "B": 9, "C": 9}
    assert int(p2["menetap"].sum()) == 8 and int(p2["tangguh"].sum()) == 8
    assert p2["stok_kritis_nov"].between(0, 8).all()


def test_woa_bawaan_identik_notebook(p2):
    bobot = {"capaian_rendah": .4, "layanan_rendah": .15, "pkb_rendah": .15, "stok_kritis": .3}
    res = hitung_woa(p2, bobot)
    assert (res["peringkat"] == p2["rank_prioritas"]).all()
    assert np.allclose(res["skor"], p2["skor_prioritas"], atol=0.01)


def test_woa_bobot_dinormalkan(p2):
    a = hitung_woa(p2, {"capaian_rendah": 4, "layanan_rendah": 1.5, "pkb_rendah": 1.5, "stok_kritis": 3})
    b = hitung_woa(p2, {"capaian_rendah": .4, "layanan_rendah": .15, "pkb_rendah": .15, "stok_kritis": .3})
    assert np.allclose(a["skor"], b["skor"])


def test_p3_konsisten():
    h = json.loads((DATA / "p3_hasil.json").read_text(encoding="utf-8"))
    assert sum(h["alokon_n"].values()) == h["ringkas"]["komentar"] == 2785
    assert sum(h["sentimen_bert"].values()) == 2785
    assert sum(t["n"] for t in h["topik"]) + h["topik_tak_terkelompok"] == 2785
    assert sum(h["jenis_n"].values()) == 2785


def test_uji_langsung_sama_dengan_notebook(p1):
    import json
    from kbdash import stats as S
    H = json.load(open(ROOT / "data" / "p1_hasil.json"))
    for nama, kol, acuan, p in [("CPR", "CPR", 69.6, 0.572), ("MKJP", "MKJP", 25.4, 0.446), ("DCR", "DCR", 18.7, 0.001)]:
        assert abs(S.wilcoxon_vs_nilai(p1[kol], acuan)["p"] - p) < 0.002
    assert abs(S.mannwhitney(p1[p1.tipe == "Kota"]["MKJP"], p1[p1.tipe == "Kabupaten"]["MKJP"])["p"] - 0.002) < 0.001
    g = {k: v["indeks"].reset_index(drop=True) for k, v in p1.groupby("kawasan")}
    assert abs(S.kruskal(g)["statistik"] - 10.916) < 0.01
    dn = S.dunn(g)
    for a in H["kruskal_kawasan"]["dunn"]:
        for b, v in H["kruskal_kawasan"]["dunn"][a].items():
            assert abs(dn.loc[a, b] - v) < 0.001
    assert abs(S.spearman(p1["MKJP"], p1["iBangga"])["rho"] - 0.625) < 0.002


def test_tanpa_keterbatasan_rls_2024():
    import json
    H = json.load(open(ROOT / "data" / "p1_hasil.json"))
    assert not any("2024" in s for s in H["keterbatasan"])
