"""1. Skurdas: skurdo rizikos lygis + atskirtis, nepriteklius, išmokų poveikis, socialinės išlaidos."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import dalis, papildomas_grafikas, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, t, en
from .eurostat_duomenys import serija

SLENKSTIS = 0.5     # proc. punkto (EU-SILC apklausa – mažesni pokyčiai gali būti atsitiktiniai)


def _skurdas(lentele: str, geo: str) -> pd.Series:
    f = dict(rskpovth="B_60", statinfo="MED_EI", age="TOTAL", sex="T")
    if lentele == "ilc_li02":
        f["unit"] = "PC"
    return serija(lentele, geo, **f)


def rodiklis() -> Rodiklis:
    lt, es = _skurdas("ilc_li02", "LT"), _skurdas("ilc_li02", "EU27_2020")
    pries_lt, pries_es = _skurdas("ilc_li10", "LT"), _skurdas("ilc_li10", "EU27_2020")
    arope_lt = serija("ilc_peps01n", "LT", unit="PC", age="TOTAL", sex="T")
    arope_es = serija("ilc_peps01n", "EU27_2020", unit="PC", age="TOTAL", sex="T")
    nep_lt = serija("ilc_mdsd11", "LT", unit="PC", age="TOTAL", sex="T")
    nep_es = serija("ilc_mdsd11", "EU27_2020", unit="PC", age="TOTAL", sex="T")
    isl_lt = serija("tps00100", "LT", unit="PPS_HAB", spdeps="TOTAL")
    isl_es = serija("tps00100", "EU27_2020", unit="PPS_HAB", spdeps="TOTAL")
    bvp_lt = serija("tps00098", "LT", unit="PC_GDP", spdeps="TOTAL")
    poveikis_lt = ((pries_lt - lt) / pries_lt * 100).dropna()     # kiek % išmokos sumažina skurdą
    poveikis_es = ((pries_es - es) / pries_es * 100).dropna()
    isl_proc_es = (isl_lt / isl_es * 100).dropna()

    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)

    nuo = "2010-01-01"
    f1 = go.Figure()
    LT, ES = t("Lietuva", "Lithuania"), t("ES-27", "EU-27")
    linijos(f1, [(LT, lt[lt.index >= nuo], SERIJOS[0]), (ES, es[es.index >= nuo], SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f1, t("Skurdo rizikos lygis", "At-risk-of-poverty rate"),
            t("Gyventojų, kurių pajamos mažesnės nei 60 % medianos, dalis, %",
              "Share of people with income below 60% of the median, %"),
            "Šaltinis: Eurostat, ilc_li02 (EU-SILC)".replace("Šaltinis", t("Šaltinis", "Source")),
            nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    ar, nep = t("Skurdo ar atskirties rizika", "At risk of poverty or social exclusion"), t("Didelis nepriteklius", "Severe deprivation")
    linijos(f2, [(f"{ar} – {LT}", arope_lt, SERIJOS[0]),
                 (f"{ar} – {ES}", arope_es, SERIJOS[1]),
                 (f"{nep} – {LT}", nep_lt, SERIJOS[2]),
                 (f"{nep} – {ES}", nep_es, SERIJOS[3])], zenklas=False, zymekliai=True)
    stilius(f2, t("Skurdo ar socialinės atskirties rizika ir nepriteklius", "Risk of poverty or social exclusion and deprivation"),
            t("% gyventojų", "% of population"),
            t("Šaltinis: Eurostat, ilc_peps01n ir ilc_mdsd11", "Source: Eurostat, ilc_peps01n and ilc_mdsd11"),
            nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    f3 = go.Figure()
    linijos(f3, [(LT, poveikis_lt[poveikis_lt.index >= nuo], SERIJOS[0]),
                 (ES, poveikis_es[poveikis_es.index >= nuo], SERIJOS[1])], zenklas=False, zymekliai=True)
    stilius(f3, t("Kiek socialinės išmokos sumažina skurdą", "How much social transfers reduce poverty"),
            t("Skurdo rizikos sumažėjimas dėl išmokų (be pensijų), % nuo skurdo lygio prieš išmokas",
              "Reduction in the poverty risk due to transfers (excl. pensions), % of the pre-transfer rate"),
            t("Šaltinis: Eurostat, ilc_li02 ir ilc_li10; skaičiavimas", "Source: Eurostat, ilc_li02 and ilc_li10; own calculation"),
            nulio_linija=False, metiniai=True)
    f3.update_yaxes(rangemode="tozero")

    f4 = go.Figure()
    linijos(f4, [(LT, isl_lt, SERIJOS[0]), (ES, isl_es, SERIJOS[1])], vnt="", zenklas=False,
            zymekliai=True, dec=0)
    stilius(f4, t("Socialinės apsaugos išlaidos vienam gyventojui", "Social protection expenditure per inhabitant"),
            t("Perkamosios galios standartu (PGS), per metus", "Purchasing power standards (PPS), per year"),
            t("Šaltinis: Eurostat, tps00100", "Source: Eurostat, tps00100"),
            vnt="", nulio_linija=False, metiniai=True)
    f4.update_yaxes(rangemode="tozero", tickformat=",.0f")
    f4.update_layout(separators=".," if en() else ", ")

    lentele = pd.DataFrame({"LT_skurdo_rizika_proc": lt, "ES27_skurdo_rizika_proc": es,
                            "LT_skurdas_pries_ismokas_proc": pries_lt, "LT_ismoku_poveikis_proc": poveikis_lt,
                            "LT_AROPE_proc": arope_lt, "LT_nepriteklius_proc": nep_lt,
                            "LT_soc_islaidos_PGS_gyv": isl_lt, "LT_soc_islaidos_proc_BVP": bvp_lt})
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    _dalys = [dalis(t("Skurdo ar socialinės atskirties rizika (AROPE)", "At risk of poverty or social exclusion (AROPE)"),
                    arope_lt, "mazesne", SLENKSTIS),
              dalis(t("Didelis materialinis ir socialinis nepriteklius", "Severe material and social deprivation"),
                    nep_lt, "mazesne", SLENKSTIS),
              dalis(t("Kiek išmokos sumažina skurdą", "Poverty reduction by social transfers"), poveikis_lt, "didesne", 1.0),
              dalis(t("Socialinės išlaidos vienam gyventojui (ES = 100)", "Social expenditure per inhabitant (EU = 100)"),
                    isl_proc_es, "didesne", 0, budas="info", vienetai="", dec=0),
              dalis(t("Socialinės apsaugos išlaidos, % BVP", "Social protection expenditure, % of GDP"),
                    bvp_lt, "didesne", 0, budas="info")]

    kryptis = t("sumažėjo", "decreased") if pokytis < 0 else t("padidėjo", "increased")
    pensijos = serija("ilc_pnp3", "LT", sex="T", unit="PC")
    pensijos_es = serija("ilc_pnp3", "EU27_2020", sex="T", unit="PC")
    _dalys.append(dalis(t("Pensijų pakankamumas (pensijos / atlyginimai)", "Pension adequacy (pensions / earnings)"),
                        pensijos * 100, "didesne", 1.0))
    _r = Rodiklis(
        dalys=_dalys,
        id="skurdas",
        pavadinimas=t("Skurdo rizikos lygis", "At-risk-of-poverty rate"),
        trumpas_aprasas=t("gyventojų, gyvenančių žemiau skurdo rizikos ribos", "of people living below the poverty threshold"),
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=False,
        vertinimo_taisykle=t(f"Gerėja, kai skurdo rizikos lygis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} "
                             f"proc. punkto; prastėja, kai tiek pat padidėja; kitu atveju – stabilu.",
                             f"Improving when the at-risk-of-poverty rate falls by more than {sk(SLENKSTIS, False)} "
                             f"percentage point in a year; worsening when it rises by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. tyrimo duomenimis, žemiau skurdo rizikos ribos gyveno {sk(pask, False)} % "
                                 f"gyventojų ({ankst} m. – {sk(pries, False)} %). Dalis {kryptis} "
                                 f"{sk(abs(pokytis), False)} proc. punkto; ES vidurkis – {sk(es.iloc[-1], False)} %. "
                                 f"Be socialinių išmokų (neskaitant pensijų) skurdo rizika būtų {sk(pries_lt.iloc[-1], False)} %, "
                                 f"t. y. išmokos ją sumažina {sk(poveikis_lt.iloc[-1], False, 0)} %.",
                                 f"According to the {metai} survey, {sk(pask, False)}% of the population lived below the "
                                 f"poverty threshold ({ankst}: {sk(pries, False)}%). The share {kryptis} by "
                                 f"{sk(abs(pokytis), False)} percentage points; the EU average is {sk(es.iloc[-1], False)}%. "
                                 f"Without social transfers (excluding pensions) the poverty risk would be "
                                 f"{sk(pries_lt.iloc[-1], False)}%, i.e. transfers reduce it by "
                                 f"{sk(poveikis_lt.iloc[-1], False, 0)}%."),
        sparkline=lt[lt.index >= nuo],
        grafikai=[f1, f2, f3, f4],
        apibrezimas=t("Skurdo rizikos lygis – dalis gyventojų, kurių ekvivalentinės disponuojamosios pajamos (po "
                      "socialinių išmokų) mažesnės nei 60 % šalies medianos. Skurdo ar socialinės atskirties rizika "
                      "(AROPE, ES 2030 m. tikslo rodiklis) papildomai apima didelį nepriteklių ir labai mažą namų ūkio "
                      "darbo intensyvumą.",
                      "The at-risk-of-poverty rate is the share of people whose equivalised disposable income (after "
                      "social transfers) is below 60% of the national median. The risk of poverty or social exclusion "
                      "(AROPE, the EU 2030 target indicator) also covers severe deprivation and very low household "
                      "work intensity."),
        pastabos=[t("Duomenys gaunami iš Gyventojų pajamų ir gyvenimo sąlygų tyrimo (EU-SILC): metų tyrimas aprašo "
                    "praėjusių metų pajamas, pvz., 2025 m. tyrimas – 2024 m. pajamas.",
                    "Data come from the Survey on Income and Living Conditions (EU-SILC): each year's survey describes "
                    "the previous year's income, e.g. the 2025 survey covers 2024 income."),
                  t("Skurdo rizikos lygis yra santykinis: jei visų pajamos auga, bet mažiausios – lėčiau už medianą, "
                    "rodiklis didėja.",
                    "The at-risk-of-poverty rate is relative: if everyone's income grows but the lowest incomes grow "
                    "more slowly than the median, the rate rises."),
                  t("Socialinės apsaugos išlaidos rodomos kaip kontekstas ir nevertinamos: didesnės išlaidos savaime "
                    "nereiškia geresnio rezultato. Rezultatą rodo eilutė „Kiek išmokos sumažina skurdą“.",
                    "Social protection expenditure is shown as context and is not assessed: higher spending does not "
                    "in itself mean a better result. The result is shown by “Poverty reduction by social transfers”.")],
        saltiniai=[("Eurostat – ilc_li02", "https://ec.europa.eu/eurostat/databrowser/view/ilc_li02/default/table?lang=en"),
                   ("Eurostat – ilc_li10", "https://ec.europa.eu/eurostat/databrowser/view/ilc_li10/default/table?lang=en"),
                   ("Eurostat – ilc_peps01n", "https://ec.europa.eu/eurostat/databrowser/view/ilc_peps01n/default/table?lang=en"),
                   ("Eurostat – ilc_mdsd11", "https://ec.europa.eu/eurostat/databrowser/view/ilc_mdsd11/default/table?lang=en"),
                   ("Eurostat – tps00100", "https://ec.europa.eu/eurostat/databrowser/view/tps00100/default/table?lang=en")],
        papildomai=[(f"{sk(arope_lt.iloc[-1], False)} %", t(f"skurdo ar atskirties rizika, {arope_lt.index[-1].year} m.",
                                                            f"risk of poverty or social exclusion, {arope_lt.index[-1].year}")),
                    (f"{sk(poveikis_lt.iloc[-1], False, 0)} %", t("tiek skurdą sumažina išmokos",
                                                                  "reduction in poverty due to social transfers"))],
        lentele=lentele,
    )
    _r.grafikai.append(papildomas_grafikas(
        t("Pensijų pakankamumas", "Pension adequacy"),
        t("65–74 m. pensijų medianos ir 50–59 m. darbo pajamų medianos santykis, %",
          "Median pensions of people aged 65–74 relative to median earnings of people aged 50–59, %"),
        t("Šaltinis: Eurostat, ilc_pnp3", "Source: Eurostat, ilc_pnp3"),
        [(LT, pensijos * 100), (ES, pensijos_es * 100)], vnt=" %", dec=0))
    return _r
