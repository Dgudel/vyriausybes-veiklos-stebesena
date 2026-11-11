"""4. Atsinaujinančių išteklių dalis energijos suvartojime + energetinė priklausomybė."""
import pandas as pd

from .bendra import Rodiklis, dalis, ivertink, papildomas_grafikas, sk, t
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
    f1 = papildomas_grafikas(t("Atsinaujinančių išteklių dalis", "Share of renewable energy"),
                             t("% galutinio energijos suvartojimo (ES tikslas 2030 m. – 42,5 %)", "% of gross final energy consumption (EU 2030 target – 42.5%)"),
                             "Šaltinis: Eurostat, sdg_07_40", [("Lietuva", lt), ("ES-27", es)], vnt=" %", nuo="2005-01-01")
    f2 = papildomas_grafikas(t("Atsinaujinanti energija pagal sektorių", "Renewable energy by sector"),
                             t("% kiekvieno sektoriaus suvartojimo, Lietuva", "% of each sector's consumption, Lithuania"),
                             "Šaltinis: Eurostat, sdg_07_40",
                             [(t("Elektra", "Electricity"), elek), (t("Šildymas ir vėsinimas", "Heating and cooling"), sil),
                              (t("Transportas", "Transport"), tra)], vnt=" %",
                             nuo="2005-01-01")
    f3 = papildomas_grafikas(t("Energetinė priklausomybė nuo importo", "Energy import dependency"),
                             t("Grynasis importas, % visų energijos poreikių", "Net imports, % of total energy needs"),
                             "Šaltinis: Eurostat, nrg_ind_id", [("Lietuva", prikl), ("ES-27", prikl_es)], vnt=" %",
                             nuo="2005-01-01")
    lentele = pd.DataFrame({"LT_proc": lt, "ES27_proc": es, "LT_elektra": elek, "LT_silumа": sil, "LT_transportas": tra,
                            "LT_priklausomybe": prikl})
    lentele = lentele[lentele.index >= "2005-01-01"]
    lentele.insert(0, "metai", lentele.index.year)
    return Rodiklis(
        dalys=[dalis(t("Elektra iš atsinaujinančių išteklių", "Electricity from renewable sources"), elek, "didesne", SLENKSTIS),
               dalis(t("Šildymas ir vėsinimas iš atsinaujinančių išteklių", "Heating and cooling from renewable sources"), sil, "didesne", SLENKSTIS),
               dalis(t("Transportas – atsinaujinanti energija", "Transport – renewable energy"), tra, "didesne", 0.5),
               dalis(t("Energetinė priklausomybė nuo importo", "Energy import dependency"), prikl, "mazesne", 2.0)],
        id="atsinaujinanti-energija", pavadinimas=t("Atsinaujinanti energija", "Renewable energy"),
        trumpas_aprasas=t("dalis galutiniame energijos suvartojime", "share of gross final energy consumption"),
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena, zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai dalis per metus padidėja daugiau nei {sk(SLENKSTIS, False, 0)} proc. punktu; "
                             f"prastėja, kai tiek pat sumažėja; kitu atveju – stabilu.",
                             f"Improving when the share rises by more than {sk(SLENKSTIS, False, 0)} percentage point in "
                             f"a year; worsening when it falls by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. atsinaujinantys ištekliai sudarė {sk(pask, False)} % galutinio energijos "
                                 f"suvartojimo ({ankst} m. – {sk(pries, False)} %; ES – {sk(es.iloc[-1], False)} %). "
                                 f"Elektroje – {sk(elek.iloc[-1], False)} %, transporte – {sk(tra.dropna().iloc[-1], False)} %. "
                                 f"Importuojama {sk(prikl.iloc[-1], False, 0)} % reikalingos energijos "
                                 f"({prikl.index[-1].year} m.).",
                                 f"In {metai}, renewable sources made up {sk(pask, False)}% of gross final energy "
                                 f"consumption ({ankst}: {sk(pries, False)}%; EU: {sk(es.iloc[-1], False)}%). In "
                                 f"electricity – {sk(elek.iloc[-1], False)}%, in transport – {sk(tra.dropna().iloc[-1], False)}%. "
                                 f"{sk(prikl.iloc[-1], False, 0)}% of the energy needed is imported ({prikl.index[-1].year})."),
        sparkline=lt[lt.index >= "2005-01-01"], grafikai=[f1, f2, f3],
        apibrezimas=t("Energijos iš atsinaujinančių išteklių (vėjo, saulės, biokuro, hidro ir kt.) dalis bendrame "
                      "galutiniame energijos suvartojime pagal ES Atsinaujinančiųjų išteklių direktyvos metodiką. "
                      "Energetinė priklausomybė – grynojo energijos importo dalis visuose šalies energijos poreikiuose.",
                      "Share of energy from renewable sources (wind, solar, biofuels, hydro, etc.) in gross final energy "
                      "consumption according to the EU Renewable Energy Directive methodology. Energy import dependency "
                      "is the share of net energy imports in the country's total energy needs."),
        pastabos=[t("Naujausių metų reikšmė gali būti išankstinė (Eurostat SHARES apskaita).",
                    "The latest year's value may be provisional (Eurostat SHARES accounts)."),
                  t("Energetinės priklausomybės šuolį 2010 m. lėmė Ignalinos atominės elektrinės uždarymas.",
                    "The jump in energy dependency in 2010 was caused by the closure of the Ignalina nuclear power plant.")],
        saltiniai=[("Eurostat – sdg_07_40", "https://ec.europa.eu/eurostat/databrowser/view/sdg_07_40/default/table?lang=en"),
                   ("Eurostat – nrg_ind_id", "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_id/default/table?lang=en")],
        papildomai=[(f"{sk(elek.iloc[-1], False, 0)} %", t("elektros iš atsinaujinančių išteklių", "of electricity from renewable sources")),
                    (f"{sk(prikl.iloc[-1], False, 0)} %", t("energijos importuojama", "of energy is imported"))], lentele=lentele)
