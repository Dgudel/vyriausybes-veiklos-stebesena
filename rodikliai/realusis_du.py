"""1.1 Realusis darbo užmokestis."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, zmoniu_laikotarpis, t, en
from .saltiniai import SEKTORIAI, du_serija, kainu_pokytis, laikotarpis_is_datos

SEKTORIAI_EN = {"Šalies ūkis": "Whole economy", "Privatusis sektorius": "Private sector",
                "Viešasis sektorius": "Public sector"}


def _sektorius(v: str) -> str:
    return SEKTORIAI_EN.get(v, v) if en() else v
SLENKSTIS = 0.5          # ±0,5 proc. punkto laikoma stabiliu


def rodiklis() -> Rodiklis:
    SALTINIS = t("Šaltinis: Valstybės duomenų agentūra, rodiklis S10R027",
                 "Source: State Data Agency of Lithuania, indicator S10R027")
    real = du_serija("Realusis")
    neto = du_serija("Neto")
    pask = real.iloc[-1]
    laik = laikotarpis_is_datos(real.index[-1])
    busena = ivertink(pask, "didesne", SLENKSTIS)

    # Sukauptas pokytis nuo seniausio turimo to paties mėnesio (grandinė per 12 mėn. žingsnius)
    datos = [d for d in real.index if d.month == real.index[-1].month]
    kaupt = 1.0
    for d in datos:
        kaupt *= 1 + real[d] / 100
    bazes_metai = datos[0].year - 1

    # 1 grafikas – pagal sektorių
    f1 = go.Figure()
    linijos(f1, [(_sektorius(v), du_serija("Realusis", v), SERIJOS[i]) for i, v in enumerate(SEKTORIAI.values())])
    stilius(f1, t("Realusis darbo užmokestis pagal sektorių", "Real wages by sector"),
            t("Metinis pokytis, %: palyginti su praėjusių metų tuo pačiu mėnesiu",
              "Annual change, %: compared with the same month of the previous year"), SALTINIS)

    # 2 grafikas – neto DU ir kainos
    kainos = kainu_pokytis("Iš viso, išskyrus tabaką")
    kainos = kainos[(kainos.index >= neto.index.min()) & (kainos.index <= neto.index.max())]
    f2 = go.Figure()
    f2.add_trace(go.Scatter(x=kainos.index, y=kainos.values, mode="lines", line=dict(width=0),
                            hoverinfo="skip", showlegend=False))
    f2.add_trace(go.Scatter(x=neto.index, y=neto.values, mode="lines", line=dict(width=0),
                            fill="tonexty", fillcolor="rgba(42,120,214,0.10)", hoverinfo="skip",
                            name=t("Perkamosios galios pokytis", "Change in purchasing power")))
    linijos(f2, [(t("Neto darbo užmokestis", "Net wages"), neto, SERIJOS[0]),
                 (t("Vartojimo kainos (iš viso, išskyrus tabaką)", "Consumer prices (total excl. tobacco)"),
                  kainos, SERIJOS[1])])
    stilius(f2, t("Atlyginimai ir kainos", "Wages and prices"),
            t("Abu rodikliai – metinis pokytis, %: palyginti su praėjusių metų tuo pačiu mėnesiu",
              "Both – annual change, %: compared with the same month of the previous year"),
            t("Šaltinis: Valstybės duomenų agentūra, rodikliai S10R027 ir S7R329",
              "Source: State Data Agency of Lithuania, indicators S10R027 and S7R329"))

    lentele = (real.rename("realusis_du_metinis_pokytis_proc").to_frame()
               .join(neto.rename("neto_du_metinis_pokytis_proc")).reset_index())
    lentele["laikotarpis"] = lentele["data"].map(laikotarpis_is_datos)


    _dalys = [dalis(t(f"{v}: realusis DU", f"{_sektorius(v)}: real wages"), du_serija("Realusis", v), "didesne", SLENKSTIS, budas="lygis",
                    zenklas=True, slenkscio_vnt=" %") for v in ["Privatusis sektorius", "Viešasis sektorius"]]
    return Rodiklis(
        dalys=_dalys,
        id="realusis-darbo-uzmokestis",
        pavadinimas=t("Realusis darbo užmokestis", "Real wages"),
        trumpas_aprasas=t("per metus, šalies ūkyje", "year on year, whole economy"),
        reiksme=pask, laikotarpis=laik, busena=busena,
        vertinimo_taisykle=t(f"Gerėja, kai realusis darbo užmokestis per metus padidėja daugiau nei "
                             f"{sk(SLENKSTIS, False)} %; prastėja, kai sumažėja daugiau nei {sk(SLENKSTIS, False)} %; "
                             f"kitu atveju – stabilu.",
                             f"Improving when real wages rise by more than {sk(SLENKSTIS, False)}% year on year; "
                             f"worsening when they fall by more than {sk(SLENKSTIS, False)}%; otherwise stable."),
        vertinimo_paaiskinimas=(t(f"{zmoniu_laikotarpis(laik, kada=True)} realusis darbo užmokestis buvo {sk(pask, zenklas=False)} % "
                                  f"didesnis nei prieš metus: neto atlyginimas augo {sk(neto.iloc[-1], zenklas=False)} %, "
                                  f"t. y. greičiau už kainas, todėl perkamoji galia didėjo.",
                                  f"In {zmoniu_laikotarpis(laik)}, real wages were {sk(pask, zenklas=False)}% higher than "
                                  f"a year earlier: net wages grew by {sk(neto.iloc[-1], zenklas=False)}%, i.e. faster "
                                  f"than prices, so purchasing power increased.")
                                if pask > 0 else
                                t(f"{zmoniu_laikotarpis(laik, kada=True)} realusis darbo užmokestis buvo {sk(abs(pask), zenklas=False)} % "
                                  f"mažesnis nei prieš metus: kainos augo greičiau už atlyginimus.",
                                  f"In {zmoniu_laikotarpis(laik)}, real wages were {sk(abs(pask), zenklas=False)}% lower "
                                  f"than a year earlier: prices grew faster than wages.")),
        sparkline=real,
        grafikai=[f1, f2],
        apibrezimas=t("Realusis darbo užmokestis – neto (atskaičius mokesčius) vidutinis darbo užmokestis, "
                      "įvertinus vartojimo kainų pokytį. Rodo, kaip keičiasi atlyginimo perkamoji galia. "
                      "Šalies ūkis – be individualiųjų įmonių.",
                      "Real wages are average net (after-tax) wages adjusted for the change in consumer prices. They "
                      "show how the purchasing power of pay is changing. Whole economy – excluding sole proprietorships."),
        pastabos=[
            t("Duomenys pateikiami kaip indeksas (praėjusių metų tas pats mėnuo = 100); švieslentėje rodomas pokytis = indeksas − 100.",
              "Data are published as an index (same month of the previous year = 100); the dashboard shows the change = index − 100."),
            t("Paskutinių mėnesių duomenys gali būti patikslinti (pažymėti „patikslinti ir perskaičiuoti duomenys“).",
              "Data for the latest months may be revised (marked as “revised and recalculated data”)."),
            t("Grafike „Atlyginimai ir kainos“ naudojama kainų grupė „Iš viso, išskyrus tabaką“, nes pateiktoje lentelėje nėra bendro VKI; "
              "todėl tarpas tarp linijų gali šiek tiek skirtis nuo realiojo DU pokyčio.",
              "The “Wages and prices” chart uses the price group “Total excluding tobacco”, as the source table has no "
              "overall CPI; the gap between the lines may therefore differ slightly from the change in real wages."),
        ],
        saltiniai=[(t("Oficialiosios statistikos portalas – darbo užmokestis", "Official Statistics Portal – wages"),
                    "https://osp.stat.gov.lt/"),
                   (t("Lietuvos atvirų duomenų portalas", "Lithuanian Open Data Portal"), "https://data.gov.lt/")],
        papildomai=[(f"{sk((kaupt - 1) * 100)} %",
                     t(f"realusis DU {zmoniu_laikotarpis(laik, kada=True)}, palyginti su {bazes_metai} m. tuo pačiu mėnesiu",
                       f"real wages in {zmoniu_laikotarpis(laik)} compared with the same month of {bazes_metai}"))],
        lentele=lentele[["laikotarpis", "realusis_du_metinis_pokytis_proc", "neto_du_metinis_pokytis_proc"]],
    )
