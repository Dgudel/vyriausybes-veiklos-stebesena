"""5. Migracijos valdymas: imigrantai pagal pilietybę ir prieglobsčio prašymai (informacinis rodiklis)."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, linijos, sk, stilius
from .eurostat_duomenys import lentele, serija, PERIODAS, _data


def _tukst(v: float) -> str:
    return f"{v:,.0f}".replace(",", " ")


def _pilietybe(kodas: str) -> pd.Series:
    return serija("migr_imm1ctz", "LT", citizen=kodas, age="TOTAL", sex="T", agedef="COMPLET", unit="NR")


def rodiklis() -> Rodiklis:
    viso, lt, ua, by = (_pilietybe(k) for k in ["TOTAL", "LT", "UA", "BY"])
    kiti = viso - lt - ua - by
    nuo = "2012-01-01"
    pask, pries = viso.iloc[-1], viso.iloc[-2]
    metai, ankst = viso.index[-1].year, viso.index[-2].year
    pokytis = (pask / pries - 1) * 100
    grizo = lt.iloc[-1]

    f1 = go.Figure()
    grupes = [("Grįžtantys Lietuvos piliečiai", lt), ("Ukrainos piliečiai", ua),
              ("Baltarusijos piliečiai", by), ("Kitų šalių piliečiai", kiti)]
    for i, (vardas, s) in enumerate(grupes):
        s = s[s.index >= nuo]
        f1.add_trace(go.Bar(x=s.index, y=s.values / 1000, name=vardas, marker_color=SERIJOS[i],
                            marker_line=dict(color="white", width=1),
                            hovertemplate=f"{vardas}: %{{y:.1f}} tūkst.<extra></extra>"))
    f1.update_layout(barmode="stack")
    stilius(f1, "Imigrantai pagal pilietybę", "Atvykusių gyventi į Lietuvą asmenų skaičius per metus, tūkst.",
            "Šaltinis: Eurostat, migr_imm1ctz", vnt="", nulio_linija=False, metiniai=True)

    # Prieglobsčio prašymai (pirmą kartą), mėnesiniai
    a = lentele("migr_asyappctzm")
    m = (a["geo"] == "LT") & (a["citizen"] == "TOTAL") & (a["applicant"] == "FRST")
    for k, v in {"sex": "T", "age": "TOTAL", "unit": "PER"}.items():
        if k in a.columns:
            m &= a[k] == v
    periodai = [c for c in a.columns if PERIODAS.match(str(c))]
    prasymai = pd.to_numeric(a[m][periodai].iloc[0], errors="coerce").dropna()
    prasymai.index = [_data(p) for p in prasymai.index]
    prasymai = prasymai.sort_index()
    p12 = prasymai.iloc[-12:].sum()
    p12_pries = prasymai.iloc[-24:-12].sum()
    pask_men = prasymai.index[-1]

    f2 = go.Figure()
    rodomi = prasymai[prasymai.index >= "2019-01-01"]
    f2.add_trace(go.Bar(x=rodomi.index, y=rodomi.values, name="Prašymai per mėnesį", marker_color=SERIJOS[0],
                        hovertemplate="%{x|%Y-%m}: %{y:.0f}<extra></extra>"))
    stilius(f2, "Prieglobsčio prašymai", "Pirmą kartą pateikti prašymai Lietuvoje per mėnesį",
            "Šaltinis: Eurostat, migr_asyappctzm", vnt="", nulio_linija=False)
    f2.update_layout(showlegend=False)

    lentele_df = (viso.rename("imigrantai_is_viso").to_frame().join(lt.rename("Lietuvos_piliečiai"))
                  .join(ua.rename("Ukrainos_piliečiai")).join(by.rename("Baltarusijos_piliečiai"))
                  .join(kiti.rename("kitų_šalių_piliečiai")))
    lentele_df = lentele_df[lentele_df.index >= nuo]
    lentele_df.insert(0, "metai", lentele_df.index.year)

    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"
    men_pav = f"{pask_men.year}-{pask_men.month:02d}"
    return Rodiklis(
        id="imigracija",
        pavadinimas="Imigracija",
        trumpas_aprasas="atvykusių gyventi per metus",
        reiksme=pask / 1000, vienetai=" tūkst.", laikotarpis=str(metai), busena="info",
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=("Informacinis rodiklis: imigracijos mastas savaime nevertinamas kaip gerėjimas ar "
                            "prastėjimas, todėl būsena nenustatoma. Stebima, kiek ir kas atvyksta, bei prieglobsčio "
                            "prašymų dinamika."),
        vertinimo_paaiskinimas=(f"{metai} m. imigrantų skaičius – {_tukst(pask)} ({ankst} m. – "
                                f"{_tukst(pries)}); imigracija {kryptis} {sk(abs(pokytis), False)} %. "
                                f"Iš jų {_tukst(grizo)} – grįžtantys Lietuvos piliečiai ({sk(grizo / pask * 100, False, 0)} %). "
                                f"Pirmų prieglobsčio prašymų per 12 mėn. iki {men_pav} – {_tukst(p12)} "
                                f"(ankstesniais 12 mėn. – {_tukst(p12_pries)})."),
        sparkline=viso[viso.index >= nuo] / 1000,
        grafikai=[f1, f2],
        apibrezimas=("Imigrantai – asmenys, atvykę gyventi į Lietuvą bent 12 mėnesių (deklaravę gyvenamąją vietą), "
                     "pagal pilietybę. Prieglobsčio prašymai – pirmą kartą Lietuvoje pateikti tarptautinės "
                     "apsaugos prašymai."),
        pastabos=["2022 m. šuolį lėmė karo pabėgėliai iš Ukrainos.",
                  "Metiniai imigracijos duomenys skelbiami su maždaug metų vėlavimu, prieglobsčio – kas mėnesį."],
        saltiniai=[("Eurostat – migr_imm1ctz", "https://ec.europa.eu/eurostat/databrowser/view/migr_imm1ctz/default/table?lang=en"),
                   ("Eurostat – migr_asyappctzm", "https://ec.europa.eu/eurostat/databrowser/view/migr_asyappctzm/default/table?lang=en")],
        papildomai=[(_tukst(grizo), f"grįžo Lietuvos piliečių, {metai} m."),
                    (_tukst(p12), f"prieglobsčio prašymų per 12 mėn. iki {men_pav}")],
        lentele=lentele_df,
    )
