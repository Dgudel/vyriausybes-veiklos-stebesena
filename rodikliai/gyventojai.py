"""6. Demografija: gyventojų skaičiaus kaita (natūrali kaita + migracija)."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius
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
    linijos(f1, [("Lietuva", pr, SERIJOS[0])], vnt=" mln.", zenklas=False, dec=2, nuo_nulio=False)
    stilius(f1, "Gyventojų skaičius", "Sausio 1 d., mln.", "Šaltinis: Eurostat, demo_gind",
            vnt="", nulio_linija=False, metiniai=True)

    f2 = go.Figure()
    for i, (vardas, s) in enumerate([("Natūrali kaita", natur), ("Neto migracija", migr)]):
        s = s[s.index >= nuo]
        f2.add_trace(go.Bar(x=s.index, y=s.values, name=vardas, marker_color=SERIJOS[i + 1],
                            hovertemplate=f"{vardas}: %{{y:+.1f}} ‰<extra></extra>"))
    a = augimas[augimas.index >= nuo]
    f2.add_trace(go.Scatter(x=a.index, y=a.values, name="Bendra kaita", mode="lines+markers",
                            line=dict(color=SERIJOS[0], width=2), marker=dict(size=6),
                            hovertemplate="Bendra kaita: %{y:+.1f} ‰<extra></extra>"))
    f2.update_layout(barmode="relative")
    stilius(f2, "Kas lemia gyventojų skaičiaus kaitą", "1000 gyventojų per metus (‰)",
            "Šaltinis: Eurostat, demo_gind", vnt=" ‰", metiniai=True)

    lentele = (pradzia.rename("LT_gyventojai_sausio_1").to_frame().join(augimas.rename("LT_kaita_promile"))
               .join(natur.rename("LT_naturali_kaita_promile")).join(migr.rename("LT_neto_migracija_promile"))
               .join(es_aug.rename("ES27_kaita_promile")))
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    poz = lambda v: "augo" if v > 0 else "mažėjo"

    _dalys = [dalis("Natūrali kaita (gimę minus mirę)", natur, "didesne", 0.5, vienetai=" ‰", slenkscio_vnt=" ‰", zenklas=True),
              dalis("Neto migracija", migr, "didesne", 0, budas="info", vienetai=" ‰", zenklas=True)]
    return Rodiklis(
        dalys=_dalys,
        id="gyventoju-kaita",
        pavadinimas="Gyventojų skaičiaus kaita",
        trumpas_aprasas="1000 gyventojų per metus",
        reiksme=pask, vienetai="‰", laikotarpis=str(metai), busena=busena,
        zenklas=True, spark_nuo_nulio=True,
        palyginimas="vertinamas metinės kaitos dydis",
        vertinimo_taisykle=(f"Vertinamas kaitos lygis: gerėja, kai gyventojų skaičius per metus padidėja daugiau "
                            f"nei {sk(SLENKSTIS, False)} ‰; prastėja, kai sumažėja daugiau nei {sk(SLENKSTIS, False)} ‰; "
                            f"kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. gyventojų skaičius {poz(pask)} ({sk(pask)} ‰): natūrali kaita "
                                f"{sk(natur.iloc[-1])} ‰, neto migracija {sk(migr.iloc[-1])} ‰. "
                                f"{pradzia.index[-1].year} m. sausio 1 d. Lietuvoje gyveno "
                                f"{sk(pradzia.iloc[-1] / 1e6, False, 3)} mln. žmonių."),
        sparkline=augimas[augimas.index >= "2005-01-01"],
        grafikai=[f1, f2],
        apibrezimas=("Gyventojų skaičiaus pokytis per metus, tenkantis 1000 gyventojų. Jį sudaro natūrali kaita "
                     "(gimusieji minus mirusieji) ir neto migracija (atvykusieji minus išvykusieji, su statistiniu "
                     "patikslinimu)."),
        pastabos=["2022 m. šuolį lėmė iš Ukrainos atvykę asmenys.",
                  "Neto migracija Eurostat skaičiuojama kaip likutis, todėl apima ir statistinius patikslinimus."],
        saltiniai=[("Eurostat – demo_gind", "https://ec.europa.eu/eurostat/databrowser/view/demo_gind/default/table?lang=en")],
        papildomai=[(f"{sk(pradzia.iloc[-1] / 1e6, False, 3)} mln.", f"gyventojų {pradzia.index[-1].year} m. sausio 1 d."),
                    (f"{sk(natur.iloc[-1])} ‰", f"natūrali kaita, {metai} m.")],
        lentele=lentele,
    )
