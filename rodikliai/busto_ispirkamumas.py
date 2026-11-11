"""1.2 Būsto įperkamumas: ar būstas brangsta greičiau nei auga atlyginimai."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, zmoniu_laikotarpis, t, en, vnt_pp
from .saltiniai import (busto_kainu_indeksai, busto_kainu_pokytis, du_serija, ketvirtinis,
                        ketvirtis_is_datos)

SLENKSTIS = 1.0     # ±1 proc. punktas tarp būsto kainų ir atlyginimų augimo – stabilu
NUO = "2015-01-01"  # nuo kada rodyti ilgąjį būsto kainų grafiką
TER_EN = {"Lietuva": "Lithuania", "Vilniaus m. sav.": "Vilnius city municipality",
          "Kita šalies teritorija": "Rest of the country"}


def _ter(v: str) -> str:
    return TER_EN.get(v, v) if en() else v


def rodiklis() -> Rodiklis:
    kainos = busto_kainu_pokytis("Lietuva")
    neto_q = ketvirtinis(du_serija("Neto"))

    pask = kainos.iloc[-1]
    laik = ketvirtis_is_datos(kainos.index[-1])

    # Vertinimas: paskutinis ketvirtis, už kurį yra ir būsto kainos, ir DU
    bendras = kainos.index.intersection(neto_q.index).max()
    skirtumas = kainos[bendras] - neto_q[bendras]          # >0 – būstas tampa mažiau įperkamas
    busena = ivertink(skirtumas, "mazesne", SLENKSTIS)
    bl = zmoniu_laikotarpis(ketvirtis_is_datos(bendras))

    # Kainų lygio pokytis nuo 2021 m. vidurkio (prieš palūkanų ir kainų šuolį)
    b = busto_kainu_indeksai()
    lyg = b[(b["teritorija"] == "Lietuva") & (b["busto_tipas"] == "Gyvenamieji pastatai, iš viso")
            & (b["islaidu_bustui_kategorijos"] == "Būstų įsigijimas")].set_index("data")["s7r334"].dropna()
    nuo_2021 = (lyg.iloc[-1] / lyg[lyg.index.year == 2021].mean() - 1) * 100
    vilnius = busto_kainu_pokytis("Vilniaus m. sav.")

    # 1 grafikas – būsto kainos ir atlyginimai (ketvirčiais)
    k1 = kainos[kainos.index >= neto_q.index.min()]
    f1 = go.Figure()
    f1.add_trace(go.Scatter(x=neto_q.index, y=neto_q.values, mode="lines", line=dict(width=0),
                            hoverinfo="skip", showlegend=False))
    f1.add_trace(go.Scatter(x=k1.index, y=k1.reindex(neto_q.index).values, mode="lines", line=dict(width=0),
                            fill="tonexty", fillcolor="rgba(235,104,52,0.10)", hoverinfo="skip",
                            name=t("Skirtumas", "Gap")))
    linijos(f1, [(t("Būsto kainos", "House prices"), k1, SERIJOS[1]),
                 (t("Neto darbo užmokestis (ketvirčio vidurkis)", "Net wages (quarterly average)"), neto_q, SERIJOS[0])])
    stilius(f1, t("Būsto kainos ir atlyginimai", "House prices and wages"),
            t("Abu rodikliai – metinis pokytis, %: palyginti su praėjusių metų tuo pačiu ketvirčiu",
              "Both – annual change, %: compared with the same quarter of the previous year"),
            t("Šaltinis: Valstybės duomenų agentūra, rodikliai S7R334 ir S10R027",
              "Source: State Data Agency of Lithuania, indicators S7R334 and S10R027"))

    # 2 grafikas – būsto kainos pagal teritoriją, ilgesnis laikotarpis
    f2 = go.Figure()
    linijos(f2, [(_ter(tr), busto_kainu_pokytis(tr)[lambda s: s.index >= NUO], SERIJOS[i])
                 for i, tr in enumerate(["Lietuva", "Vilniaus m. sav.", "Kita šalies teritorija"])])
    stilius(f2, t("Būsto kainos pagal teritoriją", "House prices by area"),
            t("Metinis pokytis, %: palyginti su praėjusių metų tuo pačiu ketvirčiu",
              "Annual change, %: compared with the same quarter of the previous year"),
            t("Šaltinis: Valstybės duomenų agentūra, rodiklis S7R334",
              "Source: State Data Agency of Lithuania, indicator S7R334"))
    f2.update_xaxes(tickformat="%Y")

    lentele = (kainos.rename("busto_kainu_metinis_pokytis_proc").to_frame()
               .join(vilnius.rename("busto_kainu_vilniuje_metinis_pokytis_proc"))
               .join(neto_q.rename("neto_du_metinis_pokytis_ketv_vidurkis_proc")).reset_index())
    lentele["laikotarpis"] = lentele["data"].map(ketvirtis_is_datos)

    kryptis = t("greičiau", "faster") if skirtumas > 0 else t("lėčiau", "more slowly")

    _dalys = []
    for tr in ["Vilniaus m. sav.", "Kita šalies teritorija"]:
        kt = busto_kainu_pokytis(tr)
        sk_ = (kt - neto_q).dropna()
        _dalys.append(dalis(t(f"{tr}: kainų ir atlyginimų augimo skirtumas", f"{_ter(tr)}: gap between price and wage growth"),
                            sk_, "mazesne", SLENKSTIS, budas="lygis", zenklas=True, vienetai=vnt_pp()))
        _dalys[-1].pokytis = t(f"kainos {sk(kt[sk_.index[-1]])} %, atlyginimai {sk(neto_q[sk_.index[-1]])} %",
                               f"prices {sk(kt[sk_.index[-1]])}%, wages {sk(neto_q[sk_.index[-1]])}%")
    return Rodiklis(
        dalys=_dalys,
        id="busto-ispirkamumas",
        pavadinimas=t("Būsto įperkamumas", "Housing affordability"),
        trumpas_aprasas=t("būsto kainos per metus", "house prices, year on year"),
        reiksme=pask, laikotarpis=laik, busena=busena,
        vertinimo_taisykle=t("Vertinama, ar būstas brangsta greičiau nei auga neto atlyginimai. "
                             f"Gerėja, kai būsto kainos auga daugiau nei {sk(SLENKSTIS, False)} proc. punkto lėčiau už atlyginimus; "
                             f"prastėja, kai daugiau nei {sk(SLENKSTIS, False)} proc. punkto greičiau; kitu atveju – stabilu.",
                             "Assesses whether housing is becoming more expensive faster than net wages are rising. "
                             f"Improving when house prices grow more than {sk(SLENKSTIS, False)} percentage point slower "
                             f"than wages; worsening when more than {sk(SLENKSTIS, False)} percentage point faster; "
                             f"otherwise stable."),
        vertinimo_paaiskinimas=t(f"{bl} būsto kainos per metus pakito {sk(kainos[bendras])} %, "
                                 f"o neto atlyginimai – {sk(neto_q[bendras])} %. Būstas brango {kryptis} "
                                 f"nei augo atlyginimai (skirtumas {sk(skirtumas)} proc. punkto).",
                                 f"In {bl}, house prices changed by {sk(kainos[bendras])}% year on year and net wages "
                                 f"by {sk(neto_q[bendras])}%. Housing became more expensive {kryptis} than wages grew "
                                 f"(gap of {sk(skirtumas)} percentage points)."),
        sparkline=kainos[kainos.index >= NUO],
        grafikai=[f1, f2],
        apibrezimas=t("Būsto kainų indeksas rodo gyventojų įsigyjamo būsto (naujos ir ankstesnės statybos, "
                      "butų ir namų) kainų pokytį. Įperkamumas vertinamas lyginant būsto kainų augimą su "
                      "neto darbo užmokesčio augimu.",
                      "The house price index shows the change in prices of dwellings purchased by households (new and "
                      "existing, flats and houses). Affordability is assessed by comparing house price growth with "
                      "net wage growth."),
        pastabos=[
            t("Būsto kainų duomenys pateikiami kaip lygio indeksas (2025 m. = 100) ketvirčiais; metinis pokytis "
              "apskaičiuotas lyginant su tuo pačiu ketvirčiu prieš metus.",
              "House price data are a quarterly level index (2025 = 100); the annual change is calculated against "
              "the same quarter a year earlier."),
            t("Darbo užmokestis skelbiamas mėnesiais, todėl palyginimui naudojamas trijų ketvirčio mėnesių "
              "metinio pokyčio vidurkis (apytikslis dydis).",
              "Wages are published monthly, so the comparison uses the average annual change over the three months "
              "of the quarter (an approximation)."),
            t("Rodiklis neįvertina būsto paskolų palūkanų; pilnesniam įperkamumo vertinimui reikėtų kainų, "
              "pajamų ir paskolos įmokos santykio.",
              "The indicator does not take mortgage interest rates into account; a fuller affordability measure "
              "would need the ratio of prices, income and loan repayments."),
            t("Papildomas rodiklis iš dokumento – būsto išlaidų našta (Eurostat ilc_lvho07a) – rodo gyvenimo būste naštą, "
              "o ne pirkimo įperkamumą.",
              "A related indicator – housing cost overburden (Eurostat ilc_lvho07a) – reflects the burden of living "
              "costs rather than the affordability of buying."),
        ],
        saltiniai=[(t("Lietuvos atvirų duomenų portalas – būsto kainų indeksai",
                      "Lithuanian Open Data Portal – house price indices"), "https://data.gov.lt/"),
                   (t("Oficialiosios statistikos portalas", "Official Statistics Portal"), "https://osp.stat.gov.lt/"),
                   ("Eurostat – ilc_lvho07a",
                    "https://ec.europa.eu/eurostat/databrowser/view/ilc_lvho07a/default/table")],
        papildomai=[(f"{sk(nuo_2021)} %", t(f"būsto kainų lygis {zmoniu_laikotarpis(laik)}, palyginti su 2021 m. vidurkiu",
                                            f"house price level in {zmoniu_laikotarpis(laik)} compared with the 2021 average")),
                    (f"{sk(vilnius.iloc[-1])} %", t(f"būsto kainų metinis pokytis Vilniaus m. sav., "
                                                    f"{zmoniu_laikotarpis(ketvirtis_is_datos(vilnius.index[-1]))}",
                                                    f"annual change in house prices, Vilnius city municipality, "
                                                    f"{zmoniu_laikotarpis(ketvirtis_is_datos(vilnius.index[-1]))}"))],
        lentele=lentele[["laikotarpis", "busto_kainu_metinis_pokytis_proc",
                         "busto_kainu_vilniuje_metinis_pokytis_proc", "neto_du_metinis_pokytis_ketv_vidurkis_proc"]],
    )
