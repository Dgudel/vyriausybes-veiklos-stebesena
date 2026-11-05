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

# data.gov.lt modelių keliai automatiniam atnaujinimui. Kai rasite tikslų kelią portale
# (pvz. su duomenų agentu), įrašykite jį vietoj None – GitHub Actions ims naujausius duomenis.
DU_MODELIS = None      # pvz. "datasets/gov/lsd/statistika/darbo_uzmokestis/S10R027..."
KAINU_MODELIS = None


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
