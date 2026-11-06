"""Eurostat lentelės: skaitomos iš duomenys/<kodas>.csv.

GitHub Actions (ATNAUJINTI=1) prieš tai atsisiunčia naujausią versiją su paketu `eurostat`
ir išsaugo tik Lietuvos ir ES-27 eilutes. Jei atsisiųsti nepavyksta, naudojamas esamas failas.
"""
import os
from functools import cache

import pandas as pd

from .bendra import DUOMENYS

SALYS = ["LT", "EU27_2020"]


def _atsisiusk(kodas: str):
    import eurostat
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
    return pd.read_csv(DUOMENYS / (failas or f"{kodas}.csv"))


def serija(kodas: str, geo: str, failas: str | None = None, **filtrai) -> pd.Series:
    """Grąžina metinę seriją (indeksas – metų pradžios datos) pagal filtrus, pvz. reason="WLIST"."""
    df = lentele(kodas, failas)
    m = df["geo"] == geo
    for k, v in filtrai.items():
        m &= df[k] == v
    eil = df[m]
    if len(eil) != 1:
        raise ValueError(f"{kodas} {geo} {filtrai}: tikėtasi 1 eilutės, rasta {len(eil)}")
    metai = [c for c in df.columns if c.isdigit()]
    s = eil[metai].iloc[0].astype(float).dropna()
    s.index = pd.to_datetime([f"{m}-01-01" for m in s.index])
    return s
