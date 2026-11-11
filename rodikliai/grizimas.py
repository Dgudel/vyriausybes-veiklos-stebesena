"""6. Emigracija ir grįžtamoji migracija: Lietuvos piliečių grynoji migracija."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, sk, stilius, t, en
from .eurostat_duomenys import serija

SLENKSTIS = 500     # žmonių per metus


def _tukst(v: float, zenklas: bool = False) -> str:
    x = f"{v:+,.0f}" if zenklas else f"{v:,.0f}"
    return (x if en() else x.replace(",", " ")).replace("-", "−")


def rodiklis() -> Rodiklis:
    f = dict(citizen="LT", age="TOTAL", sex="T", agedef="COMPLET", unit="NR")
    isvyko = serija("migr_emi1ctz", "LT", **f)
    grizo = serija("migr_imm1ctz", "LT", **f)
    neto = (grizo - isvyko).dropna()
    pask, pries = neto.iloc[-1], neto.iloc[-2]
    metai, ankst = neto.index[-1].year, neto.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    nuo = "2008-01-01"
    f1 = go.Figure()
    g, i = grizo[grizo.index >= nuo], isvyko[isvyko.index >= nuo]
    GR, IS, GM, TK = t("Grįžo", "Returned"), t("Išvyko", "Emigrated"), t("Grynoji migracija", "Net migration"), t(" tūkst.", "k")
    f1.add_trace(go.Bar(x=g.index, y=g.values / 1000, name=GR, marker_color=SERIJOS[2],
                        hovertemplate=GR + ": %{y:.1f}" + TK + "<extra></extra>"))
    f1.add_trace(go.Bar(x=i.index, y=-i.values / 1000, name=IS, marker_color=SERIJOS[1],
                        hovertemplate=IS + ": %{customdata:.1f}" + TK + "<extra></extra>", customdata=i.values / 1000))
    n = neto[neto.index >= nuo]
    f1.add_trace(go.Scatter(x=n.index, y=n.values / 1000, name=GM, mode="lines+markers",
                            line=dict(color="#0b0b0b", width=2),
                            hovertemplate=GM + ": %{y:+.1f}" + TK + "<extra></extra>"))
    f1.update_layout(barmode="relative")
    stilius(f1, t("Lietuvos piliečių emigracija ir grįžimas", "Emigration and return of Lithuanian citizens"),
            t("Tūkst. žmonių per metus", "Thousands of people per year"),
            "Šaltinis: Eurostat, migr_emi1ctz ir migr_imm1ctz", vnt="", metiniai=True)

    lentele = grizo.rename("grizo_LT_pilieciu").to_frame().join(isvyko.rename("isvyko_LT_pilieciu"))
    lentele["grynoji_migracija"] = lentele.grizo_LT_pilieciu - lentele.isvyko_LT_pilieciu
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = t("pagerėjo", "improved by") if pokytis > 0 else t("pablogėjo", "worsened by")

    _dalys = [dalis(t("Grįžo Lietuvos piliečių", "Lithuanian citizens returning"), grizo, "didesne", 3.0, budas="proc", vienetai="", dec=0),
              dalis(t("Išvyko Lietuvos piliečių", "Lithuanian citizens emigrating"), isvyko, "mazesne", 3.0, budas="proc", vienetai="", dec=0)]
    return Rodiklis(
        dalys=_dalys,
        id="emigracija-grizimas",
        pavadinimas=t("Emigracija ir grįžimas", "Emigration and return"),
        trumpas_aprasas=t("Lietuvos piliečių grynoji migracija", "net migration of Lithuanian citizens"),
        reiksme=pask / 1000, vienetai=TK, laikotarpis=str(metai), busena=busena,
        zenklas=True, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai Lietuvos piliečių grynoji migracija (grįžusieji minus išvykusieji) per metus "
                             f"padidėja daugiau nei {_tukst(SLENKSTIS)} žmonių; prastėja, kai tiek pat sumažėja; "
                             f"kitu atveju – stabilu.",
                             f"Improving when net migration of Lithuanian citizens (returning minus emigrating) rises by "
                             f"more than {_tukst(SLENKSTIS)} people in a year; worsening when it falls by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. išvykusių Lietuvos piliečių – {_tukst(isvyko.iloc[-1])}, grįžusių – "
                                 f"{_tukst(grizo.iloc[-1])}. Grynoji migracija: {_tukst(pask, True)} ({ankst} m. – "
                                 f"{_tukst(pries, True)}), t. y. {kryptis} {_tukst(abs(pokytis))}.",
                                 f"In {metai}, {_tukst(isvyko.iloc[-1])} Lithuanian citizens emigrated and "
                                 f"{_tukst(grizo.iloc[-1])} returned. Net migration: {_tukst(pask, True)} ({ankst}: "
                                 f"{_tukst(pries, True)}), i.e. it {kryptis} {_tukst(abs(pokytis))}."),
        sparkline=neto[neto.index >= nuo] / 1000,
        grafikai=[f1],
        apibrezimas=t("Į Lietuvą gyventi grįžusių ir iš jos emigravusių Lietuvos piliečių skaičiaus skirtumas. "
                      "Teigiama reikšmė reiškia, kad grįžta daugiau piliečių nei išvyksta.",
                      "Difference between the number of Lithuanian citizens returning to live in Lithuania and those "
                      "emigrating. A positive value means more citizens return than leave."),
        pastabos=[t("Emigracija apskaičiuojama pagal išvykimo deklaravimą; nedeklaravusieji išvykimo į statistiką "
                    "patenka vėliau, kai nustatoma, kad jie šalyje nebegyvena.",
                    "Emigration is based on declarations of departure; those who do not declare departure enter the "
                    "statistics later, once it is established that they no longer live in the country.")],
        saltiniai=[("Eurostat – migr_emi1ctz", "https://ec.europa.eu/eurostat/databrowser/view/migr_emi1ctz/default/table?lang=en"),
                   ("Eurostat – migr_imm1ctz", "https://ec.europa.eu/eurostat/databrowser/view/migr_imm1ctz/default/table?lang=en")],
        papildomai=[(_tukst(grizo.iloc[-1]), t(f"grįžo {metai} m.", f"returned in {metai}")),
                    (_tukst(isvyko.iloc[-1]), t(f"išvyko {metai} m.", f"emigrated in {metai}"))],
        lentele=lentele,
    )
