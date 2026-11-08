"""IRD (VRM Informatikos ir ryšių departamento) nusikalstamumo rodikliai.

IRD „CSV“ nuoroda (…/item.<nr>?export=csv) iš tikrųjų grąžina HTML lentelę „Laikotarpis | Reikšmė“,
kur laikotarpis kaupiamasis nuo metų pradžios, pvz. „2026 - (01-10)“ = sausis–spalis.
"""
import html
import os
import re

import pandas as pd

from .bendra import DUOMENYS

URL = "https://www.ird.lt/lt/indicators/opendata/item.{item}?export=csv"
LAIKOTARPIS = re.compile(r"^(\d{4})\s*-\s*\((\d{2})(?:-(\d{2}))?\)$")


def html_i_lentele(tekstas: str) -> pd.DataFrame:
    """HTML lentelė → stulpeliai metai, men (kaupiamai iki mėnesio), reiksme. Tik laikotarpiai nuo sausio."""
    langeliai = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tekstas, flags=re.S | re.I)]
    eil = []
    for laik, reiksme in zip(langeliai[0::2], langeliai[1::2]):
        m = LAIKOTARPIS.match(laik.replace(" ", " "))
        v = pd.to_numeric(reiksme.replace(" ", "").replace(",", "."), errors="coerce")
        if not m or pd.isna(v) or m.group(2) != "01":
            continue
        eil.append({"metai": int(m.group(1)), "men": int(m.group(3) or m.group(2)), "reiksme": float(v)})
    if not eil:
        raise ValueError("IRD lentelėje nerasta duomenų")
    return pd.DataFrame(eil).drop_duplicates(["metai", "men"]).sort_values(["metai", "men"]).reset_index(drop=True)


def lentele(item: int, failas: str) -> pd.DataFrame:
    """Grąžina rodiklį; su ATNAUJINTI=1 pirmiau atsisiunčia iš IRD ir atnaujina duomenys/<failas>."""
    kelias = DUOMENYS / failas
    if os.environ.get("ATNAUJINTI") == "1":
        try:
            import requests
            r = requests.get(URL.format(item=item), timeout=120)
            r.raise_for_status()
            df = html_i_lentele(r.text)
            df.to_csv(kelias, index=False)
            print(f"  ↓ IRD item.{item}: {len(df)} eilučių")
            return df
        except Exception as e:
            print(f"  ⚠ IRD item.{item} neatsisiųsta ({e}); naudojamas esamas failas")
    return pd.read_csv(kelias)
