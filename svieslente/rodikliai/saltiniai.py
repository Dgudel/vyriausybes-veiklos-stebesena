"""Duomenų rinkiniai, kuriuos naudoja keli rodikliai. Kiekvienas skaitomas vieną kartą."""
from functools import cache

import pandas as pd

from .bendra import i_data, metinis_pokytis, skaityk

METINIS = "palyginti su praėjusių metų atitinkamu laikotarpiu"
SEKTORIAI = {
    "Šalies ūkis be individualiųjų įmonių": "Šalies ūkis",
    "Privatusis sektorius be individualiųjų įmonių": "Privatusis sektorius",
    "Viešasis sektorius": "Viešasis sektorius",
}

# Lietuvos duomenų portalo (dataportal.gov.lt) API lentelės automatiniam atnaujinimui.
# Pavadinimą rasite rinkinio puslapyje: Eksportuoti → API endpoint → .../tables/<PAVADINIMAS>/query
DU_MODELIS = "S10R027_M3060315_4_lt"
KAINU_MODELIS = "S7R329_M2020214_1_lt"


@cache
def darbo_uzmokestis() -> pd.DataFrame:
    """S10R027: DU indeksai. Grąžina ilgą lentelę su metiniu pokyčiu, %."""
    d = skaityk("S10R027_darbo_uzmokestis.xlsx", DU_MODELIS)
    d = d[d["lyginimas"] == METINIS].copy()
    d["data"] = d["laikotarpis"].map(i_data)
    d["sektorius"] = d["sektorius"].map(SEKTORIAI).fillna(d["sektorius"])
    d["pokytis"] = d["s10r027"] - 100          # indeksas (praėję metai = 100) -> pokytis %
    return d.sort_values("data")


def du_serija(tipas: str, sektorius: str = "Šalies ūkis") -> pd.Series:
    d = darbo_uzmokestis()
    s = d[(d["tipas"] == tipas) & (d["sektorius"] == sektorius)]
    return s.set_index("data")["pokytis"]


@cache
def kainu_indeksai() -> pd.DataFrame:
    """S7R329: vartojimo kainų indeksai pagal specialiąsias grupes (lygis, 2025 = 100)."""
    k = skaityk("S7R329_kainu_indeksai.xlsx", KAINU_MODELIS)
    k["data"] = k["laikotarpis"].map(i_data)
    return k


def kainu_pokytis(grupe: str) -> pd.Series:
    k = kainu_indeksai()
    s = k[k["specialioji_prekiu_ir_paslaugu_grupe"] == grupe].set_index("data")["s7r329"]
    return metinis_pokytis(s)


def laikotarpis_is_datos(d: pd.Timestamp) -> str:
    return f"{d.year}M{d.month:02d}"


# ---------------- Būsto kainos ----------------
BUSTO_MODELIS = "S7R334_M2021001_3_lt"

TERITORIJOS = {"Lietuvos Respublika": "Lietuva", "Vilniaus m. sav.": "Vilniaus m. sav.",
               "Kita šalies teritorija": "Kita šalies teritorija"}


@cache
def busto_kainu_indeksai() -> pd.DataFrame:
    """S7R334: būsto kainų indeksai (lygis, 2025 = 100), ketvirtiniai."""
    b = skaityk("S7R334_busto_kainu_indeksai.xlsx", BUSTO_MODELIS)
    b["data"] = b["laikotarpis"].map(i_data)
    b["teritorija"] = b["teritorinis_lygmuo"].map(TERITORIJOS).fillna(b["teritorinis_lygmuo"])
    return b


def busto_kainu_pokytis(teritorija="Lietuva", tipas="Gyvenamieji pastatai, iš viso",
                        kategorija="Būstų įsigijimas") -> pd.Series:
    b = busto_kainu_indeksai()
    s = b[(b["teritorija"] == teritorija) & (b["busto_tipas"] == tipas)
          & (b["islaidu_bustui_kategorijos"] == kategorija)].set_index("data")["s7r334"].dropna()
    return metinis_pokytis(s)


def ketvirtinis(s: pd.Series) -> pd.Series:
    """Mėnesinę seriją paverčia ketvirtine (vidurkis); tik pilni ketvirčiai (3 mėn.)."""
    g = s.groupby(s.index.to_period("Q"))
    q = g.mean()[g.count() == 3]
    q.index = q.index.to_timestamp(how="start")
    return q


def ketvirtis_is_datos(d: pd.Timestamp) -> str:
    return f"{d.year}K{(d.month - 1) // 3 + 1}"
