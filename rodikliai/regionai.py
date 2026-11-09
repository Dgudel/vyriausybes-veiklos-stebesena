"""3. Regioniniai skirtumai: Sostinės regiono ir Vidurio ir vakarų Lietuvos BVP vienam gyventojui (PGS)."""
import pandas as pd

from .bendra import Rodiklis, dalis, ivertink, papildomas_grafikas, sk
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
    f1 = papildomas_grafikas("BVP vienam gyventojui regionuose",
                             "Pagal perkamosios galios standartą, ES vidurkis = 100",
                             "Šaltinis: Eurostat, nama_10r_2gdp",
                             [("Sostinės regionas", sost), ("Vidurio ir vakarų Lietuva", kiti), ("Lietuva", lt)], dec=0)
    f2 = papildomas_grafikas("Regioninio atotrūkio santykis",
                             "Kiek kartų Sostinės regiono BVP vienam gyventojui didesnis nei likusios Lietuvos",
                             "Šaltinis: Eurostat, nama_10r_2gdp; skaičiavimas", [("Santykis", santykis)], dec=2,
                             nuo_nulio=False)
    lentele = pd.DataFrame({"Sostines_regionas_ES100": sost, "Vidurio_vakaru_LT_ES100": kiti, "Lietuva_ES100": lt,
                            "santykis": santykis})
    lentele.insert(0, "metai", lentele.index.year)
    kryptis = "nepasikeitė" if round(pokytis, 2) == 0 else ("sumažėjo" if pokytis < 0 else "padidėjo")
    return Rodiklis(
        dalys=[dalis("Vidurio ir vakarų Lietuva (ES = 100)", kiti, "didesne", 1.0, vienetai="", slenkscio_vnt=" punkto",
                     dec=0)],
        id="regionai", pavadinimas="Regioniniai skirtumai",
        trumpas_aprasas="Sostinės ir likusios Lietuvos BVP vienam gyv. santykis",
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena, zenklas=False, dec=2, spark_nuo_nulio=False,
        vertinimo_taisykle=(f"Gerėja, kai santykis per metus sumažėja daugiau nei {sk(SLENKSTIS, False, 2)} "
                            f"(regionai artėja); prastėja, kai tiek pat padidėja; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. Sostinės regione BVP vienam gyventojui siekė {sk(sost.iloc[-1], False, 0)} % "
                                f"ES vidurkio, Vidurio ir vakarų Lietuvoje – {sk(kiti.iloc[-1], False, 0)} %. Santykis – "
                                f"{sk(pask, False, 2)} ({ankst} m. – {sk(pries, False, 2)}), t. y. {kryptis}"
                                + (f" {sk(abs(pokytis), False, 2)}" if round(pokytis, 2) else "") + "."),
        sparkline=santykis, grafikai=[f1, f2],
        apibrezimas=("Sostinės regiono (Vilniaus apskritis) ir Vidurio ir vakarų Lietuvos regiono (likusios 9 apskritys) "
                     "BVP vienam gyventojui pagal perkamosios galios standartą santykis. Rodo, ar ekonominė gerovė "
                     "pasiskirsto tolygiau."),
        pastabos=["Regioniniai duomenys skelbiami su maždaug 1,5 metų vėlavimu.",
                  "Dalis Vilniuje sukuriamo BVP tenka kitų apskričių gyventojams, kurie važinėja į darbą, todėl "
                  "santykis šiek tiek padidina skirtumą."],
        saltiniai=[("Eurostat – nama_10r_2gdp", "https://ec.europa.eu/eurostat/databrowser/view/nama_10r_2gdp/default/table?lang=en")],
        papildomai=[(f"{sk(sost.iloc[-1], False, 0)} %", "Sostinės regionas, ES = 100"),
                    (f"{sk(kiti.iloc[-1], False, 0)} %", "likusi Lietuva, ES = 100")], lentele=lentele)
