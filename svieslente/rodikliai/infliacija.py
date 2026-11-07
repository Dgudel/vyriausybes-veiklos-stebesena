"""3.4 Infliacija (SVKI metinis pokytis).

Eurostat lentelė prc_hicp_manr atnaujinta iki 2025 m. gruodžio (2026 m. SVKI pereita prie ECOICOP 2 klasifikacijos).
Todėl naujausi duomenys imami iš ECB duomenų portalo API (tas pats SVKI): Lietuva ir euro zona.
Jei ECB nepasiekiamas – naudojami turimi failai.
"""
import os

import pandas as pd

from .bendra import DUOMENYS, Rodiklis, ivertink, sk, zmoniu_laikotarpis
from .ekonomika_bendra import grafikas
from .eurostat_duomenys import laikotarpis, serija

TIKSLAS, SLENKSTIS = 2.0, 0.5
ECB_URL = ("https://data-api.ecb.europa.eu/service/data/ICP/M.LT+U2.N.000000.4.ANR"
           "?format=csvdata&startPeriod=2015-01")
ECB_FAILAS = DUOMENYS / "ecb_svki.csv"


def _ecb() -> dict[str, pd.Series]:
    if os.environ.get("ATNAUJINTI") == "1":
        try:
            import io
            import requests
            r = requests.get(ECB_URL, timeout=60)
            r.raise_for_status()
            d = pd.read_csv(io.StringIO(r.text))[["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]]
            d.to_csv(ECB_FAILAS, index=False)
            print(f"  ↓ ECB SVKI: {len(d)} eilučių")
        except Exception as e:
            print(f"  ⚠ ECB SVKI neatsisiųsta ({e}); naudojamas esamas failas")
    if not ECB_FAILAS.exists():
        return {}
    d = pd.read_csv(ECB_FAILAS)
    rez = {}
    for sal, g in d.groupby("REF_AREA"):
        rez[sal] = pd.Series(g["OBS_VALUE"].values, index=pd.to_datetime(g["TIME_PERIOD"] + "-01")).sort_index()
    return rez


def rodiklis() -> Rodiklis:
    lt = serija("prc_hicp_manr", "LT", coicop="CP00", unit="RCH_A")
    es = serija("prc_hicp_manr", "EU27_2020", coicop="CP00", unit="RCH_A")
    lyg_vardas, saltinis = "ES-27", "Šaltinis: Eurostat, prc_hicp_manr"
    ecb = _ecb()
    if "LT" in ecb and ecb["LT"].index.max() > lt.index.max():
        lt = ecb["LT"].combine_first(lt)            # naujesni ECB duomenys papildo Eurostat seriją
        saltinis = "Šaltinis: Eurostat (prc_hicp_manr), ECB (ICP)"
        if "U2" in ecb:
            es, lyg_vardas = ecb["U2"], "Euro zona"

    pask, data = lt.iloc[-1], lt.index[-1]
    pries = lt.get(data - pd.DateOffset(years=1))
    nuokrypis_dabar, nuokrypis_pries = abs(pask - TIKSLAS), abs(pries - TIKSLAS)
    busena = ivertink(nuokrypis_dabar - nuokrypis_pries, "mazesne", SLENKSTIS)
    laik = laikotarpis(data, "M")

    g = grafikas([("Lietuva", lt), (lyg_vardas, es)], "Infliacija (SVKI)",
                 "Metinis vartojimo kainų pokytis, %; punktyras – ECB tikslas 2 %", saltinis, nuo="2015-01-01",
                 nuo_nulio=False)
    g.add_hline(y=TIKSLAS, line=dict(color="#52514e", width=1, dash="dot"))

    lentele = lt.rename("LT_SVKI_metinis_pokytis_proc").to_frame().join(es.rename(f"{lyg_vardas}_SVKI_metinis_pokytis_proc"))
    lentele = lentele[lentele.index >= "2015-01-01"]
    lentele.insert(0, "laikotarpis", [laikotarpis(d, "M") for d in lentele.index])

    return Rodiklis(
        id="infliacija", pavadinimas="Infliacija",
        trumpas_aprasas="kainų pokytis per metus (SVKI)", reiksme=pask, vienetai="%", laikotarpis=laik, busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Vertinamas atstumas nuo ECB kainų stabilumo tikslo ({sk(TIKSLAS, False)} %), palyginti su tuo pačiu "
                            f"mėnesiu prieš metus. Gerėja, kai infliacija priartėja prie tikslo daugiau nei {sk(SLENKSTIS, False)} "
                            f"proc. punkto; prastėja, kai nutolsta daugiau nei {sk(SLENKSTIS, False)} proc. punkto; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{zmoniu_laikotarpis(laik, kada=True)} metinė infliacija buvo {sk(pask, False)} % "
                                f"(prieš metus – {sk(pries, False)} %; {lyg_vardas} – {sk(es.iloc[-1], False)} %)."),
        sparkline=lt[lt.index >= "2019-01-01"], grafikai=[g],
        apibrezimas=("Suderintasis vartojimo kainų indeksas (SVKI) – metinis kainų pokytis, palyginti su tuo pačiu "
                     "praėjusių metų mėnesiu. SVKI pasirinktas, nes palyginamas su kitomis ES šalimis. "
                     "Tai ne vidutinė metinė infliacija."),
        pastabos=["Nuo 2026 m. SVKI skaičiuojamas pagal naują ECOICOP 2 klasifikaciją; Eurostat lentelė prc_hicp_manr "
                  "pasibaigė 2025 m. gruodžio duomenimis, todėl naujesni duomenys imami iš ECB.",
                  "1 srityje (energijos kainos, darbo užmokestis) naudojami VDA specialiųjų grupių indeksai."],
        saltiniai=[("Eurostat – HICP", "https://ec.europa.eu/eurostat/web/hicp/information-data"),
                   ("ECB Data Portal – HICP", "https://data.ecb.europa.eu/data/datasets/ICP")],
        papildomai=[(f"{sk(es.iloc[-1], False)} %", f"{lyg_vardas}, {zmoniu_laikotarpis(laikotarpis(es.index[-1], 'M'))}")],
        lentele=lentele,
    )
