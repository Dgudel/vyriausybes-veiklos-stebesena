"""6. Visuomenės senėjimas: senatvės priklausomybės koeficientas (65+ / 15–64)."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, t
from .eurostat_duomenys import serija

SLENKSTIS = 0.5     # punkto


def rodiklis() -> Rodiklis:
    g = lambda kodas, geo="LT": serija("demo_pjanind", geo, indic_de=kodas)
    lt, es = g("OLDDEP1"), g("OLDDEP1", "EU27_2020")
    vaikai, seni, mediana = g("PC_Y0_14"), g("PC_Y65_MAX"), g("MEDAGEPOP")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)

    nuo = "1995-01-01"
    f1 = go.Figure()
    linijos(f1, [("Lietuva", lt[lt.index >= nuo], SERIJOS[0]), ("ES-27", es[es.index >= nuo].dropna(), SERIJOS[1])],
            vnt="", zenklas=False)
    stilius(f1, t("Senatvės priklausomybės koeficientas", "Old-age dependency ratio"),
            t("65 m. ir vyresnių žmonių skaičius 100-ui darbingo amžiaus (15–64 m.) žmonių",
              "People aged 65 and over per 100 people of working age (15–64)"),
            "Šaltinis: Eurostat, demo_pjanind", vnt="", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    linijos(f2, [(t("65 m. ir vyresni", "Aged 65 and over"), seni[seni.index >= nuo], SERIJOS[0]),
                 (t("Vaikai (0–14 m.)", "Children (0–14)"), vaikai[vaikai.index >= nuo], SERIJOS[3])], zenklas=False)
    stilius(f2, t("Vaikų ir vyresnio amžiaus žmonių dalis", "Share of children and older people"),
            t("% visų Lietuvos gyventojų", "% of Lithuania's population"),
            "Šaltinis: Eurostat, demo_pjanind", nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    lentele = (lt.rename("LT_koeficientas").to_frame().join(es.rename("ES27_koeficientas"))
               .join(seni.rename("LT_65plus_proc")).join(vaikai.rename("LT_0_14_proc"))
               .join(mediana.rename("LT_amziaus_mediana")))
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = t("padidėjo", "rose by") if pokytis > 0 else t("sumažėjo", "fell by")

    _dalys = [dalis(t("65 m. ir vyresnių dalis", "Share aged 65 and over"), seni, "mazesne", 0.3),
              dalis(t("Vaikų (0–14 m.) dalis", "Share of children (0–14)"), vaikai, "didesne", 0.3)]
    return Rodiklis(
        dalys=_dalys,
        id="senejimas",
        pavadinimas=t("Visuomenės senėjimas", "Population ageing"),
        trumpas_aprasas=t("65+ m. žmonių 100-ui darbingo amžiaus", "people aged 65+ per 100 of working age"),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=False,
        vertinimo_taisykle=t(f"Gerėja, kai koeficientas per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} punkto; "
                             f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)} punkto; kitu atveju – stabilu.",
                             f"Improving when the ratio falls by more than {sk(SLENKSTIS, False)} points in a year; "
                             f"worsening when it rises by more than {sk(SLENKSTIS, False)} points; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. pradžioje senatvės priklausomybės koeficientas – {sk(pask, False)}: tiek 65 m. ir vyresnių "
                                 f"žmonių tenka 100 darbingo amžiaus gyventojų ({ankst} m. – {sk(pries, False)}). Koeficientas "
                                 f"{kryptis} {sk(abs(pokytis), False)} punkto; ES vidurkis – {sk(es.iloc[-1], False)}. "
                                 f"Gyventojų amžiaus mediana – {sk(mediana.iloc[-1], False)} m.",
                                 f"At the start of {metai}, the old-age dependency ratio was {sk(pask, False)}: this many "
                                 f"people aged 65 and over per 100 people of working age ({ankst}: {sk(pries, False)}). The "
                                 f"ratio {kryptis} {sk(abs(pokytis), False)} points; the EU average is {sk(es.iloc[-1], False)}. "
                                 f"The median age is {sk(mediana.iloc[-1], False)} years."),
        sparkline=lt[lt.index >= "2005-01-01"],
        grafikai=[f1, f2],
        apibrezimas=t("Senatvės priklausomybės koeficientas – 65 metų ir vyresnių gyventojų skaičius, tenkantis 100 "
                      "darbingo amžiaus (15–64 m.) gyventojų, sausio 1 d. Kuo jis didesnis, tuo mažiau dirbančiųjų "
                      "tenka vienam pensinio amžiaus žmogui.",
                      "The old-age dependency ratio is the number of people aged 65 and over per 100 people of working "
                      "age (15–64) on 1 January. The higher it is, the fewer workers there are per person of pension age."),
        pastabos=[t("Rodiklis keičiasi lėtai ir daugiausia priklauso nuo ankstesnių dešimtmečių gimstamumo ir "
                    "emigracijos, todėl trumpuoju laikotarpiu Vyriausybės sprendimai jį veikia mažai.",
                    "The indicator changes slowly and depends mostly on fertility and emigration in previous decades, "
                    "so government decisions have little effect on it in the short term.")],
        saltiniai=[("Eurostat – demo_pjanind", "https://ec.europa.eu/eurostat/databrowser/view/demo_pjanind/default/table?lang=en")],
        papildomai=[(f"{sk(seni.iloc[-1], False)} %", t(f"gyventojų – 65 m. ir vyresni, {metai} m.", f"of the population aged 65 and over, {metai}")),
                    (t(f"{sk(mediana.iloc[-1], False)} m.", f"{sk(mediana.iloc[-1], False)} yrs"), t("amžiaus mediana", "median age"))],
        lentele=lentele,
    )
