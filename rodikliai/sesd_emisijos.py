"""4. Klimatas: šiltnamio efektą sukeliančių dujų (ŠESD) išmetimai."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, t
from .eurostat_duomenys import serija

SLENKSTIS = 1.0     # % per metus


def rodiklis() -> Rodiklis:
    bendri = serija("sdg_13_10", "LT", src_crf="TOTX4_MEMO", unit="MTCO2E")
    grynieji = serija("sdg_13_10", "LT", src_crf="TOTXMEMO", unit="MTCO2E")
    indeksas = serija("sdg_13_10", "LT", src_crf="TOTX4_MEMO", unit="I90")
    vienam = serija("sdg_13_10", "LT", src_crf="TOTX4_MEMO", unit="T_HAB")
    pask, pries = bendri.iloc[-1], bendri.iloc[-2]
    metai, ankst = bendri.index[-1].year, bendri.index[-2].year
    pokytis = (pask / pries - 1) * 100
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)

    f1 = go.Figure()
    linijos(f1, [(t("Išmetimai (be LULUCF)", "Emissions (excl. LULUCF)"), bendri, SERIJOS[0]),
                 (t("Grynieji (su miškais ir žemėnauda)", "Net (incl. forests and land use)"), grynieji, SERIJOS[2])],
            vnt="", zenklas=False, zymekliai=False)
    stilius(f1, t("Šiltnamio efektą sukeliančių dujų išmetimai", "Greenhouse gas emissions"),
            t("Mln. t CO₂ ekvivalento per metus", "Million t CO₂ equivalent per year"),
            t("Šaltinis: Eurostat, sdg_13_10 (EEA nacionalinė ŠESD apskaita)", "Source: Eurostat, sdg_13_10 (EEA national GHG inventory)"), vnt="", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    linijos(f2, [("Lietuva", vienam, SERIJOS[0])], vnt=" t", zenklas=False, zymekliai=False)
    stilius(f2, t("Išmetimai vienam gyventojui", "Emissions per inhabitant"), t("Tonos CO₂ ekvivalento (be LULUCF)", "Tonnes CO₂ equivalent (excl. LULUCF)"),
            "Šaltinis: Eurostat, sdg_13_10", vnt=" t", nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    lentele = (bendri.rename("LT_mln_t_CO2e").to_frame().join(grynieji.rename("LT_grynieji_mln_t_CO2e"))
               .join(indeksas.rename("LT_indeksas_1990_100")).join(vienam.rename("LT_t_vienam_gyv")))
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = t("sumažėjo", "fell by") if pokytis < 0 else t("padidėjo", "rose by")
    mln_t = t(" mln. t", " Mt")

    _dalys = [dalis(t("Grynieji išmetimai (su LULUCF)", "Net emissions (incl. LULUCF)"), grynieji, "mazesne", 0.2,
                    vienetai=mln_t, slenkscio_vnt=mln_t),
              dalis(t("Išmetimai vienam gyventojui", "Emissions per inhabitant"), vienam, "mazesne", 1.0, budas="proc", vienetai=" t")]
    return Rodiklis(
        dalys=_dalys,
        id="sesd-emisijos",
        pavadinimas=t("Šiltnamio efektą sukeliančių dujų išmetimai", "Greenhouse gas emissions"),
        trumpas_aprasas=t("mln. t CO₂ ekv.", "million t CO₂ eq."),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai išmetimai per metus sumažėja daugiau nei {sk(SLENKSTIS, False, 0)} %; "
                             f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False, 0)} %; kitu atveju – stabilu.",
                             f"Improving when emissions fall by more than {sk(SLENKSTIS, False, 0)}% in a year; "
                             f"worsening when they rise by more than {sk(SLENKSTIS, False, 0)}%; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. Lietuva išmetė {sk(pask, False)} mln. t CO₂ ekv. "
                                 f"({ankst} m. – {sk(pries, False)} mln. t). Išmetimai {kryptis} "
                                 f"{sk(abs(pokytis), False)} %; tai {sk(indeksas.iloc[-1], False, 0)} % 1990 m. lygio.",
                                 f"In {metai}, Lithuania emitted {sk(pask, False)} million t CO₂ eq. ({ankst}: "
                                 f"{sk(pries, False)} million t). Emissions {kryptis} {sk(abs(pokytis), False)}%; this "
                                 f"is {sk(indeksas.iloc[-1], False, 0)}% of the 1990 level."),
        sparkline=bendri[bendri.index >= "2005-01-01"],
        grafikai=[f1, f2],
        apibrezimas=t("Visi šalyje išmesti šiltnamio efektą sukeliantys dujų kiekiai (CO₂, metanas, azoto suboksidas, "
                      "F dujos), perskaičiuoti į CO₂ ekvivalentą, neįskaitant žemės naudojimo ir miškininkystės "
                      "(LULUCF), bet įskaitant tarptautinę aviaciją. Grynieji išmetimai rodo, kiek lieka atėmus "
                      "miškų ir žemės sugeriamą kiekį.",
                      "Total greenhouse gases emitted in the country (CO₂, methane, nitrous oxide, F-gases) converted to "
                      "CO₂ equivalent, excluding land use and forestry (LULUCF) but including international aviation. "
                      "Net emissions show what remains after subtracting the amount absorbed by forests and land."),
        pastabos=[
            t("Nacionalinė apskaita skelbiama su maždaug 1,5 metų vėlavimu.",
              "The national inventory is published with a delay of about 1.5 years."),
            t("Grynieji išmetimai labai priklauso nuo miškų kirtimo ir augimo įvertinimų, todėl gali būti "
              "perskaičiuojami atgaline data.",
              "Net emissions depend heavily on estimates of forest felling and growth, so they may be revised retroactively."),
        ],
        saltiniai=[("Eurostat – sdg_13_10", "https://ec.europa.eu/eurostat/databrowser/view/sdg_13_10/default/table?lang=en")],
        papildomai=[(f"{sk(vienam.iloc[-1], False)} t", t(f"vienam gyventojui, {metai} m.", f"per inhabitant, {metai}")),
                    (f"{sk(grynieji.iloc[-1], False)}{mln_t}", t(f"grynieji (su LULUCF), {metai} m.", f"net (incl. LULUCF), {metai}"))],
        lentele=lentele,
    )
