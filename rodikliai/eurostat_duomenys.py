"""Eurostat lentelės: skaitomos iš duomenys/<kodas>.csv.

GitHub Actions (ATNAUJINTI=1) prieš tai atsisiunčia naujausią versiją su paketu `eurostat`
ir išsaugo tik Lietuvos ir ES-27 eilutes. Jei atsisiųsti nepavyksta, naudojamas esamas failas.
"""
import os
import re
from functools import cache

import pandas as pd

from .bendra import DUOMENYS

SALYS = ["LT", "EU27_2020"]


def _atsisiusk(kodas: str):
    import eurostat
    try:    # tik Lietuva ir ES – dideli rinkiniai (pvz. namq_10_gdp) siunčiami greitai
        df = eurostat.get_data_df(kodas, filter_pars={"geo": SALYS})
    except Exception:
        df = eurostat.get_data_df(kodas)
    geo_col = next(c for c in df.columns if c.startswith("geo"))
    df = df[df[geo_col].isin(SALYS)].rename(columns={geo_col: "geo"})
    q_col = next((c for c in df.columns if c.startswith("quant")), None)
    if q_col and q_col != "quantile":
        df = df.rename(columns={q_col: "quantile"})
    df.to_csv(DUOMENYS / f"{kodas}.csv", index=False)
    print(f"  ↓ Eurostat {kodas}: {len(df)} eilučių")


@cache
def lentele(kodas: str, failas: str | None = None) -> pd.DataFrame:
    if os.environ.get("ATNAUJINTI") == "1":
        try:
            _atsisiusk(kodas)
            failas = f"{kodas}.csv"
        except Exception as e:                       # tinklo klaida – naudojame turimą failą
            print(f"  ⚠ Eurostat {kodas} neatsisiųsta ({e}); naudojamas esamas failas")
    return pd.read_csv(DUOMENYS / (failas or f"{kodas}.csv"), low_memory=False)


PERIODAS = re.compile(r"^(\d{4})(?:-(\d{2})|-Q(\d))?$")


def _data(p: str) -> pd.Timestamp:
    m = PERIODAS.match(p)
    metai, men, ketv = m.group(1), m.group(2), m.group(3)
    if men:
        return pd.Timestamp(int(metai), int(men), 1)
    if ketv:
        return pd.Timestamp(int(metai), 3 * int(ketv) - 2, 1)
    return pd.Timestamp(int(metai), 1, 1)


def serija(kodas: str, geo: str, failas: str | None = None, **filtrai) -> pd.Series:
    """Grąžina seriją (indeksas – laikotarpio pradžios data) pagal filtrus, pvz. reason="WLIST".
    Tinka metiniams (2024), ketvirtiniams (2024-Q3) ir mėnesiniams (2024-09) duomenims."""
    df = lentele(kodas, failas)
    m = df["geo"] == geo
    for k, v in filtrai.items():
        m &= df[k] == v
    eil = df[m]
    if len(eil) != 1:
        raise ValueError(f"{kodas} {geo} {filtrai}: tikėtasi 1 eilutės, rasta {len(eil)}")
    periodai = [c for c in df.columns if PERIODAS.match(str(c))]
    s = pd.to_numeric(eil[periodai].iloc[0], errors="coerce").dropna()
    s.index = [_data(p) for p in s.index]
    return s


def laikotarpis(d: pd.Timestamp, daznis: str) -> str:
    """Data -> OSP stiliaus laikotarpis: M – 2026M09, Q – 2026K3, A – 2026."""
    if daznis == "M":
        return f"{d.year}M{d.month:02d}"
    if daznis == "Q":
        return f"{d.year}K{(d.month - 1) // 3 + 1}"
    return str(d.year)
