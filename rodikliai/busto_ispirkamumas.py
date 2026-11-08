"""1.2 Būsto įperkamumas: ar būstas brangsta greičiau nei auga atlyginimai."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, zmoniu_laikotarpis
from .saltiniai import (busto_kainu_indeksai, busto_kainu_pokytis, du_serija, ketvirtinis,
                        ketvirtis_is_datos)

SLENKSTIS = 1.0     # ±1 proc. punktas tarp būsto kainų ir atlyginimų augimo – stabilu
NUO = "2015-01-01"  # nuo kada rodyti ilgąjį būsto kainų grafiką


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
                            name="Skirtumas"))
    linijos(f1, [("Būsto kainos", k1, SERIJOS[1]),
                 ("Neto darbo užmokestis (ketvirčio vidurkis)", neto_q, SERIJOS[0])])
    stilius(f1, "Būsto kainos ir atlyginimai",
            "Abu rodikliai – metinis pokytis, %: palyginti su praėjusių metų tuo pačiu ketvirčiu",
            "Šaltinis: Valstybės duomenų agentūra, rodikliai S7R334 ir S10R027")

    # 2 grafikas – būsto kainos pagal teritoriją, ilgesnis laikotarpis
    f2 = go.Figure()
    linijos(f2, [(t, busto_kainu_pokytis(t)[lambda s: s.index >= NUO], SERIJOS[i])
                 for i, t in enumerate(["Lietuva", "Vilniaus m. sav.", "Kita šalies teritorija"])])
    stilius(f2, "Būsto kainos pagal teritoriją",
            "Metinis pokytis, %: palyginti su praėjusių metų tuo pačiu ketvirčiu",
            "Šaltinis: Valstybės duomenų agentūra, rodiklis S7R334")
    f2.update_xaxes(tickformat="%Y")

    lentele = (kainos.rename("busto_kainu_metinis_pokytis_proc").to_frame()
               .join(vilnius.rename("busto_kainu_vilniuje_metinis_pokytis_proc"))
               .join(neto_q.rename("neto_du_metinis_pokytis_ketv_vidurkis_proc")).reset_index())
    lentele["laikotarpis"] = lentele["data"].map(ketvirtis_is_datos)

    kryptis = "greičiau" if skirtumas > 0 else "lėčiau"

    _dalys = []
    for t in ["Vilniaus m. sav.", "Kita šalies teritorija"]:
        kt = busto_kainu_pokytis(t)
        sk_ = (kt - neto_q).dropna()
        _dalys.append(dalis(f"{t}: kainų ir atlyginimų augimo skirtumas", sk_, "mazesne", SLENKSTIS, budas="lygis",
                            zenklas=True, vienetai=" p. p."))
        _dalys[-1].pokytis = f"kainos {sk(kt[sk_.index[-1]])} %, atlyginimai {sk(neto_q[sk_.index[-1]])} %"
    return Rodiklis(
        dalys=_dalys,
        id="busto-ispirkamumas",
        pavadinimas="Būsto įperkamumas",
        trumpas_aprasas="būsto kainos per metus",
        reiksme=pask, laikotarpis=laik, busena=busena,
        vertinimo_taisykle=("Vertinama, ar būstas brangsta greičiau nei auga neto atlyginimai. "
                            f"Gerėja, kai būsto kainos auga daugiau nei {sk(SLENKSTIS, False)} proc. punkto lėčiau už atlyginimus; "
                            f"prastėja, kai daugiau nei {sk(SLENKSTIS, False)} proc. punkto greičiau; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{bl} būsto kainos per metus pakito {sk(kainos[bendras])} %, "
                                f"o neto atlyginimai – {sk(neto_q[bendras])} %. Būstas brango {kryptis} "
                                f"nei augo atlyginimai (skirtumas {sk(skirtumas)} proc. punkto)."),
        sparkline=kainos[kainos.index >= NUO],
        grafikai=[f1, f2],
        apibrezimas=("Būsto kainų indeksas rodo gyventojų įsigyjamo būsto (naujos ir ankstesnės statybos, "
                     "butų ir namų) kainų pokytį. Įperkamumas vertinamas lyginant būsto kainų augimą su "
                     "neto darbo užmokesčio augimu."),
        pastabos=[
            "Būsto kainų duomenys pateikiami kaip lygio indeksas (2025 m. = 100) ketvirčiais; metinis pokytis "
            "apskaičiuotas lyginant su tuo pačiu ketvirčiu prieš metus.",
            "Darbo užmokestis skelbiamas mėnesiais, todėl palyginimui naudojamas trijų ketvirčio mėnesių "
            "metinio pokyčio vidurkis (apytikslis dydis).",
            "Rodiklis neįvertina būsto paskolų palūkanų; pilnesniam įperkamumo vertinimui reikėtų kainų, "
            "pajamų ir paskolos įmokos santykio.",
            "Papildomas rodiklis iš dokumento – būsto išlaidų našta (Eurostat ilc_lvho07a) – rodo gyvenimo būste naštą, "
            "o ne pirkimo įperkamumą.",
        ],
        saltiniai=[("Lietuvos atvirų duomenų portalas – būsto kainų indeksai",
                    "https://data.gov.lt/"),
                   ("Oficialiosios statistikos portalas", "https://osp.stat.gov.lt/"),
                   ("Eurostat – ilc_lvho07a",
                    "https://ec.europa.eu/eurostat/databrowser/view/ilc_lvho07a/default/table")],
        papildomai=[(f"{sk(nuo_2021)} %", f"būsto kainų lygis {zmoniu_laikotarpis(laik)}, palyginti su 2021 m. vidurkiu"),
                    (f"{sk(vilnius.iloc[-1])} %", f"būsto kainų metinis pokytis Vilniaus m. sav., "
                                                  f"{zmoniu_laikotarpis(ketvirtis_is_datos(vilnius.index[-1]))}")],
        lentele=lentele[["laikotarpis", "busto_kainu_metinis_pokytis_proc",
                         "busto_kainu_vilniuje_metinis_pokytis_proc", "neto_du_metinis_pokytis_ketv_vidurkis_proc"]],
    )
