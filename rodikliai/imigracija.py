"""6. Imigracija ir grynoji migracija (informacinis rodiklis)."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, linijos, sk, stilius, t, en
from .eurostat_duomenys import lentele, serija, PERIODAS, _data


def _tukst(v: float) -> str:
    return f"{v:,.0f}" if en() else f"{v:,.0f}".replace(",", " ")


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
    TK = t(" tūkst.", "k")
    grupes = [(t("Grįžtantys Lietuvos piliečiai", "Returning Lithuanian citizens"), lt),
              (t("Ukrainos piliečiai", "Ukrainian citizens"), ua),
              (t("Baltarusijos piliečiai", "Belarusian citizens"), by), (t("Kitų šalių piliečiai", "Other citizens"), kiti)]
    for i, (vardas, s) in enumerate(grupes):
        s = s[s.index >= nuo]
        f1.add_trace(go.Bar(x=s.index, y=s.values / 1000, name=vardas, marker_color=SERIJOS[i],
                            marker_line=dict(color="white", width=1),
                            hovertemplate=f"{vardas}: %{{y:.1f}}{TK}<extra></extra>"))
    f1.update_layout(barmode="stack")
    stilius(f1, t("Imigrantai pagal pilietybę", "Immigrants by citizenship"),
            t("Atvykusių gyventi į Lietuvą asmenų skaičius per metus, tūkst.", "Number of people arriving to live in Lithuania per year, thousands"),
            "Šaltinis: Eurostat, migr_imm1ctz", vnt="", nulio_linija=False, metiniai=True)

    # Grynoji tarptautinė migracija (visi asmenys)
    neto = serija("demo_gind", "LT", indic_de="CNMIGRAT")
    neto = neto[neto.index >= "2000-01-01"]
    f2 = go.Figure()
    f2.add_trace(go.Bar(x=neto.index, y=neto.values / 1000, name=t("Grynoji migracija", "Net migration"),
                        marker_color=[SERIJOS[2] if v >= 0 else SERIJOS[1] for v in neto.values],
                        hovertemplate="%{x|%Y}: %{y:+.1f}" + TK + "<extra></extra>"))
    stilius(f2, t("Grynoji tarptautinė migracija", "Net international migration"),
            t("Atvykusieji minus išvykusieji, tūkst. per metus", "Immigrants minus emigrants, thousands per year"),
            "Šaltinis: Eurostat, demo_gind", vnt="", metiniai=True)
    f2.update_layout(showlegend=False)

    lentele_df = (viso.rename("imigrantai_is_viso").to_frame().join(lt.rename("Lietuvos_piliečiai"))
                  .join(ua.rename("Ukrainos_piliečiai")).join(by.rename("Baltarusijos_piliečiai"))
                  .join(kiti.rename("kitų_šalių_piliečiai")))
    lentele_df = lentele_df[lentele_df.index >= nuo]
    lentele_df.insert(0, "metai", lentele_df.index.year)

    kryptis = t("sumažėjo", "fell by") if pokytis < 0 else t("padidėjo", "rose by")

    _dalys = [dalis(t("Grynoji tarptautinė migracija", "Net international migration"), neto, "didesne", 0, budas="info",
                    vienetai="", dec=0, zenklas=True)]
    return Rodiklis(
        dalys=_dalys,
        id="imigracija",
        pavadinimas=t("Imigracija", "Immigration"),
        trumpas_aprasas=t("atvykusių gyventi per metus", "arrivals to live in Lithuania per year"),
        reiksme=pask / 1000, vienetai=TK, laikotarpis=str(metai), busena="info",
        zenklas=False, spark_nuo_nulio=True,
        palyginimas=t("nevertinama", "not assessed"),
        vertinimo_taisykle=t("Informacinis rodiklis: imigracijos mastas savaime nevertinamas kaip gerėjimas ar "
                             "prastėjimas, todėl būsena nenustatoma. Stebima, kiek ir kas atvyksta, ir grynoji migracija.",
                             "Informational indicator: the scale of immigration is not in itself assessed as improving "
                             "or worsening, so no status is set. It monitors how many people arrive, who they are, and net migration."),
        vertinimo_paaiskinimas=t(f"{metai} m. imigrantų skaičius – {_tukst(pask)} ({ankst} m. – "
                                 f"{_tukst(pries)}); imigracija {kryptis} {sk(abs(pokytis), False)} %. "
                                 f"Iš jų {_tukst(grizo)} – grįžtantys Lietuvos piliečiai ({sk(grizo / pask * 100, False, 0)} %). "
                                 f"Grynoji tarptautinė migracija – {_tukst(neto.iloc[-1]).replace('-', '−')} "
                                 f"({neto.index[-1].year} m.).",
                                 f"In {metai}, there were {_tukst(pask)} immigrants ({ankst}: {_tukst(pries)}); "
                                 f"immigration {kryptis} {sk(abs(pokytis), False)}%. Of these, {_tukst(grizo)} were "
                                 f"returning Lithuanian citizens ({sk(grizo / pask * 100, False, 0)}%). Net international "
                                 f"migration was {_tukst(neto.iloc[-1]).replace('-', '−')} ({neto.index[-1].year})."),
        sparkline=viso[viso.index >= nuo] / 1000,
        grafikai=[f1, f2],
        apibrezimas=t("Imigrantai – asmenys, atvykę gyventi į Lietuvą bent 12 mėnesių (deklaravę gyvenamąją vietą), "
                      "pagal pilietybę. Prieglobsčio prašymai – pirmą kartą Lietuvoje pateikti tarptautinės "
                      "apsaugos prašymai.",
                      "Immigrants are people who arrived to live in Lithuania for at least 12 months (having declared "
                      "their place of residence), by citizenship. Asylum applications are first-time applications for "
                      "international protection lodged in Lithuania."),
        pastabos=[t("2022 m. šuolį lėmė karo pabėgėliai iš Ukrainos.", "The jump in 2022 was due to war refugees from Ukraine."),
                  t("Duomenys skelbiami su maždaug metų vėlavimu. Prieglobsčio prašymai ir neteisėta migracija "
                    "rodomi 5 srityje („Neteisėtos migracijos valdymas“).",
                    "Data are published with a delay of about a year. Asylum applications and irregular migration are "
                    "shown in area 5 (“Management of irregular migration”).")],
        saltiniai=[("Eurostat – migr_imm1ctz", "https://ec.europa.eu/eurostat/databrowser/view/migr_imm1ctz/default/table?lang=en"),
                   ("Eurostat – demo_gind", "https://ec.europa.eu/eurostat/databrowser/view/demo_gind/default/table?lang=en")],
        papildomai=[(_tukst(grizo), t(f"grįžo Lietuvos piliečių, {metai} m.", f"Lithuanian citizens returned, {metai}")),
                    (_tukst(neto.iloc[-1]).replace("-", "−"), t(f"grynoji migracija, {neto.index[-1].year} m.", f"net migration, {neto.index[-1].year}"))],
        lentele=lentele_df,
    )
