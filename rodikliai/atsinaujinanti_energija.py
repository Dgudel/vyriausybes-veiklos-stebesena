"""4. Atsinaujinančių išteklių dalis energijos suvartojime + energetinė priklausomybė."""
import pandas as pd

from .bendra import Rodiklis, dalis, ivertink, papildomas_grafikas, sk
from .eurostat_duomenys import serija

SLENKSTIS = 1.0     # proc. punkto


def rodiklis() -> Rodiklis:
    g = lambda kodas, geo="LT": serija("sdg_07_40", geo, nrg_bal=kodas, unit="PC")
    lt, es = g("REN"), g("REN", "EU27_2020")
    elek, sil, tra = g("REN_ELC"), g("REN_HEAT_CL"), g("REN_TRA")
    prikl = serija("nrg_ind_id", "LT", siec="TOTAL", unit="PC")
    prikl_es = serija("nrg_ind_id", "EU27_2020", siec="TOTAL", unit="PC")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)
    f1 = papildomas_grafikas("Atsinaujinančių išteklių dalis", "% galutinio energijos suvartojimo (ES tikslas 2030 m. – 42,5 %)",
                             "Šaltinis: Eurostat, sdg_07_40", [("Lietuva", lt), ("ES-27", es)], vnt=" %", nuo="2005-01-01")
    f2 = papildomas_grafikas("Atsinaujinanti energija pagal sektorių", "% kiekvieno sektoriaus suvartojimo, Lietuva",
                             "Šaltinis: Eurostat, sdg_07_40",
                             [("Elektra", elek), ("Šildymas ir vėsinimas", sil), ("Transportas", tra)], vnt=" %",
                             nuo="2005-01-01")
    f3 = papildomas_grafikas("Energetinė priklausomybė nuo importo", "Grynasis importas, % visų energijos poreikių",
                             "Šaltinis: Eurostat, nrg_ind_id", [("Lietuva", prikl), ("ES-27", prikl_es)], vnt=" %",
                             nuo="2005-01-01")
    lentele = pd.DataFrame({"LT_proc": lt, "ES27_proc": es, "LT_elektra": elek, "LT_silumа": sil, "LT_transportas": tra,
                            "LT_priklausomybe": prikl})
    lentele = lentele[lentele.index >= "2005-01-01"]
    lentele.insert(0, "metai", lentele.index.year)
    return Rodiklis(
        dalys=[dalis("Elektra iš atsinaujinančių išteklių", elek, "didesne", SLENKSTIS),
               dalis("Šildymas ir vėsinimas iš atsinaujinančių išteklių", sil, "didesne", SLENKSTIS),
               dalis("Transportas – atsinaujinanti energija", tra, "didesne", 0.5),
               dalis("Energetinė priklausomybė nuo importo", prikl, "mazesne", 2.0)],
        id="atsinaujinanti-energija", pavadinimas="Atsinaujinanti energija",
        trumpas_aprasas="dalis galutiniame energijos suvartojime",
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena, zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai dalis per metus padidėja daugiau nei {sk(SLENKSTIS, False, 0)} proc. punktu; "
                            f"prastėja, kai tiek pat sumažėja; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. atsinaujinantys ištekliai sudarė {sk(pask, False)} % galutinio energijos "
                                f"suvartojimo ({ankst} m. – {sk(pries, False)} %; ES – {sk(es.iloc[-1], False)} %). "
                                f"Elektroje – {sk(elek.iloc[-1], False)} %, transporte – {sk(tra.dropna().iloc[-1], False)} %. "
                                f"Importuojama {sk(prikl.iloc[-1], False, 0)} % reikalingos energijos "
                                f"({prikl.index[-1].year} m.)."),
        sparkline=lt[lt.index >= "2005-01-01"], grafikai=[f1, f2, f3],
        apibrezimas=("Energijos iš atsinaujinančių išteklių (vėjo, saulės, biokuro, hidro ir kt.) dalis bendrame "
                     "galutiniame energijos suvartojime pagal ES Atsinaujinančiųjų išteklių direktyvos metodiką. "
                     "Energetinė priklausomybė – grynojo energijos importo dalis visuose šalies energijos poreikiuose."),
        pastabos=["Naujausių metų reikšmė gali būti išankstinė (Eurostat SHARES apskaita).",
                  "Energetinės priklausomybės šuolį 2010 m. lėmė Ignalinos atominės elektrinės uždarymas."],
        saltiniai=[("Eurostat – sdg_07_40", "https://ec.europa.eu/eurostat/databrowser/view/sdg_07_40/default/table?lang=en"),
                   ("Eurostat – nrg_ind_id", "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_id/default/table?lang=en")],
        papildomai=[(f"{sk(elek.iloc[-1], False, 0)} %", "elektros iš atsinaujinančių išteklių"),
                    (f"{sk(prikl.iloc[-1], False, 0)} %", "energijos importuojama")], lentele=lentele)
