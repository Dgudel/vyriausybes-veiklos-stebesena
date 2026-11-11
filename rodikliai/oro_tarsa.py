"""4. Oro tarša: ankstyvos mirtys dėl kietųjų dalelių KD2,5."""
import pandas as pd

from .bendra import Rodiklis, ivertink, papildomas_grafikas, sk, t
from .eurostat_duomenys import serija

SLENKSTIS = 5.0     # % per metus (įvertis labai priklauso nuo oro sąlygų)


def rodiklis() -> Rodiklis:
    g = lambda geo, unit="RT": serija("sdg_11_52", geo, airpol="PM2_5", effect="PMD", unit=unit)
    lt, es, sk_lt = g("LT"), g("EU27_2020"), g("LT", "NR")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = (pask / pries - 1) * 100
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)
    f1 = papildomas_grafikas(t("Ankstyvos mirtys dėl oro taršos kietosiomis dalelėmis (KD2,5)", "Premature deaths due to fine particulate matter (PM2.5)"),
                             t("Ankstyvų mirčių skaičius 100 tūkst. gyventojų (EEA įvertis)", "Premature deaths per 100,000 inhabitants (EEA estimate)"),
                             t("Šaltinis: Eurostat, sdg_11_52 (Europos aplinkos agentūra)", "Source: Eurostat, sdg_11_52 (European Environment Agency)"), [("Lietuva", lt), ("ES-27", es)],
                             dec=0)
    lentele = pd.DataFrame({"LT_100k": lt, "ES27_100k": es, "LT_skaicius": sk_lt})
    lentele.insert(0, "metai", lentele.index.year)
    kryptis = t("sumažėjo", "fell by") if pokytis < 0 else t("padidėjo", "rose by")
    return Rodiklis(
        id="oro-tarsa", pavadinimas=t("Oro tarša (KD2,5)", "Air pollution (PM2.5)"),
        trumpas_aprasas=t("ankstyvų mirčių 100 tūkst. gyventojų", "premature deaths per 100,000 inhabitants"),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena, zenklas=False, dec=0, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai rodiklis per metus sumažėja daugiau nei {sk(SLENKSTIS, False, 0)} %; "
                             f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False, 0)} %; kitu atveju – stabilu.",
                             f"Improving when the rate falls by more than {sk(SLENKSTIS, False, 0)}% in a year; "
                             f"worsening when it rises by more than {sk(SLENKSTIS, False, 0)}%; otherwise stable."),
        vertinimo_paaiskinimas=t(f"Europos aplinkos agentūros vertinimu, {metai} m. dėl kietųjų dalelių KD2,5 taršos "
                                 f"Lietuvoje anksčiau laiko mirė apie {sk(sk_lt.iloc[-1], False, 0)} žmonių – "
                                 f"{sk(pask, False, 0)} 100 tūkst. gyventojų ({ankst} m. – {sk(pries, False, 0)}). "
                                 f"Rodiklis {kryptis} {sk(abs(pokytis), False, 0)} %; ES vidurkis – {sk(es.iloc[-1], False, 0)}.",
                                 f"According to the European Environment Agency, about {sk(sk_lt.iloc[-1], False, 0)} "
                                 f"people in Lithuania died prematurely in {metai} due to PM2.5 pollution – "
                                 f"{sk(pask, False, 0)} per 100,000 inhabitants ({ankst}: {sk(pries, False, 0)}). The rate "
                                 f"{kryptis} {sk(abs(pokytis), False, 0)}%; the EU average is {sk(es.iloc[-1], False, 0)}."),
        sparkline=lt, grafikai=[f1],
        apibrezimas=t("Europos aplinkos agentūros (EEA) modeliu įvertintas ankstyvų mirčių, priskirtinų ilgalaikiam "
                      "smulkiųjų kietųjų dalelių (KD2,5) poveikiui, skaičius 100 tūkst. gyventojų. Rodo oro taršos "
                      "poveikį sveikatai.",
                      "Number of premature deaths attributable to long-term exposure to fine particulate matter (PM2.5) "
                      "per 100,000 inhabitants, as modelled by the European Environment Agency (EEA). Shows the health "
                      "impact of air pollution."),
        pastabos=[t("Įvertis modelinis ir priklauso nuo metų oro sąlygų (pvz., šaltų žiemų ir kūrenimo), todėl "
                    "pavieniai metai gali smarkiai svyruoti.",
                    "The estimate is model-based and depends on each year's weather (e.g. cold winters and heating), "
                    "so individual years may fluctuate strongly."),
                  t("Duomenys skelbiami su maždaug 2–3 metų vėlavimu.", "Data are published with a delay of about 2–3 years.")],
        saltiniai=[("Eurostat – sdg_11_52", "https://ec.europa.eu/eurostat/databrowser/view/sdg_11_52/default/table?lang=en")],
        papildomai=[(sk(sk_lt.iloc[-1], False, 0), t(f"ankstyvų mirčių {metai} m.", f"premature deaths in {metai}"))], lentele=lentele)
