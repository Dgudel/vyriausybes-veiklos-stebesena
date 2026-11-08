"""6. Emigracija ir grįžtamoji migracija: Lietuvos piliečių grynoji migracija."""
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, ivertink, sk, stilius
from .eurostat_duomenys import serija

SLENKSTIS = 500     # žmonių per metus


def _tukst(v: float, zenklas: bool = False) -> str:
    return (f"{v:+,.0f}" if zenklas else f"{v:,.0f}").replace(",", " ").replace("-", "−")


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
    f1.add_trace(go.Bar(x=g.index, y=g.values / 1000, name="Grįžo", marker_color=SERIJOS[2],
                        hovertemplate="Grįžo: %{y:.1f} tūkst.<extra></extra>"))
    f1.add_trace(go.Bar(x=i.index, y=-i.values / 1000, name="Išvyko", marker_color=SERIJOS[1],
                        hovertemplate="Išvyko: %{customdata:.1f} tūkst.<extra></extra>", customdata=i.values / 1000))
    n = neto[neto.index >= nuo]
    f1.add_trace(go.Scatter(x=n.index, y=n.values / 1000, name="Grynoji migracija", mode="lines+markers",
                            line=dict(color="#0b0b0b", width=2),
                            hovertemplate="Grynoji migracija: %{y:+.1f} tūkst.<extra></extra>"))
    f1.update_layout(barmode="relative")
    stilius(f1, "Lietuvos piliečių emigracija ir grįžimas", "Tūkst. žmonių per metus",
            "Šaltinis: Eurostat, migr_emi1ctz ir migr_imm1ctz", vnt="", metiniai=True)

    lentele = grizo.rename("grizo_LT_pilieciu").to_frame().join(isvyko.rename("isvyko_LT_pilieciu"))
    lentele["grynoji_migracija"] = lentele.grizo_LT_pilieciu - lentele.isvyko_LT_pilieciu
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = "pagerėjo" if pokytis > 0 else "pablogėjo"
    return Rodiklis(
        id="emigracija-grizimas",
        pavadinimas="Emigracija ir grįžimas",
        trumpas_aprasas="Lietuvos piliečių grynoji migracija",
        reiksme=pask / 1000, vienetai=" tūkst.", laikotarpis=str(metai), busena=busena,
        zenklas=True, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai Lietuvos piliečių grynoji migracija (grįžusieji minus išvykusieji) per metus "
                            f"padidėja daugiau nei {_tukst(SLENKSTIS)} žmonių; prastėja, kai tiek pat sumažėja; "
                            f"kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. išvykusių Lietuvos piliečių – {_tukst(isvyko.iloc[-1])}, grįžusių – "
                                f"{_tukst(grizo.iloc[-1])}. Grynoji migracija: {_tukst(pask, True)} ({ankst} m. – "
                                f"{_tukst(pries, True)}), t. y. {kryptis} {_tukst(abs(pokytis))}."),
        sparkline=neto[neto.index >= nuo] / 1000,
        grafikai=[f1],
        apibrezimas=("Į Lietuvą gyventi grįžusių ir iš jos emigravusių Lietuvos piliečių skaičiaus skirtumas. "
                     "Teigiama reikšmė reiškia, kad grįžta daugiau piliečių nei išvyksta."),
        pastabos=["Emigracija apskaičiuojama pagal išvykimo deklaravimą; nedeklaravusieji išvykimo į statistiką "
                  "patenka vėliau, kai nustatoma, kad jie šalyje nebegyvena."],
        saltiniai=[("Eurostat – migr_emi1ctz", "https://ec.europa.eu/eurostat/databrowser/view/migr_emi1ctz/default/table?lang=en"),
                   ("Eurostat – migr_imm1ctz", "https://ec.europa.eu/eurostat/databrowser/view/migr_imm1ctz/default/table?lang=en")],
        papildomai=[(_tukst(grizo.iloc[-1]), f"grįžo {metai} m."), (_tukst(isvyko.iloc[-1]), f"išvyko {metai} m.")],
        lentele=lentele,
    )
