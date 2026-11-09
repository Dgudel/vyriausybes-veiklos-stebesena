"""1. Skurdas: skurdo rizikos lygis + atskirtis, nepriteklius, išmokų poveikis, socialinės išlaidos."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius
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
    linijos(f1, [("Lietuva", lt[lt.index >= nuo], SERIJOS[0]), ("ES-27", es[es.index >= nuo], SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f1, "Skurdo rizikos lygis", "Gyventojų, kurių pajamos mažesnės nei 60 % medianos, dalis, %",
            "Šaltinis: Eurostat, ilc_li02 (EU-SILC)", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    linijos(f2, [("Skurdo ar atskirties rizika – Lietuva", arope_lt, SERIJOS[0]),
                 ("Skurdo ar atskirties rizika – ES-27", arope_es, SERIJOS[1]),
                 ("Didelis nepriteklius – Lietuva", nep_lt, SERIJOS[2]),
                 ("Didelis nepriteklius – ES-27", nep_es, SERIJOS[3])], zenklas=False, zymekliai=True)
    stilius(f2, "Skurdo ar socialinės atskirties rizika ir nepriteklius", "% gyventojų",
            "Šaltinis: Eurostat, ilc_peps01n ir ilc_mdsd11", nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    f3 = go.Figure()
    linijos(f3, [("Lietuva", poveikis_lt[poveikis_lt.index >= nuo], SERIJOS[0]),
                 ("ES-27", poveikis_es[poveikis_es.index >= nuo], SERIJOS[1])], zenklas=False, zymekliai=True)
    stilius(f3, "Kiek socialinės išmokos sumažina skurdą",
            "Skurdo rizikos sumažėjimas dėl išmokų (be pensijų), % nuo skurdo lygio prieš išmokas",
            "Šaltinis: Eurostat, ilc_li02 ir ilc_li10; skaičiavimas", nulio_linija=False, metiniai=True)
    f3.update_yaxes(rangemode="tozero")

    f4 = go.Figure()
    linijos(f4, [("Lietuva", isl_lt, SERIJOS[0]), ("ES-27", isl_es, SERIJOS[1])], vnt="", zenklas=False,
            zymekliai=True, dec=0)
    stilius(f4, "Socialinės apsaugos išlaidos vienam gyventojui",
            "Perkamosios galios standartu (PGS), per metus", "Šaltinis: Eurostat, tps00100",
            vnt="", nulio_linija=False, metiniai=True)
    f4.update_yaxes(rangemode="tozero", tickformat=",.0f")
    f4.update_layout(separators=", ")

    lentele = pd.DataFrame({"LT_skurdo_rizika_proc": lt, "ES27_skurdo_rizika_proc": es,
                            "LT_skurdas_pries_ismokas_proc": pries_lt, "LT_ismoku_poveikis_proc": poveikis_lt,
                            "LT_AROPE_proc": arope_lt, "LT_nepriteklius_proc": nep_lt,
                            "LT_soc_islaidos_PGS_gyv": isl_lt, "LT_soc_islaidos_proc_BVP": bvp_lt})
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    _dalys = [dalis("Skurdo ar socialinės atskirties rizika (AROPE)", arope_lt, "mazesne", SLENKSTIS),
              dalis("Didelis materialinis ir socialinis nepriteklius", nep_lt, "mazesne", SLENKSTIS),
              dalis("Kiek išmokos sumažina skurdą", poveikis_lt, "didesne", 1.0),
              dalis("Socialinės išlaidos vienam gyventojui (ES = 100)", isl_proc_es, "didesne", 0, budas="info",
                    vienetai="", dec=0),
              dalis("Socialinės apsaugos išlaidos, % BVP", bvp_lt, "didesne", 0, budas="info")]

    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"
    return Rodiklis(
        dalys=_dalys,
        id="skurdas",
        pavadinimas="Skurdo rizikos lygis",
        trumpas_aprasas="gyventojų, gyvenančių žemiau skurdo rizikos ribos",
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=False,
        vertinimo_taisykle=(f"Gerėja, kai skurdo rizikos lygis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} "
                            f"proc. punkto; prastėja, kai tiek pat padidėja; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. tyrimo duomenimis, žemiau skurdo rizikos ribos gyveno {sk(pask, False)} % "
                                f"gyventojų ({ankst} m. – {sk(pries, False)} %). Dalis {kryptis} "
                                f"{sk(abs(pokytis), False)} proc. punkto; ES vidurkis – {sk(es.iloc[-1], False)} %. "
                                f"Be socialinių išmokų (neskaitant pensijų) skurdo rizika būtų {sk(pries_lt.iloc[-1], False)} %, "
                                f"t. y. išmokos ją sumažina {sk(poveikis_lt.iloc[-1], False, 0)} %."),
        sparkline=lt[lt.index >= nuo],
        grafikai=[f1, f2, f3, f4],
        apibrezimas=("Skurdo rizikos lygis – dalis gyventojų, kurių ekvivalentinės disponuojamosios pajamos (po "
                     "socialinių išmokų) mažesnės nei 60 % šalies medianos. Skurdo ar socialinės atskirties rizika "
                     "(AROPE, ES 2030 m. tikslo rodiklis) papildomai apima didelį nepriteklių ir labai mažą namų ūkio "
                     "darbo intensyvumą."),
        pastabos=["Duomenys gaunami iš Gyventojų pajamų ir gyvenimo sąlygų tyrimo (EU-SILC): metų tyrimas aprašo "
                  "praėjusių metų pajamas, pvz., 2025 m. tyrimas – 2024 m. pajamas.",
                  "Skurdo rizikos lygis yra santykinis: jei visų pajamos auga, bet mažiausios – lėčiau už medianą, "
                  "rodiklis didėja.",
                  "Socialinės apsaugos išlaidos rodomos kaip kontekstas ir nevertinamos: didesnės išlaidos savaime "
                  "nereiškia geresnio rezultato. Rezultatą rodo eilutė „Kiek išmokos sumažina skurdą“."],
        saltiniai=[("Eurostat – ilc_li02", "https://ec.europa.eu/eurostat/databrowser/view/ilc_li02/default/table?lang=en"),
                   ("Eurostat – ilc_li10", "https://ec.europa.eu/eurostat/databrowser/view/ilc_li10/default/table?lang=en"),
                   ("Eurostat – ilc_peps01n", "https://ec.europa.eu/eurostat/databrowser/view/ilc_peps01n/default/table?lang=en"),
                   ("Eurostat – ilc_mdsd11", "https://ec.europa.eu/eurostat/databrowser/view/ilc_mdsd11/default/table?lang=en"),
                   ("Eurostat – tps00100", "https://ec.europa.eu/eurostat/databrowser/view/tps00100/default/table?lang=en")],
        papildomai=[(f"{sk(arope_lt.iloc[-1], False)} %", f"skurdo ar atskirties rizika, {arope_lt.index[-1].year} m."),
                    (f"{sk(poveikis_lt.iloc[-1], False, 0)} %", "tiek skurdą sumažina išmokos")],
        lentele=lentele,
    )
