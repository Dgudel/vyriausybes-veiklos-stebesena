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

# Didelėms lentelėms – papildomi filtrai, kad atsisiuntimas būtų greitas
FILTRAI = {
    "migr_imm1ctz": {"age": "TOTAL", "sex": "T", "agedef": "COMPLET", "unit": "NR"},
    "migr_asyappctzm": {"age": "TOTAL", "sex": "T", "unit": "PER", "geo": ["LT"]},
    "gov_10a_exp": {"sector": "S13", "na_item": "TE", "cofog99": ["TOTAL", "GF02", "GF0201"]},
    "crim_off_cat": {"geo": ["LT"]},
    "ilc_li02": {"statinfo": "MED_EI", "sex": "T"},
    "ilc_li10": {"statinfo": "MED_EI", "sex": "T"},
    "migr_emi1ctz": {"age": "TOTAL", "sex": "T", "agedef": "COMPLET", "unit": "NR"},
    "migr_eiord": {"age": "TOTAL", "sex": "T", "unit": "PER", "geo": ["LT"]},
    "migr_eipre": {"citizen": "TOTAL", "sex": "T", "age": "TOTAL", "unit": "PER", "geo": ["LT"]},
    "migr_eirtn": {"age": "TOTAL", "sex": "T", "unit": "PER", "geo": ["LT"]},
}


def tsv_i_lentele(tekstas: str) -> pd.DataFrame:
    """Eurostat TSV (pirmas stulpelis „freq,unit,...,geo\\TIME_PERIOD“, reikšmės su žymomis „8.4 e“, „:“)
    → platus formatas: dimensijų stulpeliai + laikotarpių stulpeliai (skaičiai)."""
    import io
    d = pd.read_csv(io.StringIO(tekstas), sep="\t", dtype=str)
    pirmas = d.columns[0]
    dims = d[pirmas].str.split(",", expand=True)
    dims.columns = pirmas.split("\\")[0].split(",")
    vert = d.drop(columns=pirmas)
    vert.columns = [c.strip() for c in vert.columns]
    vert = vert.apply(lambda s: pd.to_numeric(
        s.str.strip().str.replace(r"[^0-9.\-]", "", regex=True).replace("", None), errors="coerce"))
    return pd.concat([dims, vert], axis=1)


def _atsisiusk_tsv(kodas: str) -> pd.DataFrame:
    """Tiesioginis Eurostat API (be paketo `eurostat`) – veikia ir tada, kai paketas nesusitvarko su lentele."""
    import requests
    url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{kodas}?format=TSV&compressed=false"
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    return tsv_i_lentele(r.text)


def _atsisiusk_sdmx3(kodas: str, filtrai: dict) -> pd.DataFrame:
    """SDMX 3.0 API su filtru serveryje (tik LT ir ES) – tinka ir didelėms lentelėms."""
    import io
    import requests
    url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/{kodas}/1.0/*"
    kitos = {f"c[{k}]": ",".join(v) if isinstance(v, list) else v for k, v in filtrai.items() if k != "geo"}
    for salys in (filtrai.get("geo", SALYS), ["LT"]):   # kai kuriose lentelėse ES sumos nėra (tada 400)
        r = requests.get(url, params={"c[geo]": ",".join(salys), **kitos, "format": "csvdata",
                                      "formatVersion": "2.0", "compress": "false"}, timeout=300)
        if r.status_code == 400 and salys != ["LT"]:
            continue
        r.raise_for_status()
        d = pd.read_csv(io.StringIO(r.text), dtype=str)
        tarnybiniai = {"STRUCTURE", "STRUCTURE_ID", "STRUCTURE_NAME", "TIME_PERIOD", "CONF_STATUS"}
        dims = [c for c in d.columns if c not in tarnybiniai and not c.startswith("OBS_")]
        d["OBS_VALUE"] = pd.to_numeric(d["OBS_VALUE"], errors="coerce")
        d[dims] = d[dims].fillna("")
        return d.pivot_table(index=dims, columns="TIME_PERIOD", values="OBS_VALUE", aggfunc="first").reset_index()
    raise ValueError("SDMX 3.0: nepavyko")


def _atsisiusk(kodas: str):
    df = None
    filtrai = {"geo": SALYS, **FILTRAI.get(kodas, {})}
    try:        # 1) paketas eurostat su filtrais
        import eurostat
        df = eurostat.get_data_df(kodas, filter_pars=filtrai)
    except Exception:
        pass
    if df is None or df.empty:
        try:    # 2) SDMX 3.0 su filtru serveryje
            df = _atsisiusk_sdmx3(kodas, filtrai)
        except Exception:
            df = _atsisiusk_tsv(kodas)      # 3) visa lentelė TSV formatu
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
