"""4. Oro tarša: ankstyvos mirtys dėl kietųjų dalelių KD2,5."""
import pandas as pd

from .bendra import Rodiklis, ivertink, papildomas_grafikas, sk
from .eurostat_duomenys import serija

SLENKSTIS = 5.0     # % per metus (įvertis labai priklauso nuo oro sąlygų)


def rodiklis() -> Rodiklis:
    g = lambda geo, unit="RT": serija("sdg_11_52", geo, airpol="PM2_5", effect="PMD", unit=unit)
    lt, es, sk_lt = g("LT"), g("EU27_2020"), g("LT", "NR")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = (pask / pries - 1) * 100
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)
    f1 = papildomas_grafikas("Ankstyvos mirtys dėl oro taršos kietosiomis dalelėmis (KD2,5)",
                             "Ankstyvų mirčių skaičius 100 tūkst. gyventojų (EEA įvertis)",
                             "Šaltinis: Eurostat, sdg_11_52 (Europos aplinkos agentūra)", [("Lietuva", lt), ("ES-27", es)],
                             dec=0)
    lentele = pd.DataFrame({"LT_100k": lt, "ES27_100k": es, "LT_skaicius": sk_lt})
    lentele.insert(0, "metai", lentele.index.year)
    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"
    return Rodiklis(
        id="oro-tarsa", pavadinimas="Oro tarša (KD2,5)", trumpas_aprasas="ankstyvų mirčių 100 tūkst. gyventojų",
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena, zenklas=False, dec=0, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai rodiklis per metus sumažėja daugiau nei {sk(SLENKSTIS, False, 0)} %; "
                            f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False, 0)} %; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"Europos aplinkos agentūros vertinimu, {metai} m. dėl kietųjų dalelių KD2,5 taršos "
                                f"Lietuvoje anksčiau laiko mirė apie {sk(sk_lt.iloc[-1], False, 0)} žmonių – "
                                f"{sk(pask, False, 0)} 100 tūkst. gyventojų ({ankst} m. – {sk(pries, False, 0)}). "
                                f"Rodiklis {kryptis} {sk(abs(pokytis), False, 0)} %; ES vidurkis – {sk(es.iloc[-1], False, 0)}."),
        sparkline=lt, grafikai=[f1],
        apibrezimas=("Europos aplinkos agentūros (EEA) modeliu įvertintas ankstyvų mirčių, priskirtinų ilgalaikiam "
                     "smulkiųjų kietųjų dalelių (KD2,5) poveikiui, skaičius 100 tūkst. gyventojų. Rodo oro taršos "
                     "poveikį sveikatai."),
        pastabos=["Įvertis modelinis ir priklauso nuo metų oro sąlygų (pvz., šaltų žiemų ir kūrenimo), todėl "
                  "pavieniai metai gali smarkiai svyruoti.",
                  "Duomenys skelbiami su maždaug 2–3 metų vėlavimu."],
        saltiniai=[("Eurostat – sdg_11_52", "https://ec.europa.eu/eurostat/databrowser/view/sdg_11_52/default/table?lang=en")],
        papildomai=[(sk(sk_lt.iloc[-1], False, 0), f"ankstyvų mirčių {metai} m.")], lentele=lentele)
