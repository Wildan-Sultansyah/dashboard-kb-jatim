"""Uji statistik yang dihitung langsung dari data (untuk halaman interaktif).

Hasilnya sudah dicocokkan dengan keluaran notebook (lihat tests/test_data.py).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def wilcoxon_vs_nilai(x: pd.Series, pembanding: float) -> dict:
    """Apakah nilai tengah (median) daerah berbeda dari satu angka pembanding?"""
    x = x.dropna()
    r = stats.wilcoxon(x - pembanding)
    return {"statistik": float(r.statistic), "p": float(r.pvalue), "n": int(len(x)), "median": float(x.median())}


def mannwhitney(a: pd.Series, b: pd.Series) -> dict:
    a, b = a.dropna(), b.dropna()
    r = stats.mannwhitneyu(a, b, alternative="two-sided")
    return {"statistik": float(r.statistic), "p": float(r.pvalue), "n1": len(a), "n2": len(b),
            "median1": float(a.median()), "median2": float(b.median())}


def kruskal(grup: dict[str, pd.Series]) -> dict:
    g = {k: v.dropna().values for k, v in grup.items() if v.notna().sum() > 0}
    r = stats.kruskal(*g.values())
    return {"statistik": float(r.statistic), "p": float(r.pvalue), "median": {k: float(np.median(v)) for k, v in g.items()}}


def dunn(grup: dict[str, pd.Series]) -> pd.DataFrame:
    """Uji lanjut Dunn (koreksi ties) dengan koreksi Bonferroni; matriks p."""
    g = {k: v.dropna() for k, v in grup.items()}
    semua = pd.concat(g.values())
    n = len(semua)
    rank = semua.rank()
    _, cnt = np.unique(semua.values, return_counts=True)
    tie = (cnt ** 3 - cnt).sum() / (12 * (n - 1))
    rata = {k: rank.loc[v.index].mean() if False else None for k, v in g.items()}
    # peringkat per grup (indeks bisa tumpang tindih antar grup, jadi hitung dari posisi)
    pos, rata = 0, {}
    for k, v in g.items():
        rata[k] = rank.iloc[pos:pos + len(v)].mean()
        pos += len(v)
    nama = list(g)
    m = len(nama) * (len(nama) - 1) / 2
    out = pd.DataFrame(1.0, index=nama, columns=nama)
    for i, a in enumerate(nama):
        for b in nama[i + 1:]:
            se = np.sqrt((n * (n + 1) / 12 - tie) * (1 / len(g[a]) + 1 / len(g[b])))
            z = (rata[a] - rata[b]) / se
            p = min(1.0, 2 * (1 - stats.norm.cdf(abs(z))) * m)
            out.loc[a, b] = out.loc[b, a] = p
    return out


def spearman(x: pd.Series, y: pd.Series) -> dict:
    d = pd.concat([x, y], axis=1).dropna()
    r = stats.spearmanr(d.iloc[:, 0], d.iloc[:, 1])
    return {"rho": float(r.statistic), "p": float(r.pvalue), "n": int(len(d))}
