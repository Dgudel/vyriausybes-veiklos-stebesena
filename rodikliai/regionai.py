"""3. Regioniniai skirtumai: Sostinės regiono ir Vidurio ir vakarų Lietuvos BVP vienam gyventojui (PGS)."""
import pandas as pd

from .bendra import Rodiklis, dalis, ivertink, papildomas_grafikas, sk, t
from .eurostat_duomenys import serija

SLENKSTIS = 0.03    # santykio punktų


def rodiklis() -> Rodiklis:
    g = lambda geo: serija("nama_10r_2gdp", geo, unit="PPS_HAB_EU27_2020")
    sost, kiti, lt = g("LT01"), g("LT02"), g("LT")
    santykis = (sost / kiti).dropna()
    pask, pries = santykis.iloc[-1], santykis.iloc[-2]
    metai, ankst = santykis.index[-1].year, santykis.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)
    SOST, KITI = t("Sostinės regionas", "Capital region"), t("Vidurio ir vakarų Lietuva", "Central and Western Lithuania")
    f1 = papildomas_grafikas(t("BVP vienam gyventojui regionuose", "GDP per capita by region"),
                             t("Pagal perkamosios galios standartą, ES vidurkis = 100", "In purchasing power standards, EU average = 100"),
                             "Šaltinis: Eurostat, nama_10r_2gdp",
                             [(SOST, sost), (KITI, kiti), ("Lietuva", lt)], dec=0)
    f2 = papildomas_grafikas(t("Regioninio atotrūkio santykis", "Regional gap ratio"),
                             t("Kiek kartų Sostinės regiono BVP vienam gyventojui didesnis nei likusios Lietuvos",
                               "How many times higher GDP per capita is in the Capital region than in the rest of Lithuania"),
                             "Šaltinis: Eurostat, nama_10r_2gdp; skaičiavimas", [(t("Santykis", "Ratio"), santykis)], dec=2,
                             nuo_nulio=False)
    lentele = pd.DataFrame({"Sostines_regionas_ES100": sost, "Vidurio_vakaru_LT_ES100": kiti, "Lietuva_ES100": lt,
                            "santykis": santykis})
    lentele.insert(0, "metai", lentele.index.year)
    kryptis = (t("nepasikeitė", "unchanged") if round(pokytis, 2) == 0 else
               (t("sumažėjo", "down") if pokytis < 0 else t("padidėjo", "up")))
    return Rodiklis(
        dalys=[dalis(t("Vidurio ir vakarų Lietuva (ES = 100)", "Central and Western Lithuania (EU = 100)"), kiti, "didesne", 1.0,
                     vienetai="", slenkscio_vnt=t(" punkto", " points"), dec=0)],
        id="regionai", pavadinimas=t("Regioniniai skirtumai", "Regional disparities"),
        trumpas_aprasas=t("Sostinės ir likusios Lietuvos BVP vienam gyv. santykis", "ratio of GDP per capita, Capital region vs rest of Lithuania"),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena, zenklas=False, dec=2, spark_nuo_nulio=False,
        vertinimo_taisykle=t(f"Gerėja, kai santykis per metus sumažėja daugiau nei {sk(SLENKSTIS, False, 2)} "
                             f"(regionai artėja); prastėja, kai tiek pat padidėja; kitu atveju – stabilu.",
                             f"Improving when the ratio falls by more than {sk(SLENKSTIS, False, 2)} in a year (regions "
                             f"converge); worsening when it rises by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. Sostinės regione BVP vienam gyventojui siekė {sk(sost.iloc[-1], False, 0)} % "
                                 f"ES vidurkio, Vidurio ir vakarų Lietuvoje – {sk(kiti.iloc[-1], False, 0)} %. Santykis – "
                                 f"{sk(pask, False, 2)} ({ankst} m. – {sk(pries, False, 2)}), t. y. {kryptis}"
                                 + (f" {sk(abs(pokytis), False, 2)}" if round(pokytis, 2) else "") + ".",
                                 f"In {metai}, GDP per capita in the Capital region was {sk(sost.iloc[-1], False, 0)}% of "
                                 f"the EU average, and {sk(kiti.iloc[-1], False, 0)}% in Central and Western Lithuania. "
                                 f"The ratio is {sk(pask, False, 2)} ({ankst}: {sk(pries, False, 2)}), i.e. {kryptis}"
                                 + (f" {sk(abs(pokytis), False, 2)}" if round(pokytis, 2) else "") + "."),
        sparkline=santykis, grafikai=[f1, f2],
        apibrezimas=t("Sostinės regiono (Vilniaus apskritis) ir Vidurio ir vakarų Lietuvos regiono (likusios 9 apskritys) "
                      "BVP vienam gyventojui pagal perkamosios galios standartą santykis. Rodo, ar ekonominė gerovė "
                      "pasiskirsto tolygiau.",
                      "Ratio of GDP per capita in purchasing power standards between the Capital region (Vilnius county) "
                      "and the Central and Western Lithuania region (the other 9 counties). Shows whether economic "
                      "prosperity is becoming more evenly distributed."),
        pastabos=[t("Regioniniai duomenys skelbiami su maždaug 1,5 metų vėlavimu.",
                    "Regional data are published with a delay of about 1.5 years."),
                  t("Dalis Vilniuje sukuriamo BVP tenka kitų apskričių gyventojams, kurie važinėja į darbą, todėl "
                    "santykis šiek tiek padidina skirtumą.",
                    "Part of the GDP generated in Vilnius is attributable to commuters from other counties, so the "
                    "ratio slightly overstates the gap.")],
        saltiniai=[("Eurostat – nama_10r_2gdp", "https://ec.europa.eu/eurostat/databrowser/view/nama_10r_2gdp/default/table?lang=en")],
        papildomai=[(f"{sk(sost.iloc[-1], False, 0)} %", t("Sostinės regionas, ES = 100", "Capital region, EU = 100")),
                    (f"{sk(kiti.iloc[-1], False, 0)} %", t("likusi Lietuva, ES = 100", "rest of Lithuania, EU = 100"))], lentele=lentele)
