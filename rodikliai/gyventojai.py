"""6. Demografija: gyventojų skaičiaus kaita (natūrali kaita + migracija)."""
import plotly.graph_objects as go

from .bendra import dalis, papildomas_grafikas, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, t
from .eurostat_duomenys import serija

SLENKSTIS = 1.0     # ‰ – gyventojų skaičiaus pokytis per metus


def rodiklis() -> Rodiklis:
    g = lambda kodas: serija("demo_gind", "LT", indic_de=kodas)
    pradzia, augimas, natur, migr = g("JAN"), g("GROWRT"), g("NATGROWRT"), g("CNMIGRATRT")
    es_aug = serija("demo_gind", "EU27_2020", indic_de="GROWRT")
    pask, metai = augimas.iloc[-1], augimas.index[-1].year
    # Vertinamas pats kaitos lygis: tvari raida – kai gyventojų nemažėja
    busena = ivertink(pask, "didesne", SLENKSTIS)

    nuo = "1990-01-01"
    f1 = go.Figure()
    pr = pradzia[pradzia.index >= nuo] / 1e6
    linijos(f1, [("Lietuva", pr, SERIJOS[0])], vnt=t(" mln.", " m"), zenklas=False, dec=2, nuo_nulio=False)
    stilius(f1, t("Gyventojų skaičius", "Population"), t("Sausio 1 d., mln.", "On 1 January, millions"), "Šaltinis: Eurostat, demo_gind",
            vnt="", nulio_linija=False, metiniai=True)

    f2 = go.Figure()
    for i, (vardas, s) in enumerate([(t("Natūrali kaita", "Natural change"), natur), (t("Neto migracija", "Net migration"), migr)]):
        s = s[s.index >= nuo]
        f2.add_trace(go.Bar(x=s.index, y=s.values, name=vardas, marker_color=SERIJOS[i + 1],
                            hovertemplate=f"{vardas}: %{{y:+.1f}} ‰<extra></extra>"))
    a = augimas[augimas.index >= nuo]
    bk = t("Bendra kaita", "Total change")
    f2.add_trace(go.Scatter(x=a.index, y=a.values, name=bk, mode="lines+markers",
                            line=dict(color=SERIJOS[0], width=2), marker=dict(size=6),
                            hovertemplate=bk + ": %{y:+.1f} ‰<extra></extra>"))
    f2.update_layout(barmode="relative")
    stilius(f2, t("Kas lemia gyventojų skaičiaus kaitą", "What drives population change"),
            t("1000 gyventojų per metus (‰)", "Per 1,000 inhabitants per year (‰)"),
            "Šaltinis: Eurostat, demo_gind", vnt=" ‰", metiniai=True)

    lentele = (pradzia.rename("LT_gyventojai_sausio_1").to_frame().join(augimas.rename("LT_kaita_promile"))
               .join(natur.rename("LT_naturali_kaita_promile")).join(migr.rename("LT_neto_migracija_promile"))
               .join(es_aug.rename("ES27_kaita_promile")))
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    poz = lambda v: t("augo", "grew") if v > 0 else t("mažėjo", "fell")

    _dalys = [dalis(t("Natūrali kaita (gimę minus mirę)", "Natural change (births minus deaths)"), natur, "didesne", 0.5,
                    vienetai=" ‰", slenkscio_vnt=" ‰", zenklas=True),
              dalis(t("Neto migracija", "Net migration"), migr, "didesne", 0, budas="info", vienetai=" ‰", zenklas=True)]
    gimstamumas = serija("demo_frate", "LT", unit="NR", age="TOTAL", agedef="COMPLET")
    gimstamumas_es = serija("demo_frate", "EU27_2020", unit="NR", age="TOTAL", agedef="COMPLET")
    _dalys.append(dalis(t("Suminis gimstamumo rodiklis (vaikų vienai moteriai)", "Total fertility rate (children per woman)"),
                        gimstamumas, "didesne", 0.03,
                        vienetai="", slenkscio_vnt="", dec=2))
    _r = Rodiklis(
        dalys=_dalys,
        id="gyventoju-kaita",
        pavadinimas=t("Gyventojų skaičiaus kaita", "Population change"),
        trumpas_aprasas=t("1000 gyventojų per metus", "per 1,000 inhabitants per year"),
        reiksme=pask, vienetai="‰", laikotarpis=str(metai), busena=busena,
        zenklas=True, spark_nuo_nulio=True,
        palyginimas=t("vertinamas metinės kaitos dydis", "the size of the annual change is assessed"),
        vertinimo_taisykle=t(f"Vertinamas kaitos lygis: gerėja, kai gyventojų skaičius per metus padidėja daugiau "
                             f"nei {sk(SLENKSTIS, False)} ‰; prastėja, kai sumažėja daugiau nei {sk(SLENKSTIS, False)} ‰; "
                             f"kitu atveju – stabilu.",
                             f"The rate of change is assessed: improving when the population grows by more than "
                             f"{sk(SLENKSTIS, False)} ‰ in a year; worsening when it falls by more than {sk(SLENKSTIS, False)} ‰; "
                             f"otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. gyventojų skaičius {poz(pask)} ({sk(pask)} ‰): natūrali kaita "
                                 f"{sk(natur.iloc[-1])} ‰, neto migracija {sk(migr.iloc[-1])} ‰. "
                                 f"{pradzia.index[-1].year} m. sausio 1 d. Lietuvoje gyveno "
                                 f"{sk(pradzia.iloc[-1] / 1e6, False, 3)} mln. žmonių.",
                                 f"In {metai}, the population {poz(pask)} ({sk(pask)} ‰): natural change "
                                 f"{sk(natur.iloc[-1])} ‰, net migration {sk(migr.iloc[-1])} ‰. On 1 January "
                                 f"{pradzia.index[-1].year}, Lithuania had {sk(pradzia.iloc[-1] / 1e6, False, 3)} million inhabitants."),
        sparkline=augimas[augimas.index >= "2005-01-01"],
        grafikai=[f1, f2],
        apibrezimas=t("Gyventojų skaičiaus pokytis per metus, tenkantis 1000 gyventojų. Jį sudaro natūrali kaita "
                      "(gimusieji minus mirusieji) ir neto migracija (atvykusieji minus išvykusieji, su statistiniu "
                      "patikslinimu).",
                      "Annual change in population per 1,000 inhabitants. It consists of natural change (births minus "
                      "deaths) and net migration (immigrants minus emigrants, including statistical adjustment)."),
        pastabos=[t("2022 m. šuolį lėmė iš Ukrainos atvykę asmenys.", "The jump in 2022 was due to arrivals from Ukraine."),
                  t("Neto migracija Eurostat skaičiuojama kaip likutis, todėl apima ir statistinius patikslinimus.",
                    "Eurostat calculates net migration as a residual, so it also includes statistical adjustments.")],
        saltiniai=[("Eurostat – demo_gind", "https://ec.europa.eu/eurostat/databrowser/view/demo_gind/default/table?lang=en")],
        papildomai=[(t(f"{sk(pradzia.iloc[-1] / 1e6, False, 3)} mln.", f"{sk(pradzia.iloc[-1] / 1e6, False, 3)} million"),
                     t(f"gyventojų {pradzia.index[-1].year} m. sausio 1 d.", f"inhabitants on 1 January {pradzia.index[-1].year}")),
                    (f"{sk(natur.iloc[-1])} ‰", t(f"natūrali kaita, {metai} m.", f"natural change, {metai}"))],
        lentele=lentele,
    )
    _r.grafikai.append(papildomas_grafikas(
        t("Suminis gimstamumo rodiklis", "Total fertility rate"),
        t("Vaikų skaičius, tenkantis vienai moteriai (kartų kaitai reikia ~2,1)", "Number of children per woman (replacement level ~2.1)"),
        "Šaltinis: Eurostat, demo_frate", [("Lietuva", gimstamumas), ("ES-27", gimstamumas_es)], dec=2,
        nuo="1990-01-01"))
    return _r
