"""1. Pajamų nelygybė: S80/S20 santykis + Gini koeficientas."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, t
from .eurostat_duomenys import serija

SLENKSTIS = 0.2     # santykio punktų per metus


def rodiklis() -> Rodiklis:
    f = dict(age="TOTAL", sex="T", unit="RAT")
    lt, es = serija("ilc_di11", "LT", **f), serija("ilc_di11", "EU27_2020", **f)
    gini_lt = serija("ilc_di12", "LT", age="TOTAL", statinfo="GINI_HND")
    gini_es = serija("ilc_di12", "EU27_2020", age="TOTAL", statinfo="GINI_HND")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)

    nuo = "2005-01-01"
    f1 = go.Figure()
    linijos(f1, [("Lietuva", lt[lt.index >= nuo], SERIJOS[0]), ("ES-27", es[es.index >= nuo], SERIJOS[1])],
            vnt="", zenklas=False, dec=2, zymekliai=True)
    stilius(f1, t("Pajamų kvintilių santykis S80/S20", "Income quintile share ratio S80/S20"),
            t("Kiek kartų turtingiausių 20 % gyventojų pajamos didesnės už mažiausiai uždirbančių 20 %",
              "How many times higher the income of the richest 20% is than that of the poorest 20%"),
            "Šaltinis: Eurostat, ilc_di11 (EU-SILC)", vnt="", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    linijos(f2, [("Lietuva", gini_lt[gini_lt.index >= nuo], SERIJOS[0]),
                 ("ES-27", gini_es[gini_es.index >= nuo], SERIJOS[1])], vnt="", zenklas=False, zymekliai=True)
    stilius(f2, t("Gini koeficientas", "Gini coefficient"),
            t("0 – visų pajamos vienodos, 100 – visos pajamos tenka vienam žmogui",
              "0 – everyone has equal income, 100 – one person receives all income"),
            "Šaltinis: Eurostat, ilc_di12 (EU-SILC)", vnt="", nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    lentele = pd.DataFrame({"LT_S80_S20": lt, "ES27_S80_S20": es, "LT_Gini": gini_lt, "ES27_Gini": gini_es})
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    _dalys = [dalis(t("Gini koeficientas", "Gini coefficient"), gini_lt, "mazesne", 0.5, vienetai="",
                    slenkscio_vnt=t(" punkto", " points"))]

    kryptis = (t("sumažėjo", "decreased by") if pokytis < 0 else
               (t("padidėjo", "increased by") if pokytis > 0 else t("nepasikeitė", "was unchanged")))
    return Rodiklis(
        dalys=_dalys,
        id="nelygybe",
        pavadinimas=t("Pajamų nelygybė", "Income inequality"),
        trumpas_aprasas=t("turtingiausių ir vargingiausių 20 % pajamų santykis", "income ratio of the richest to the poorest 20%"),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena,
        zenklas=False, dec=2, spark_nuo_nulio=False,
        vertinimo_taisykle=t(f"Gerėja, kai santykis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)}; "
                             f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)}; kitu atveju – stabilu.",
                             f"Improving when the ratio falls by more than {sk(SLENKSTIS, False)} in a year; "
                             f"worsening when it rises by more than {sk(SLENKSTIS, False)}; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. tyrimo duomenimis, turtingiausių 20 % gyventojų pajamos buvo "
                                 f"{sk(pask, False, 2)} karto didesnės nei mažiausias pajamas gaunančių 20 % "
                                 f"({ankst} m. – {sk(pries, False, 2)}). Santykis "
                                 + (f"{kryptis} {sk(abs(pokytis), False, 2)}" if pokytis else kryptis)
                                 + f"; ES vidurkis – {sk(es.iloc[-1], False, 2)}. Gini koeficientas – "
                                 f"{sk(gini_lt.iloc[-1], False)} (ES – {sk(gini_es.iloc[-1], False)}).",
                                 f"According to the {metai} survey, the income of the richest 20% was "
                                 f"{sk(pask, False, 2)} times that of the poorest 20% ({ankst}: {sk(pries, False, 2)}). "
                                 f"The ratio " + (f"{kryptis} {sk(abs(pokytis), False, 2)}" if pokytis else kryptis)
                                 + f"; the EU average is {sk(es.iloc[-1], False, 2)}. The Gini coefficient is "
                                 f"{sk(gini_lt.iloc[-1], False)} (EU: {sk(gini_es.iloc[-1], False)})."),
        sparkline=lt[lt.index >= "2010-01-01"],
        grafikai=[f1, f2],
        apibrezimas=t("S80/S20 – 20 % didžiausias ekvivalentines disponuojamąsias pajamas gaunančių gyventojų pajamų "
                      "sumos ir 20 % mažiausias pajamas gaunančių gyventojų pajamų sumos santykis. Gini koeficientas "
                      "apibendrina viso pajamų pasiskirstymo nelygybę.",
                      "S80/S20 is the ratio of the total equivalised disposable income of the 20% of the population "
                      "with the highest income to that of the 20% with the lowest income. The Gini coefficient "
                      "summarises inequality across the whole income distribution."),
        pastabos=[t("Duomenys – EU-SILC tyrimo: metų tyrimas aprašo praėjusių metų pajamas.",
                    "Data come from EU-SILC: each year's survey describes the previous year's income."),
                  t("Lietuvoje pajamų nelygybė viena didžiausių ES.",
                    "Income inequality in Lithuania is among the highest in the EU.")],
        saltiniai=[("Eurostat – ilc_di11", "https://ec.europa.eu/eurostat/databrowser/view/ilc_di11/default/table?lang=en"),
                   ("Eurostat – ilc_di12", "https://ec.europa.eu/eurostat/databrowser/view/ilc_di12/default/table?lang=en")],
        papildomai=[(sk(gini_lt.iloc[-1], False), t(f"Gini koeficientas, {gini_lt.index[-1].year} m.",
                                                     f"Gini coefficient, {gini_lt.index[-1].year}")),
                    (sk(es.iloc[-1], False, 2), t("S80/S20 ES vidurkis", "S80/S20 EU average"))],
        lentele=lentele,
    )
