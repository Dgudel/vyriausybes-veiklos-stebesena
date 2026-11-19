"""4. Būsto statyba: per metus pastatyti (baigti statyti) butai 1000 gyventojų (VDA, S8R269)."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, ivertink, linijos, sk, skaityk, stilius, t
from .eurostat_duomenys import serija

LENTELE = "s8r269_m4060403_1_lt"
SLENKSTIS = 0.3     # buto 1000 gyventojų (≈ 850 butų per metus)


def _butai() -> pd.Series:
    d = skaityk(f"{LENTELE}.csv", LENTELE)
    tipas = next(c for c in d.columns if c.startswith("statiniu"))
    d = d[(d.administracine_teritorija == "Lietuvos Respublika") & (d[tipas] == "Gyvenamieji pastatai, iš viso")]
    s = pd.to_numeric(d.set_index("laikotarpis")["s8r269"], errors="coerce").dropna()
    s.index = [pd.Timestamp(int(m), 1, 1) for m in s.index]
    return s.sort_index()


def rodiklis() -> Rodiklis:
    butai = _butai()
    gyv = serija("demo_gind", "LT", indic_de="JAN")           # gyventojai sausio 1 d.
    vid = ((gyv + gyv.shift(-1)) / 2).fillna(gyv)              # metų vidurkis (jei kitų metų dar nėra – sausio 1 d.)
    lt = (butai / vid.reindex(butai.index) * 1000).dropna()
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    f1 = go.Figure()
    linijos(f1, [(t("Pastatyti butai 1000 gyv.", "Dwellings completed per 1,000 inhabitants"), lt, SERIJOS[0])],
            vnt="", zenklas=False, dec=2, zymekliai=True)
    stilius(f1, t("Būsto statyba", "Housing construction"),
            t("Per metus pastatyti (baigti statyti) butai 1000 gyventojų", "Dwellings completed during the year per 1,000 inhabitants"),
            t("Šaltinis: Valstybės duomenų agentūra, S8R269; Eurostat, demo_gind",
              "Source: State Data Agency of Lithuania, S8R269; Eurostat, demo_gind"), vnt="", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    f2.add_trace(go.Bar(x=butai.index, y=butai.values, marker_color=SERIJOS[0], name=t("Butai", "Dwellings"),
                        hovertemplate=t("%{y:,.0f} butų", "%{y:,.0f} dwellings") + "<extra></extra>"))
    stilius(f2, t("Pastatytų butų skaičius", "Number of dwellings completed"), t("Butai per metus", "Dwellings per year"),
            t("Šaltinis: Valstybės duomenų agentūra, S8R269", "Source: State Data Agency of Lithuania, S8R269"),
            vnt="", nulio_linija=False, metiniai=True)

    lentele = butai.rename("pastatyta_butu").to_frame().join(lt.rename("butu_1000_gyv").round(2))
    lentele.insert(0, "metai", lentele.index.year)
    kryptis = t("padidėjo", "rose by") if pokytis > 0 else t("sumažėjo", "fell by")
    return Rodiklis(
        id="busto-statyba",
        pavadinimas=t("Būsto statyba", "Housing construction"),
        trumpas_aprasas=t("pastatyti butai 1000 gyventojų", "dwellings completed per 1,000 inhabitants"),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena, dec=2,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai rodiklis per metus padidėja daugiau nei {sk(SLENKSTIS, False)} buto "
                             f"1000 gyventojų; prastėja, kai tiek pat sumažėja; kitu atveju – stabilu.",
                             f"Improving when the rate rises by more than {sk(SLENKSTIS, False)} dwellings per 1,000 "
                             f"inhabitants in a year; worsening when it falls by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. pastatyta {sk(butai.iloc[-1], False, 0)} butų – {sk(pask, False, 2)} "
                                 f"1000 gyventojų ({ankst} m. – {sk(pries, False, 2)}). Rodiklis {kryptis} "
                                 f"{sk(abs(pokytis), False, 2)} buto 1000 gyventojų.",
                                 f"In {metai}, {sk(butai.iloc[-1], False, 0)} dwellings were completed – {sk(pask, False, 2)} "
                                 f"per 1,000 inhabitants ({ankst}: {sk(pries, False, 2)}). The rate {kryptis} "
                                 f"{sk(abs(pokytis), False, 2)} dwellings per 1,000 inhabitants."),
        sparkline=lt[lt.index >= "2010-01-01"],
        grafikai=[f1, f2],
        apibrezimas=t("Per kalendorinius metus pastatytų (baigtų statyti ir įregistruotų) butų gyvenamuosiuose pastatuose "
                      "skaičius, tenkantis 1000 vidutinio metinio gyventojų skaičiaus.",
                      "Number of dwellings in residential buildings completed (finished and registered) during the "
                      "calendar year per 1,000 of the average annual population."),
        pastabos=[t("Būsto statyba priklauso ir nuo palūkanų normų bei ekonomikos ciklo, todėl Vyriausybės sprendimai "
                    "ją veikia netiesiogiai. Pastatyto būsto ploto (m²) duomenų atviruose šaltiniuose automatiškai "
                    "gauti nepavyko, todėl rodomas butų skaičius.",
                    "Housing construction also depends on interest rates and the business cycle, so government "
                    "decisions affect it indirectly. Data on completed floor area (m²) could not be obtained "
                    "automatically from open sources, so the number of dwellings is shown.")],
        saltiniai=[(t("Lietuvos duomenų portalas – S8R269 (pastatyti butai)", "Lithuanian data portal – S8R269 (dwellings completed)"),
                    "https://osp.stat.gov.lt/statistiniu-rodikliu-analize#/"),
                   ("Eurostat – demo_gind", "https://ec.europa.eu/eurostat/databrowser/view/demo_gind/default/table?lang=en")],
        lentele=lentele,
    )
