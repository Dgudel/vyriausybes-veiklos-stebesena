"""4. Žiedinė ekonomika: perdirbamų komunalinių atliekų dalis."""
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, t, vnt_pp
from .eurostat_duomenys import serija

SLENKSTIS = 1.0     # proc. punkto


def rodiklis() -> Rodiklis:
    lt, es = serija("sdg_11_60", "LT", unit="PC"), serija("sdg_11_60", "EU27_2020", unit="PC")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    nuo = "2005-01-01"
    f1 = go.Figure()
    linijos(f1, [("Lietuva", lt[lt.index >= nuo], SERIJOS[0]), ("ES-27", es[es.index >= nuo], SERIJOS[1])],
            zenklas=False, zymekliai=True)
    f1.add_hline(y=55, line=dict(color=SERIJOS[2], width=1, dash="dash"),
                 annotation_text=t("ES tikslas 2025 m. – 55 %", "EU 2025 target – 55%"), annotation_position="top left")
    stilius(f1, t("Perdirbamų komunalinių atliekų dalis", "Municipal waste recycling rate"),
            t("Perdirbta ir kompostuota, % visų komunalinių atliekų", "Recycled and composted, % of all municipal waste"),
            "Šaltinis: Eurostat, sdg_11_60", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    lentele = lt.rename("LT_proc").to_frame().join(es.rename("ES27_proc"))
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = t("padidėjo", "rose by") if pokytis > 0 else t("sumažėjo", "fell by")
    return Rodiklis(
        id="atlieku-perdirbimas",
        pavadinimas=t("Komunalinių atliekų perdirbimas", "Municipal waste recycling"),
        trumpas_aprasas=t("perdirbama atliekų dalis", "share of waste recycled"),
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai dalis per metus padidėja daugiau nei {sk(SLENKSTIS, False, 0)} proc. punktu; "
                             f"prastėja, kai sumažėja daugiau nei {sk(SLENKSTIS, False, 0)} proc. punktu; kitu atveju – stabilu.",
                             f"Improving when the share rises by more than {sk(SLENKSTIS, False, 0)} percentage point in "
                             f"a year; worsening when it falls by more than {sk(SLENKSTIS, False, 0)} percentage point; "
                             "otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. perdirbta {sk(pask, False)} % komunalinių atliekų ({ankst} m. – "
                                 f"{sk(pries, False)} %). Dalis {kryptis} {sk(abs(pokytis), False)} proc. punkto; "
                                 f"ES vidurkis – {sk(es.iloc[-1], False)} %.",
                                 f"In {metai}, {sk(pask, False)}% of municipal waste was recycled ({ankst}: "
                                 f"{sk(pries, False)}%). The share {kryptis} {sk(abs(pokytis), False)} percentage points; "
                                 f"the EU average is {sk(es.iloc[-1], False)}%."),
        sparkline=lt[lt.index >= nuo],
        grafikai=[f1],
        apibrezimas=t("Perdirbtų (įskaitant kompostavimą ir anaerobinį apdorojimą) komunalinių atliekų dalis nuo "
                      "visų susidariusių komunalinių atliekų. ES Atliekų pagrindų direktyva nustato tikslus: "
                      "55 % iki 2025 m., 60 % iki 2030 m., 65 % iki 2035 m.",
                      "Share of municipal waste recycled (including composting and anaerobic digestion) in all "
                      "municipal waste generated. The EU Waste Framework Directive sets targets of 55% by 2025, 60% by "
                      "2030 and 65% by 2035."),
        pastabos=[t("Nuo 2020 m. ES taiko griežtesnę perdirbimo skaičiavimo metodiką, todėl ankstesni metai nėra "
                    "visiškai palyginami.",
                    "Since 2020 the EU has applied a stricter recycling calculation method, so earlier years are not "
                    "fully comparable.")],
        saltiniai=[("Eurostat – sdg_11_60", "https://ec.europa.eu/eurostat/databrowser/view/sdg_11_60/default/table?lang=en")],
        papildomai=[(f"{sk(55 - pask, False)}{vnt_pp()}", t("iki ES 2025 m. tikslo (55 %)", "short of the EU 2025 target (55%)"))] if pask < 55 else [],
        lentele=lentele,
    )
