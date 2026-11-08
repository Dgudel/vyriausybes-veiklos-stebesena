"""4. Klimatas: šiltnamio efektą sukeliančių dujų (ŠESD) išmetimai."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius
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
    linijos(f1, [("Išmetimai (be LULUCF)", bendri, SERIJOS[0]),
                 ("Grynieji (su miškais ir žemėnauda)", grynieji, SERIJOS[2])],
            vnt="", zenklas=False, zymekliai=False)
    stilius(f1, "Šiltnamio efektą sukeliančių dujų išmetimai", "Mln. t CO₂ ekvivalento per metus",
            "Šaltinis: Eurostat, sdg_13_10 (EEA nacionalinė ŠESD apskaita)", vnt="", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    linijos(f2, [("Lietuva", vienam, SERIJOS[0])], vnt=" t", zenklas=False, zymekliai=False)
    stilius(f2, "Išmetimai vienam gyventojui", "Tonos CO₂ ekvivalento (be LULUCF)",
            "Šaltinis: Eurostat, sdg_13_10", vnt=" t", nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    lentele = (bendri.rename("LT_mln_t_CO2e").to_frame().join(grynieji.rename("LT_grynieji_mln_t_CO2e"))
               .join(indeksas.rename("LT_indeksas_1990_100")).join(vienam.rename("LT_t_vienam_gyv")))
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"

    _dalys = [dalis("Grynieji išmetimai (su LULUCF)", grynieji, "mazesne", 0.2, vienetai=" mln. t", slenkscio_vnt=" mln. t"),
              dalis("Išmetimai vienam gyventojui", vienam, "mazesne", 1.0, budas="proc", vienetai=" t")]
    return Rodiklis(
        dalys=_dalys,
        id="sesd-emisijos",
        pavadinimas="Šiltnamio efektą sukeliančių dujų išmetimai",
        trumpas_aprasas="mln. t CO₂ ekv.",
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai išmetimai per metus sumažėja daugiau nei {sk(SLENKSTIS, False, 0)} %; "
                            f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False, 0)} %; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. Lietuva išmetė {sk(pask, False)} mln. t CO₂ ekv. "
                                f"({ankst} m. – {sk(pries, False)} mln. t). Išmetimai {kryptis} "
                                f"{sk(abs(pokytis), False)} %; tai {sk(indeksas.iloc[-1], False, 0)} % 1990 m. lygio."),
        sparkline=bendri[bendri.index >= "2005-01-01"],
        grafikai=[f1, f2],
        apibrezimas=("Visi šalyje išmesti šiltnamio efektą sukeliantys dujų kiekiai (CO₂, metanas, azoto suboksidas, "
                     "F dujos), perskaičiuoti į CO₂ ekvivalentą, neįskaitant žemės naudojimo ir miškininkystės "
                     "(LULUCF), bet įskaitant tarptautinę aviaciją. Grynieji išmetimai rodo, kiek lieka atėmus "
                     "miškų ir žemės sugeriamą kiekį."),
        pastabos=[
            "Nacionalinė apskaita skelbiama su maždaug 1,5 metų vėlavimu.",
            "Grynieji išmetimai labai priklauso nuo miškų kirtimo ir augimo įvertinimų, todėl gali būti "
            "perskaičiuojami atgaline data.",
        ],
        saltiniai=[("Eurostat – sdg_13_10", "https://ec.europa.eu/eurostat/databrowser/view/sdg_13_10/default/table?lang=en")],
        papildomai=[(f"{sk(vienam.iloc[-1], False)} t", f"vienam gyventojui, {metai} m."),
                    (f"{sk(grynieji.iloc[-1], False)} mln. t", f"grynieji (su LULUCF), {metai} m.")],
        lentele=lentele,
    )
