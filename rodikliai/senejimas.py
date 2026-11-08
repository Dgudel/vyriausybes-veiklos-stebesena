"""6. Visuomenės senėjimas: senatvės priklausomybės koeficientas (65+ / 15–64)."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius
from .eurostat_duomenys import serija

SLENKSTIS = 0.5     # punkto


def rodiklis() -> Rodiklis:
    g = lambda kodas, geo="LT": serija("demo_pjanind", geo, indic_de=kodas)
    lt, es = g("OLDDEP1"), g("OLDDEP1", "EU27_2020")
    vaikai, seni, mediana = g("PC_Y0_14"), g("PC_Y65_MAX"), g("MEDAGEPOP")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)

    nuo = "1995-01-01"
    f1 = go.Figure()
    linijos(f1, [("Lietuva", lt[lt.index >= nuo], SERIJOS[0]), ("ES-27", es[es.index >= nuo].dropna(), SERIJOS[1])],
            vnt="", zenklas=False)
    stilius(f1, "Senatvės priklausomybės koeficientas",
            "65 m. ir vyresnių žmonių skaičius 100-ui darbingo amžiaus (15–64 m.) žmonių",
            "Šaltinis: Eurostat, demo_pjanind", vnt="", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    linijos(f2, [("65 m. ir vyresni", seni[seni.index >= nuo], SERIJOS[0]),
                 ("Vaikai (0–14 m.)", vaikai[vaikai.index >= nuo], SERIJOS[3])], zenklas=False)
    stilius(f2, "Vaikų ir vyresnio amžiaus žmonių dalis", "% visų Lietuvos gyventojų",
            "Šaltinis: Eurostat, demo_pjanind", nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    lentele = (lt.rename("LT_koeficientas").to_frame().join(es.rename("ES27_koeficientas"))
               .join(seni.rename("LT_65plus_proc")).join(vaikai.rename("LT_0_14_proc"))
               .join(mediana.rename("LT_amziaus_mediana")))
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = "padidėjo" if pokytis > 0 else "sumažėjo"

    _dalys = [dalis("65 m. ir vyresnių dalis", seni, "mazesne", 0.3),
              dalis("Vaikų (0–14 m.) dalis", vaikai, "didesne", 0.3)]
    return Rodiklis(
        dalys=_dalys,
        id="senejimas",
        pavadinimas="Visuomenės senėjimas",
        trumpas_aprasas="65+ m. žmonių 100-ui darbingo amžiaus",
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=False,
        vertinimo_taisykle=(f"Gerėja, kai koeficientas per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} punkto; "
                            f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)} punkto; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. pradžioje senatvės priklausomybės koeficientas – {sk(pask, False)}: tiek 65 m. ir vyresnių "
                                f"žmonių tenka 100 darbingo amžiaus gyventojų ({ankst} m. – {sk(pries, False)}). Koeficientas "
                                f"{kryptis} {sk(abs(pokytis), False)} punkto; ES vidurkis – {sk(es.iloc[-1], False)}. "
                                f"Gyventojų amžiaus mediana – {sk(mediana.iloc[-1], False)} m."),
        sparkline=lt[lt.index >= "2005-01-01"],
        grafikai=[f1, f2],
        apibrezimas=("Senatvės priklausomybės koeficientas – 65 metų ir vyresnių gyventojų skaičius, tenkantis 100 "
                     "darbingo amžiaus (15–64 m.) gyventojų, sausio 1 d. Kuo jis didesnis, tuo mažiau dirbančiųjų "
                     "tenka vienam pensinio amžiaus žmogui."),
        pastabos=["Rodiklis keičiasi lėtai ir daugiausia priklauso nuo ankstesnių dešimtmečių gimstamumo ir "
                  "emigracijos, todėl trumpuoju laikotarpiu Vyriausybės sprendimai jį veikia mažai."],
        saltiniai=[("Eurostat – demo_pjanind", "https://ec.europa.eu/eurostat/databrowser/view/demo_pjanind/default/table?lang=en")],
        papildomai=[(f"{sk(seni.iloc[-1], False)} %", f"gyventojų – 65 m. ir vyresni, {metai} m."),
                    (f"{sk(mediana.iloc[-1], False)} m.", "amžiaus mediana")],
        lentele=lentele,
    )
