"""5. Saugumas: gynybos išlaidos, % BVP (NATO duomenys; failas atnaujinamas kartą per metus)."""
import pandas as pd
import plotly.graph_objects as go

from .eurostat_duomenys import serija
from .bendra import DUOMENYS, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius

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
    linijos(f1, [("Lietuva", lt, SERIJOS[0]), ("NATO Europa ir Kanada", nato, SERIJOS[1])],
            zenklas=False, dec=2, zymekliai=True)
    for y, tekstas in [(2, "Ankstesnis NATO tikslas – 2 %"), (3.5, "NATO tikslas 2035 m. – 3,5 % (pagrindinės išlaidos)")]:
        f1.add_hline(y=y, line=dict(color=SERIJOS[2], width=1, dash="dash"),
                     annotation_text=tekstas, annotation_position="top left")
    stilius(f1, "Gynybos išlaidos", "% BVP (paskutiniai metai – NATO įvertis)",
            "Šaltinis: NATO, Defence Expenditure of NATO Countries", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    g = lambda geo, unit="PC_GDP": serija("gov_10a_exp", geo, unit=unit, sector="S13", cofog99="GF02", na_item="TE")
    es_lt, es_es, es_mln = g("LT"), g("EU27_2020"), g("LT", "MIO_EUR")
    f2 = go.Figure()
    linijos(f2, [("Lietuva", es_lt[es_lt.index >= "2005-01-01"], SERIJOS[0]),
                 ("ES-27", es_es[es_es.index >= "2005-01-01"], SERIJOS[1])], zenklas=False, zymekliai=True)
    stilius(f2, "Valdžios išlaidos gynybai (faktinės)", "Valdžios sektoriaus išlaidos pagal COFOG „Gynyba“, % BVP",
            "Šaltinis: Eurostat, gov_10a_exp", nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    lentele = d.merge(pd.DataFrame({"metai": es_lt.index.year, "Eurostat_COFOG_proc_BVP": es_lt.values,
                                    "Eurostat_COFOG_mln_EUR": es_mln.reindex(es_lt.index).values}),
                      on="metai", how="outer").sort_values("metai")
    zyma = " (įvertis)" if ivertis else ""
    return Rodiklis(
        id="gynybos-islaidos",
        pavadinimas="Gynybos išlaidos",
        trumpas_aprasas="BVP dalis",
        reiksme=pask, vienetai="%", laikotarpis=f"{metai}{' (įvert.)' if ivertis else ''}", busena=busena,
        zenklas=False, dec=2, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai gynybos išlaidų dalis BVP per metus padidėja daugiau nei "
                            f"{sk(SLENKSTIS, False)} proc. punkto; prastėja, kai tiek pat sumažėja; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m.{zyma} Lietuva gynybai skyrė {sk(pask, False, 2)} % BVP "
                                f"({metai - 1} m. – {sk(pries, False, 2)} %). NATO Europos šalių ir Kanados vidurkis – "
                                f"{sk(nato.iloc[-1], False, 2)} %."),
        sparkline=lt,
        grafikai=[f1, f2],
        apibrezimas=("Gynybos išlaidos pagal NATO apibrėžtį (kariuomenė, karinė įranga, infrastruktūra, kariniai "
                     "pensijų ir kiti su gynyba susiję mokėjimai) kaip BVP dalis. 2025 m. Hagos viršūnių "
                     "susitikime NATO šalys įsipareigojo iki 2035 m. gynybai skirti 5 % BVP, iš jų 3,5 % – "
                     "pagrindinėms gynybos išlaidoms."),
        pastabos=["Eurostat (COFOG) duomenys apima tik valdžios sektoriaus išlaidas pagal funkciją „Gynyba“ ir "
                  "atnaujinami automatiškai; NATO apibrėžtis platesnė, todėl jos reikšmės didesnės.",
                  "NATO duomenys skelbiami kartą per metus (paprastai birželį); paskutinių metų reikšmė yra "
                  "įvertis. Failas duomenys/nato_gynybos_islaidos.csv atnaujinamas rankiniu būdu."],
        saltiniai=[("NATO – Defence Expenditure of NATO Countries (2014–2025)",
                    "https://www.nato.int/content/dam/nato/webready/documents/finance/def-exp-2025-en.pdf"),
                   ("Eurostat – gov_10a_exp", "https://ec.europa.eu/eurostat/databrowser/view/gov_10a_exp/default/table?lang=en")],
        papildomai=[(f"{sk(pask - nato.iloc[-1])} p. p.", "palyginti su NATO Europa ir Kanada"),
                    (f"{sk(lt.iloc[0], False, 2)} %", f"{d.metai.iloc[0]} m.")],
        lentele=lentele,
    )
