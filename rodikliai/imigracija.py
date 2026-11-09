"""6. Imigracija ir grynoji migracija (informacinis rodiklis)."""
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

    # Grynoji tarptautinė migracija (visi asmenys)
    neto = serija("demo_gind", "LT", indic_de="CNMIGRAT")
    neto = neto[neto.index >= "2000-01-01"]
    f2 = go.Figure()
    f2.add_trace(go.Bar(x=neto.index, y=neto.values / 1000, name="Grynoji migracija",
                        marker_color=[SERIJOS[2] if v >= 0 else SERIJOS[1] for v in neto.values],
                        hovertemplate="%{x|%Y}: %{y:+.1f} tūkst.<extra></extra>"))
    stilius(f2, "Grynoji tarptautinė migracija", "Atvykusieji minus išvykusieji, tūkst. per metus",
            "Šaltinis: Eurostat, demo_gind", vnt="", metiniai=True)
    f2.update_layout(showlegend=False)

    lentele_df = (viso.rename("imigrantai_is_viso").to_frame().join(lt.rename("Lietuvos_piliečiai"))
                  .join(ua.rename("Ukrainos_piliečiai")).join(by.rename("Baltarusijos_piliečiai"))
                  .join(kiti.rename("kitų_šalių_piliečiai")))
    lentele_df = lentele_df[lentele_df.index >= nuo]
    lentele_df.insert(0, "metai", lentele_df.index.year)

    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"
    return Rodiklis(
        id="imigracija",
        pavadinimas="Imigracija",
        trumpas_aprasas="atvykusių gyventi per metus",
        reiksme=pask / 1000, vienetai=" tūkst.", laikotarpis=str(metai), busena="info",
        zenklas=False, spark_nuo_nulio=True,
        palyginimas="nevertinama",
        vertinimo_taisykle=("Informacinis rodiklis: imigracijos mastas savaime nevertinamas kaip gerėjimas ar "
                            "prastėjimas, todėl būsena nenustatoma. Stebima, kiek ir kas atvyksta, ir grynoji migracija."),
        vertinimo_paaiskinimas=(f"{metai} m. imigrantų skaičius – {_tukst(pask)} ({ankst} m. – "
                                f"{_tukst(pries)}); imigracija {kryptis} {sk(abs(pokytis), False)} %. "
                                f"Iš jų {_tukst(grizo)} – grįžtantys Lietuvos piliečiai ({sk(grizo / pask * 100, False, 0)} %). "
                                f"Grynoji tarptautinė migracija – {_tukst(neto.iloc[-1]).replace('-', '−')} "
                                f"({neto.index[-1].year} m.)."),
        sparkline=viso[viso.index >= nuo] / 1000,
        grafikai=[f1, f2],
        apibrezimas=("Imigrantai – asmenys, atvykę gyventi į Lietuvą bent 12 mėnesių (deklaravę gyvenamąją vietą), "
                     "pagal pilietybę. Prieglobsčio prašymai – pirmą kartą Lietuvoje pateikti tarptautinės "
                     "apsaugos prašymai."),
        pastabos=["2022 m. šuolį lėmė karo pabėgėliai iš Ukrainos.",
                  "Duomenys skelbiami su maždaug metų vėlavimu. Prieglobsčio prašymai ir neteisėta migracija "
                  "rodomi 5 srityje („Neteisėtos migracijos valdymas“)."],
        saltiniai=[("Eurostat – migr_imm1ctz", "https://ec.europa.eu/eurostat/databrowser/view/migr_imm1ctz/default/table?lang=en"),
                   ("Eurostat – demo_gind", "https://ec.europa.eu/eurostat/databrowser/view/demo_gind/default/table?lang=en")],
        papildomai=[(_tukst(grizo), f"grįžo Lietuvos piliečių, {metai} m."),
                    (_tukst(neto.iloc[-1]).replace("-", "−"), f"grynoji migracija, {neto.index[-1].year} m.")],
        lentele=lentele_df,
    )
