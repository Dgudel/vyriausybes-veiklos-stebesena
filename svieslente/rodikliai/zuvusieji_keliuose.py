"""4. Eismo saugumas: žuvusieji keliuose 100 tūkst. gyventojų."""
import plotly.graph_objects as go

from .bendra import SERIJOS, TEKSTAS_ANTR, Rodiklis, ivertink, linijos, sk, stilius
from .eurostat_duomenys import serija

SLENKSTIS = 0.3     # žuvusiųjų 100 tūkst. gyv. (≈ 9 žmonės per metus)
KELIAI = [("RD_URB", "Miestuose"), ("RD_RUR", "Užmiesčio keliuose"), ("MWAY", "Automagistralėse")]


def rodiklis() -> Rodiklis:
    lt = serija("sdg_11_40", "LT", tra_infr="TOTAL", unit="RT")
    es = serija("sdg_11_40", "EU27_2020", tra_infr="TOTAL", unit="RT")
    sk_lt = serija("sdg_11_40", "LT", tra_infr="TOTAL", unit="NR")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)

    nuo = "2005-01-01"
    f1 = go.Figure()
    linijos(f1, [("Lietuva", lt[lt.index >= nuo], SERIJOS[0]), ("ES-27", es[es.index >= nuo], SERIJOS[1])],
            vnt="", zenklas=False, zymekliai=True)
    stilius(f1, "Žuvusieji keliuose", "Žuvusiųjų skaičius 100 tūkst. gyventojų",
            "Šaltinis: Eurostat, sdg_11_40 (CARE duomenų bazė)", vnt="", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    tipai = {}
    for i, (kodas, vardas) in enumerate(KELIAI):
        s = serija("sdg_11_40", "LT", tra_infr=kodas, unit="NR")
        s = s[s.index >= "2016-01-01"]
        tipai[kodas] = s
        f2.add_trace(go.Bar(x=s.index, y=s.values, name=vardas, marker_color=SERIJOS[i],
                            marker_line=dict(color="white", width=1),
                            hovertemplate=f"{vardas}: %{{y:.0f}}<extra></extra>"))
    f2.update_layout(barmode="stack")
    stilius(f2, "Kur žūstama: kelio tipas", "Žuvusiųjų skaičius Lietuvoje (duomenys pagal kelio tipą – nuo 2016 m.)",
            "Šaltinis: Eurostat, sdg_11_40", vnt="", nulio_linija=False, metiniai=True)

    lentele = (lt.rename("LT_100k").to_frame().join(es.rename("ES27_100k")).join(sk_lt.rename("LT_zuvusiuju_sk")))
    for kodas, s in tipai.items():
        lentele = lentele.join(s.rename(f"LT_{kodas}_sk"))
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"
    return Rodiklis(
        id="zuvusieji-keliuose",
        pavadinimas="Žuvusieji keliuose",
        trumpas_aprasas="100 tūkst. gyventojų",
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai rodiklis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} "
                            f"žuvusiojo 100 tūkst. gyv.; prastėja, kai tiek pat padidėja; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. keliuose žuvo {sk(sk_lt.iloc[-1], False, 0)} žmonės – "
                                f"{sk(pask, False)} 100 tūkst. gyventojų ({ankst} m. – {sk(pries, False)}). "
                                f"Rodiklis {kryptis} {sk(abs(pokytis), False)}; ES vidurkis – {sk(es.iloc[-1], False)}."),
        sparkline=lt[lt.index >= nuo],
        grafikai=[f1, f2],
        apibrezimas=("Kelių eismo įvykiuose žuvusių asmenų (mirusių per 30 dienų po įvykio) skaičius, "
                     "tenkantis 100 tūkst. gyventojų. ES siekia iki 2030 m. žuvusiųjų skaičių sumažinti perpus, "
                     "palyginti su 2019 m."),
        pastabos=[
            "Programoje numatytas kelių būklės (pažeidimų) rodiklis viešai skelbiamų duomenų neturi, todėl "
            "infrastruktūros kokybę šiuo metu atspindi eismo saugumo rezultatas.",
            "Lietuvoje žuvusiųjų skaičius nedidelis (apie 120–190 per metus), todėl pavieniai metai gali svyruoti.",
        ],
        saltiniai=[("Eurostat – sdg_11_40", "https://ec.europa.eu/eurostat/databrowser/view/sdg_11_40/default/table?lang=en")],
        papildomai=[(sk(sk_lt.iloc[-1], False, 0), f"žuvusiųjų {metai} m."),
                    (sk(lt[lt.index.year == 2019].iloc[0], False), "2019 m. (ES tikslo atskaitos metai)")],
        lentele=lentele,
    )
