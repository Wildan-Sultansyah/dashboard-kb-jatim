"""Fungsi grafik Plotly yang dipakai lintas halaman."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sample_colorscale

from . import theme as T
from .data import muat_geojson

MARGIN = dict(l=0, r=30, t=30, b=0)


_POLI: dict | None = None


def _poligon(wilayah: str) -> tuple[list, list]:
    """Koordinat (x=bujur, y=lintang) satu wilayah; cincin dipisah None."""
    global _POLI
    if _POLI is None:
        _POLI = {}
        for f in muat_geojson()["features"]:
            g = f["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            xs, ys = [], []
            for poly in polys:
                for ring in poly:
                    xs += [c[0] for c in ring] + [None]
                    ys += [c[1] for c in ring] + [None]
            _POLI[f["properties"]["wilayah"]] = (xs, ys)
    return _POLI[wilayah]


def _bungkus(label, lebar: int = 16) -> str:
    """Label kategori panjang dilipat jadi beberapa baris supaya tidak terpotong."""
    import textwrap
    return "<br>".join(textwrap.wrap(str(label), lebar)) or str(label)


def _layout(fig: go.Figure, tinggi: int = 400) -> go.Figure:
    """Peta digambar sebagai poligon biasa (tanpa unduhan peta dasar, jadi tetap tampil saat offline)."""
    fig.update_xaxes(visible=False, range=[111.0, 114.7], fixedrange=True)
    fig.update_yaxes(visible=False, range=[-8.85, -6.6], scaleanchor="x", scaleratio=1.0, fixedrange=True)
    fig.update_layout(height=tinggi, margin=MARGIN, legend=dict(orientation="h", y=-0.02, x=0),
                      plot_bgcolor="rgba(0,0,0,0)", hovermode="closest")
    return fig


def _sorot(fig: go.Figure, wilayah: str | None) -> None:
    """Garis tebal gelap di sekeliling daerah yang dipilih."""
    if not wilayah:
        return
    xs, ys = _poligon(wilayah)
    for warna, lebar in (("white", 7), ("#0b2a5b", 3)):   # garis putih di bawah supaya tetap jelas di atas warna apa pun
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=warna, width=lebar), hoverinfo="skip", showlegend=False))


def _tambah(fig, wilayah, warna, teks, nama=None, grup=None, legenda=False):
    xs, ys = _poligon(wilayah)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", fill="toself", fillcolor=warna, line=dict(color="white", width=0.8),
                             hoveron="fills", text=teks, hoverinfo="text", name=nama or wilayah,
                             legendgroup=grup, showlegend=legenda, hoverlabel=dict(bgcolor="white", font=dict(color="#222"))))


def peta_kontinu(df: pd.DataFrame, kolom: str, judul: str, skala, zmin=None, zmax=None,
                 label: str | None = None, teks: pd.Series | None = None, tinggi: int = 400,
                 colorbar_judul: str | None = None, sorot: str | None = None) -> go.Figure:
    zmin = float(df[kolom].min()) if zmin is None else zmin
    zmax = float(df[kolom].max()) if zmax is None else zmax
    hover = teks if teks is not None else (df["nama"] + f"<br>{label or kolom}: " + df[kolom].round(2).astype(str))
    norm = ((df[kolom].clip(zmin, zmax) - zmin) / ((zmax - zmin) or 1)).fillna(0)
    warna = sample_colorscale(skala, norm.tolist())
    fig = go.Figure()
    for w, c, t in zip(df["wilayah"], warna, hover):
        _tambah(fig, w, c, t)
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", hoverinfo="skip", showlegend=False,
                             marker=dict(size=0.1, color=[zmin], colorscale=skala, cmin=zmin, cmax=zmax, showscale=True,
                                         colorbar=dict(orientation="h", thickness=10, len=0.75, x=0.5, xanchor="center", y=-0.04, yanchor="top"))))
    _sorot(fig, sorot)
    fig.update_layout(title=dict(text=judul, x=0, font=dict(size=14)))
    return _layout(fig, tinggi)


def peta_kategori(df: pd.DataFrame, kolom: str, warna: dict[str, str], judul: str,
                  teks: pd.Series | None = None, urutan: list[str] | None = None,
                  nama_legenda: dict[str, str] | None = None, tinggi: int = 400, sorot: str | None = None) -> go.Figure:
    fig = go.Figure()
    for kat in (urutan or list(warna)):
        sub = df[df[kolom] == kat]
        for i, (idx, w) in enumerate(zip(sub.index, sub["wilayah"])):
            hv = teks.loc[idx] if teks is not None else sub.loc[idx, "nama"] + f"<br>{kat}"
            _tambah(fig, w, warna[kat], hv, nama=(nama_legenda or {}).get(kat, kat), grup=kat, legenda=(i == 0))
    _sorot(fig, sorot)
    fig.update_layout(title=dict(text=judul, x=0, font=dict(size=14)))
    return _layout(fig, tinggi)


def peta_sorot(df: pd.DataFrame, wilayah: str, tinggi: int = 380) -> go.Figure:
    """Peta abu-abu dengan satu daerah disorot."""
    fig = go.Figure()
    for w, n in zip(df["wilayah"], df["nama"]):
        if w != wilayah:
            _tambah(fig, w, T.PUCAT, n)
    _tambah(fig, wilayah, T.PINK, df.loc[df["wilayah"] == wilayah, "nama"].iloc[0])
    return _layout(fig, tinggi)


def bar_horizontal(nama: pd.Series, nilai: pd.Series, warna, judul: str = "", sumbu: str = "",
                   tinggi: int | None = None, teks: pd.Series | None = None, urut: bool = True,
                   rentang=None) -> go.Figure:
    d = pd.DataFrame({"n": nama.values, "v": nilai.values})
    if teks is not None:
        d["t"] = teks.values
    if isinstance(warna, tuple):  # (skala, vmin, vmax): warna mengikuti nilai
        skala, lo, hi = warna
        d["c"] = sample_colorscale(skala, ((d["v"].clip(lo, hi) - lo) / ((hi - lo) or 1)).tolist())
    elif isinstance(warna, (pd.Series, list, np.ndarray)):
        d["c"] = list(warna)
    else:
        d["c"] = warna
    if urut:
        d = d.sort_values("v")
    fig = go.Figure(go.Bar(
        y=[_bungkus(n_) for n_ in d["n"]], x=d["v"], orientation="h", marker=dict(color=d["c"]), customdata=d["n"],
        text=d["t"] if teks is not None else None, textposition="outside", cliponaxis=False,
        hovertemplate="%{customdata}: %{x:.2f}<extra></extra>"))
    fig.update_layout(title=dict(text=judul, x=0, font=dict(size=14)), xaxis_title=sumbu,
                      yaxis_title=None, margin=dict(l=0, r=30, t=34, b=0),
                      height=tinggi or max(260, 22 * len(d) + 70), bargap=0.25)
    if not rentang:  # beri ruang agar teks di ujung batang tidak terpotong
        lo, hi = float(d["v"].min()), float(d["v"].max())
        rentang = [min(0.0, lo * 1.25), max(0.0, hi) * (1.5 if teks is not None else 1.12)]
    fig.update_xaxes(range=rentang)
    fig.update_xaxes(gridcolor="rgba(128,128,128,.18)")
    return fig


def stacked_pct(df_pct: pd.DataFrame, warna: dict[str, str], judul: str = "", tinggi: int | None = None,
                sumbu: str = "% komentar", anotasi_n: pd.Series | None = None) -> go.Figure:
    """Bar horizontal bertumpuk 100%. Kolom = kategori, indeks = baris."""
    fig = go.Figure()
    for kol in df_pct.columns:
        fig.add_trace(go.Bar(
            y=[_bungkus(n_) for n_ in df_pct.index], x=df_pct[kol], name=kol, orientation="h", customdata=list(df_pct.index),
            marker=dict(color=warna[kol], line=dict(color="rgba(255,255,255,.9)", width=1.5)),
            text=[f"{v:.0f}%" if v >= 6 else "" for v in df_pct[kol]], textposition="inside",
            insidetextanchor="middle", hovertemplate="%{customdata}<br>" + kol + ": %{x:.1f}%<extra></extra>"))
    fig.update_layout(barmode="stack", title=dict(text=judul, x=0, font=dict(size=14)),
                      xaxis=dict(title=sumbu, range=[0, 100], gridcolor="rgba(128,128,128,.18)"),
                      yaxis_title=None, margin=dict(l=0, r=30, t=34, b=0),
                      height=tinggi or max(240, 46 * len(df_pct) + 130),
                      legend=dict(orientation="h", y=-0.45 if len(df_pct) < 4 else -0.2, x=0),
                      uniformtext_minsize=9, uniformtext_mode="hide")
    if anotasi_n is not None:
        for nm, n in anotasi_n.items():
            fig.add_annotation(x=100, y=_bungkus(nm), text=f" n={n}", showarrow=False, xanchor="left",
                               font=dict(size=10, color=T.TEKS2))
        fig.update_layout(margin=dict(l=0, r=50, t=34, b=0))
    return fig


def heatmap(z: pd.DataFrame, skala, judul: str = "", zmin=None, zmax=None, fmt: str = ".1f",
            tinggi: int | None = None, colorbar_judul: str = "", zmid=None, tampil_angka: bool = True) -> go.Figure:
    import textwrap
    teks = z.map(lambda v: "" if pd.isna(v) else format(v, fmt)) if tampil_angka else None
    kolom_x = ["<br>".join(textwrap.wrap(str(c), 13)) or str(c) for c in z.columns]
    fig = go.Figure(go.Heatmap(
        z=z.values, x=kolom_x, y=list(z.index), colorscale=skala, zmin=zmin, zmax=zmax, zmid=zmid,
        text=teks.values if teks is not None else None, texttemplate="%{text}" if tampil_angka else None,
        textfont=dict(size=10), xgap=2, ygap=2, hoverongaps=False,
        colorbar=dict(title=colorbar_judul, thickness=12),
        hovertemplate="%{y} · %{x}: %{z:.2f}<extra></extra>"))
    fig.update_layout(title=dict(text=judul, x=0, y=0.99, yanchor="top", font=dict(size=14)), margin=dict(l=0, r=0, t=110, b=0),
                      height=(tinggi or max(260, 22 * len(z) + 110)) + 40)
    fig.update_yaxes(autorange="reversed", automargin=True)
    fig.update_xaxes(side="top", tickangle=0, automargin=True)
    return fig


def waffle(persen: dict[str, float], warna: dict[str, str], judul: str = "") -> go.Figure:
    """Kotak 10 x 10: 'dari 100 komentar/daerah, berapa yang ...'. Tiap kotak = 1."""
    kat = list(persen)
    hit = {k: int(persen[k]) for k in kat}
    sisa = 100 - sum(hit.values())
    for k in sorted(kat, key=lambda k: persen[k] - int(persen[k]), reverse=True)[:max(sisa, 0)]:
        hit[k] += 1
    fig = go.Figure()
    urut = [k for k in kat for _ in range(hit[k])]
    for k in kat:
        idx = [i for i, v in enumerate(urut) if v == k]
        fig.add_trace(go.Scatter(
            x=[i % 10 for i in idx], y=[9 - i // 10 for i in idx], mode="markers", name=f"{k} ({hit[k]})",
            marker=dict(symbol="square", size=26, color=warna[k], line=dict(color="white", width=1)),
            hovertemplate=f"{k}: {persen[k]:.1f}%<extra></extra>"))
    fig.update_xaxes(visible=False, range=[-.6, 9.6])
    fig.update_yaxes(visible=False, range=[-.6, 9.6], scaleanchor="x")
    fig.update_layout(title=dict(text=judul, x=0, font=dict(size=14)), height=400, margin=dict(l=0, r=0, t=34, b=0),
                      legend=dict(orientation="h", y=-0.02, x=0))
    return fig


def kotak(df: pd.DataFrame, nilai: str, kelompok: str, urutan: list[str], warna: dict[str, str],
          judul: str = "", sumbu: str = "", tinggi: int = 380) -> go.Figure:
    """Boxplot + titik tiap daerah (hover = nama daerah)."""
    fig = go.Figure()
    for g in urutan:
        s = df[df[kelompok] == g]
        fig.add_trace(go.Box(y=s[nilai], name=f"{g} (n={len(s)})", boxpoints="all", jitter=.45, pointpos=0,
                             marker=dict(color=warna[g], size=7, line=dict(color="white", width=1)),
                             line=dict(color=warna[g]), fillcolor="rgba(0,0,0,0)", text=s["nama"],
                             hovertemplate="%{text}: %{y:.2f}<extra></extra>"))
    fig.update_layout(title=dict(text=judul, x=0, font=dict(size=14)), height=tinggi, margin=dict(l=0, r=0, t=34, b=0),
                      yaxis_title=sumbu, showlegend=False)
    fig.update_yaxes(gridcolor="rgba(120,130,190,.18)")
    return fig
