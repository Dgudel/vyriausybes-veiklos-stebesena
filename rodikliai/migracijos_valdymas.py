"""5. Migracijos valdymas: įpareigotų išvykti užsieniečių faktinio išsiuntimo dalis + prieglobsčio prašymai."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, ivertink, sk, stilius
from .eurostat_duomenys import PERIODAS, _data, lentele, serija

SLENKSTIS = 2.0     # proc. punkto


def _tukst(v: float) -> str:
    return f"{v:,.0f}".replace(",", " ")


def _prieglobstis() -> pd.Series:
    a = lentele("migr_asyappctzm")
    m = (a["geo"] == "LT") & (a["citizen"] == "TOTAL") & (a["applicant"] == "FRST")
    for k, v in {"sex": "T", "age": "TOTAL", "unit": "PER"}.items():
        if k in a.columns:
            m &= a[k] == v
    periodai = [c for c in a.columns if PERIODAS.match(str(c))]
    s = pd.to_numeric(a[m][periodai].iloc[0], errors="coerce").dropna()
    s.index = [_data(p) for p in s.index]
    return s.sort_index()


def _neteisetai_esantys() -> pd.Series | None:
    """Neteisėtai šalyje nustatyti ne ES piliečiai per metus (migr_eipre). Jei duomenų nėra – None."""
    try:
        d = lentele("migr_eipre")
    except Exception as e:
        print(f"  ⚠ migr_eipre nėra ({e}); grafikas praleidžiamas")
        return None
    m = d["geo"] == "LT"
    for k, v in {"citizen": "TOTAL", "sex": "T", "age": "TOTAL", "unit": "PER",
                 "reason": "TOTAL", "apprehen": "TOTAL"}.items():
        if k in d.columns:
            if v not in set(d[k]):
                print(f"  ⚠ migr_eipre: stulpelyje {k} nėra reikšmės {v}; grafikas praleidžiamas")
                return None
            m &= d[k] == v
    if m.sum() != 1:
        return None
    periodai = [c for c in d.columns if PERIODAS.match(str(c))]
    s = pd.to_numeric(d[m][periodai].iloc[0], errors="coerce").dropna()
    s.index = [_data(p) for p in s.index]
    return s.sort_index()


def rodiklis() -> Rodiklis:
    bendra = dict(citizen="TOTAL", age="TOTAL", sex="T", unit="PER")
    isakyta = serija("migr_eiord", "LT", **bendra)
    issiusta = serija("migr_eirtn", "LT", c_dest="TOTAL", **bendra)
    dalis = (issiusta / isakyta * 100).dropna()
    pask, pries = dalis.iloc[-1], dalis.iloc[-2]
    metai, ankst = dalis.index[-1].year, dalis.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    nuo = "2010-01-01"
    f1 = go.Figure()
    for i, (vardas, s) in enumerate([("Įpareigota išvykti", isakyta), ("Faktiškai išsiųsta", issiusta)]):
        s = s[s.index >= nuo]
        f1.add_trace(go.Bar(x=s.index, y=s.values, name=vardas, marker_color=SERIJOS[i],
                            hovertemplate=f"{vardas}: %{{y:.0f}}<extra></extra>"))
    d = dalis[dalis.index >= nuo]
    f1.add_trace(go.Scatter(x=d.index, y=d.values, name="Išsiųstųjų dalis, %", yaxis="y2", mode="lines+markers",
                            line=dict(color=SERIJOS[2], width=2), hovertemplate="Dalis: %{y:.0f} %<extra></extra>"))
    f1.update_layout(barmode="group")
    stilius(f1, "Įpareigoti išvykti ir išsiųsti užsieniečiai", "Ne ES piliečių skaičius per metus (kairė ašis)",
            "Šaltinis: Eurostat, migr_eiord ir migr_eirtn", vnt="", nulio_linija=False, metiniai=True)
    f1.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105], tickvals=[0, 25, 50, 75, 100],
                                 ticksuffix=" %", showgrid=False, zeroline=False))

    prasymai = _prieglobstis()
    p12, p12_pries, pask_men = prasymai.iloc[-12:].sum(), prasymai.iloc[-24:-12].sum(), prasymai.index[-1]
    f2 = go.Figure()
    r = prasymai[prasymai.index >= "2019-01-01"]
    f2.add_trace(go.Bar(x=r.index, y=r.values, marker_color=SERIJOS[0], name="Prašymai",
                        hovertemplate="%{x|%Y-%m}: %{y:.0f}<extra></extra>"))
    stilius(f2, "Prieglobsčio prašymai", "Pirmą kartą pateikti prašymai Lietuvoje per mėnesį",
            "Šaltinis: Eurostat, migr_asyappctzm", vnt="", nulio_linija=False)
    f2.update_layout(showlegend=False)

    grafikai = [f1, f2]
    nustatyta = _neteisetai_esantys()
    if nustatyta is not None and not nustatyta.empty:
        n = nustatyta[nustatyta.index >= nuo]
        f3 = go.Figure()
        f3.add_trace(go.Bar(x=n.index, y=n.values, marker_color=SERIJOS[1], name="Nustatyta",
                            hovertemplate="%{x|%Y}: %{y:.0f}<extra></extra>"))
        stilius(f3, "Neteisėtai šalyje esantys užsieniečiai",
                "Per metus nustatyta neteisėtai atvykusių ar esančių ne ES piliečių",
                "Šaltinis: Eurostat, migr_eipre", vnt="", nulio_linija=False, metiniai=True)
        f3.update_layout(showlegend=False)
        grafikai.insert(1, f3)

    lentele_df = pd.DataFrame({"ipareigota_isvykti": isakyta, "issiusta": issiusta, "dalis_proc": dalis})
    if nustatyta is not None:
        lentele_df = lentele_df.join(nustatyta.rename("nustatyta_neteisetai_esanciu"), how="outer")
    lentele_df = lentele_df[lentele_df.index >= nuo]
    lentele_df.insert(0, "metai", lentele_df.index.year)

    men_pav = f"{pask_men.year}-{pask_men.month:02d}"
    kryptis = "padidėjo" if pokytis > 0 else "sumažėjo"
    return Rodiklis(
        id="migracijos-valdymas",
        pavadinimas="Neteisėtos migracijos valdymas",
        trumpas_aprasas="įpareigotų išvykti išsiųsta dalis",
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, dec=0, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai išsiųstų užsieniečių dalis per metus padidėja daugiau nei "
                            f"{sk(SLENKSTIS, False, 0)} proc. punktais; prastėja, kai tiek pat sumažėja; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. įpareigotų išvykti ne ES piliečių – {_tukst(isakyta.iloc[-1])}, faktiškai "
                                f"išsiųstų – {_tukst(issiusta.iloc[-1])}, t. y. {sk(pask, False, 0)} % ({ankst} m. – "
                                f"{sk(pries, False, 0)} %). Dalis {kryptis} {sk(abs(pokytis), False, 0)} p. p. "
                                f"Pirmų prieglobsčio prašymų per 12 mėn. iki {men_pav} – {_tukst(p12)} "
                                f"(ankstesniais 12 mėn. – {_tukst(p12_pries)})."),
        sparkline=dalis[dalis.index >= nuo],
        grafikai=grafikai,
        apibrezimas=("Faktiškai iš Lietuvos išsiųstų (grąžintų) ne ES piliečių skaičiaus ir per tuos pačius metus "
                     "įpareigotų išvykti asmenų skaičiaus santykis. ES šį santykį naudoja kaip grąžinimo "
                     "politikos veiksmingumo rodiklį."),
        pastabos=["Išsiųsti asmenys ne visada tie patys, kurie įpareigoti išvykti tais pačiais metais, todėl tai "
                  "santykinis rodiklis.",
                  "2021 m. kritimą lėmė neteisėtos migracijos per Baltarusijos sieną krizė: įpareigotų išvykti "
                  "skaičius staiga išaugo."],
        saltiniai=[("Eurostat – migr_eiord", "https://ec.europa.eu/eurostat/databrowser/view/migr_eiord/default/table?lang=en"),
                   ("Eurostat – migr_eirtn", "https://ec.europa.eu/eurostat/databrowser/view/migr_eirtn/default/table?lang=en"),
                   ("Eurostat – migr_eipre", "https://ec.europa.eu/eurostat/databrowser/view/migr_eipre/default/table?lang=en"),
                   ("Eurostat – migr_asyappctzm", "https://ec.europa.eu/eurostat/databrowser/view/migr_asyappctzm/default/table?lang=en")],
        papildomai=[(_tukst(issiusta.iloc[-1]), f"išsiųsta {metai} m."),
                    (_tukst(p12), f"prieglobsčio prašymų per 12 mėn. iki {men_pav}")],
        lentele=lentele_df,
    )
