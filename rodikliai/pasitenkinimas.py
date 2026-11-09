"""1. Pasitenkinimas gyvenimu (EU-SILC, 0–10 skalė)."""
import pandas as pd

from .bendra import Rodiklis, dalis, ivertink, papildomas_grafikas, sk
from .eurostat_duomenys import serija

SLENKSTIS = 0.1     # balo


def _s(geo, age="Y_GE16"):
    return serija("ilc_pw01", geo, statinfo="AVG", unit="RTG", isced11="TOTAL", life_sat="LIFE", sex="T", age=age)


def rodiklis() -> Rodiklis:
    lt, es = _s("LT"), _s("EU27_2020")
    jauni, seni = _s("LT", "Y16-29"), _s("LT", "Y_GE65")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    f1 = papildomas_grafikas("Pasitenkinimas gyvenimu", "Vidutinis įvertinimas 0–10 skalėje, 16 m. ir vyresni",
                             "Šaltinis: Eurostat, ilc_pw01 (EU-SILC)", [("Lietuva", lt), ("ES-27", es)])
    f2 = papildomas_grafikas("Pasitenkinimas gyvenimu pagal amžių", "Vidutinis įvertinimas 0–10 skalėje, Lietuva",
                             "Šaltinis: Eurostat, ilc_pw01", [("16–29 m.", jauni), ("65 m. ir vyresni", seni)])
    lentele = pd.DataFrame({"LT": lt, "ES27": es, "LT_16_29": jauni, "LT_65plus": seni})
    lentele.insert(0, "metai", lentele.index.year)
    kryptis = "padidėjo" if pokytis > 0 else ("sumažėjo" if pokytis < 0 else "nepasikeitė")
    return Rodiklis(
        dalys=[dalis("Jaunimas (16–29 m.)", jauni, "didesne", SLENKSTIS, vienetai="", slenkscio_vnt=" balo"),
               dalis("Vyresni (65 m. ir daugiau)", seni, "didesne", SLENKSTIS, vienetai="", slenkscio_vnt=" balo")],
        id="pasitenkinimas", pavadinimas="Pasitenkinimas gyvenimu", trumpas_aprasas="vidutinis įvertinimas, 0–10",
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena, zenklas=False, spark_nuo_nulio=False,
        vertinimo_taisykle=(f"Gerėja, kai vidutinis įvertinimas per metus padidėja daugiau nei {sk(SLENKSTIS, False)} "
                            f"balo; prastėja, kai tiek pat sumažėja; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. gyventojai savo gyvenimą vidutiniškai vertino {sk(pask, False)} balo iš 10 "
                                f"({ankst} m. – {sk(pries, False)}); įvertinimas {kryptis}"
                                + (f" {sk(abs(pokytis), False)} balo" if pokytis else "")
                                + f". ES vidurkis – {sk(es.iloc[-1], False)}. Jaunimas vertina {sk(jauni.iloc[-1], False)}, "
                                f"vyresni nei 65 m. – {sk(seni.iloc[-1], False)}."),
        sparkline=lt, grafikai=[f1, f2],
        apibrezimas=("Atsakymų į klausimą „Kiek apskritai esate patenkinti savo gyvenimu?“ (0 – visiškai nepatenkintas, "
                     "10 – visiškai patenkintas) vidurkis, Gyventojų pajamų ir gyvenimo sąlygų tyrimas (EU-SILC)."),
        pastabos=["Klausimas užduodamas ne kasmet visose šalyse; 2013 ir 2018 m. – specialieji tyrimo moduliai."],
        saltiniai=[("Eurostat – ilc_pw01", "https://ec.europa.eu/eurostat/databrowser/view/ilc_pw01/default/table?lang=en")],
        papildomai=[(sk(es.iloc[-1], False), "ES vidurkis")], lentele=lentele)
