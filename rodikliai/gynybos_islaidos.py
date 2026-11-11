"""5. Saugumas: gynybos išlaidos, % BVP (NATO duomenys; failas atnaujinamas kartą per metus)."""
import pandas as pd
import plotly.graph_objects as go

from .eurostat_duomenys import serija
from .bendra import dalis, DUOMENYS, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, t, vnt_pp

SLENKSTIS = 0.1     # proc. punkto


def rodiklis() -> Rodiklis:
    d = pd.read_csv(DUOMENYS / "nato_gynybos_islaidos.csv")
    x = pd.to_datetime(d.metai.astype(str) + "-01-01")
    lt = pd.Series(d.LT_proc_BVP.values, index=x)
    nato = pd.Series(d.NATO_Europa_Kanada_proc_BVP.values, index=x)
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai = int(d.metai.iloc[-1])
    ivertis = bool(d.ivertis.iloc[-1])
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    f1 = go.Figure()
    linijos(f1, [("Lietuva", lt, SERIJOS[0]), (t("NATO Europa ir Kanada", "NATO Europe and Canada"), nato, SERIJOS[1])],
            zenklas=False, dec=2, zymekliai=True)
    for y, tekstas in [(2, t("Ankstesnis NATO tikslas – 2 %", "Previous NATO target – 2%")),
                       (3.5, t("NATO tikslas 2035 m. – 3,5 % (pagrindinės išlaidos)", "NATO 2035 target – 3.5% (core spending)"))]:
        f1.add_hline(y=y, line=dict(color=SERIJOS[2], width=1, dash="dash"),
                     annotation_text=tekstas, annotation_position="top left")
    stilius(f1, t("Gynybos išlaidos", "Defence expenditure"), t("% BVP (paskutiniai metai – NATO įvertis)", "% of GDP (latest year – NATO estimate)"),
            "Šaltinis: NATO, Defence Expenditure of NATO Countries", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    g = lambda geo, unit="PC_GDP": serija("gov_10a_exp", geo, unit=unit, sector="S13", cofog99="GF02", na_item="TE")
    es_lt, es_es, es_mln = g("LT"), g("EU27_2020"), g("LT", "MIO_EUR")
    f2 = go.Figure()
    linijos(f2, [("Lietuva", es_lt[es_lt.index >= "2005-01-01"], SERIJOS[0]),
                 ("ES-27", es_es[es_es.index >= "2005-01-01"], SERIJOS[1])], zenklas=False, zymekliai=True)
    stilius(f2, t("Valdžios išlaidos gynybai (faktinės)", "Government expenditure on defence (actual)"),
            t("Valdžios sektoriaus išlaidos pagal COFOG „Gynyba“, % BVP", "General government expenditure on COFOG “Defence”, % of GDP"),
            "Šaltinis: Eurostat, gov_10a_exp", nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    lentele = d.merge(pd.DataFrame({"metai": es_lt.index.year, "Eurostat_COFOG_proc_BVP": es_lt.values,
                                    "Eurostat_COFOG_mln_EUR": es_mln.reindex(es_lt.index).values}),
                      on="metai", how="outer").sort_values("metai")
    zyma = t(" (įvertis)", " (estimate)") if ivertis else ""

    _dalys = [dalis(t("Valdžios išlaidos gynybai (Eurostat COFOG)", "Government expenditure on defence (Eurostat COFOG)"), es_lt, "didesne", SLENKSTIS)]
    return Rodiklis(
        dalys=_dalys,
        id="gynybos-islaidos",
        pavadinimas=t("Gynybos išlaidos", "Defence expenditure"),
        trumpas_aprasas=t("BVP dalis", "share of GDP"),
        reiksme=pask, vienetai="%", laikotarpis=f"{metai}{t(' (įvert.)', ' (est.)') if ivertis else ''}", busena=busena,
        zenklas=False, dec=2, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai gynybos išlaidų dalis BVP per metus padidėja daugiau nei "
                             f"{sk(SLENKSTIS, False)} proc. punkto; prastėja, kai tiek pat sumažėja; kitu atveju – stabilu.",
                             f"Improving when defence spending as a share of GDP rises by more than {sk(SLENKSTIS, False)} "
                             f"percentage point in a year; worsening when it falls by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m.{zyma} Lietuva gynybai skyrė {sk(pask, False, 2)} % BVP "
                                 f"({metai - 1} m. – {sk(pries, False, 2)} %). NATO Europos šalių ir Kanados vidurkis – "
                                 f"{sk(nato.iloc[-1], False, 2)} %.",
                                 f"In {metai}{zyma}, Lithuania spent {sk(pask, False, 2)}% of GDP on defence "
                                 f"({metai - 1}: {sk(pries, False, 2)}%). The average for NATO Europe and Canada is "
                                 f"{sk(nato.iloc[-1], False, 2)}%."),
        sparkline=lt,
        grafikai=[f1, f2],
        apibrezimas=t("Gynybos išlaidos pagal NATO apibrėžtį (kariuomenė, karinė įranga, infrastruktūra, kariniai "
                      "pensijų ir kiti su gynyba susiję mokėjimai) kaip BVP dalis. 2025 m. Hagos viršūnių "
                      "susitikime NATO šalys įsipareigojo iki 2035 m. gynybai skirti 5 % BVP, iš jų 3,5 % – "
                      "pagrindinėms gynybos išlaidoms.",
                      "Defence expenditure according to the NATO definition (armed forces, military equipment, "
                      "infrastructure, military pensions and other defence-related payments) as a share of GDP. At the "
                      "2025 Hague summit NATO members committed to spending 5% of GDP on defence by 2035, of which "
                      "3.5% on core defence requirements."),
        pastabos=[t("Eurostat (COFOG) duomenys apima tik valdžios sektoriaus išlaidas pagal funkciją „Gynyba“ ir "
                    "atnaujinami automatiškai; NATO apibrėžtis platesnė, todėl jos reikšmės didesnės.",
                    "Eurostat (COFOG) data cover only general government spending on the “Defence” function and are "
                    "updated automatically; the NATO definition is broader, so its values are higher."),
                  t("NATO duomenys skelbiami kartą per metus (paprastai birželį); paskutinių metų reikšmė yra "
                    "įvertis. Failas duomenys/nato_gynybos_islaidos.csv atnaujinamas rankiniu būdu.",
                    "NATO data are published once a year (usually in June); the latest year's value is an estimate. "
                    "The file duomenys/nato_gynybos_islaidos.csv is updated manually.")],
        saltiniai=[("NATO – Defence Expenditure of NATO Countries (2014–2025)",
                    "https://www.nato.int/content/dam/nato/webready/documents/finance/def-exp-2025-en.pdf"),
                   ("Eurostat – gov_10a_exp", "https://ec.europa.eu/eurostat/databrowser/view/gov_10a_exp/default/table?lang=en")],
        papildomai=[(f"{sk(pask - nato.iloc[-1])}{vnt_pp()}", t("palyginti su NATO Europa ir Kanada", "relative to NATO Europe and Canada")),
                    (f"{sk(lt.iloc[0], False, 2)} %", t(f"{d.metai.iloc[0]} m.", f"in {d.metai.iloc[0]}"))],
        lentele=lentele,
    )
