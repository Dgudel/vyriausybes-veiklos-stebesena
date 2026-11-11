"""4. Eismo saugumas: žuvusieji keliuose 100 tūkst. gyventojų."""
import plotly.graph_objects as go

from .bendra import SERIJOS, TEKSTAS_ANTR, Rodiklis, ivertink, linijos, sk, stilius, t
from .eurostat_duomenys import serija

SLENKSTIS = 0.3     # žuvusiųjų 100 tūkst. gyv. (≈ 9 žmonės per metus)
KELIAI = [("RD_URB", "Miestuose", "Urban roads"), ("RD_RUR", "Užmiesčio keliuose", "Rural roads"),
          ("MWAY", "Automagistralėse", "Motorways")]


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
    stilius(f1, t("Žuvusieji keliuose", "Road deaths"), t("Žuvusiųjų skaičius 100 tūkst. gyventojų", "Deaths per 100,000 inhabitants"),
            t("Šaltinis: Eurostat, sdg_11_40 (CARE duomenų bazė)", "Source: Eurostat, sdg_11_40 (CARE database)"), vnt="", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    tipai = {}
    for i, (kodas, vardas_lt, vardas_en) in enumerate(KELIAI):
        vardas = t(vardas_lt, vardas_en)
        s = serija("sdg_11_40", "LT", tra_infr=kodas, unit="NR")
        s = s[s.index >= "2016-01-01"]
        tipai[kodas] = s
        f2.add_trace(go.Bar(x=s.index, y=s.values, name=vardas, marker_color=SERIJOS[i],
                            marker_line=dict(color="white", width=1),
                            hovertemplate=f"{vardas}: %{{y:.0f}}<extra></extra>"))
    f2.update_layout(barmode="stack")
    stilius(f2, t("Kur žūstama: kelio tipas", "Where deaths occur: road type"),
            t("Žuvusiųjų skaičius Lietuvoje (duomenys pagal kelio tipą – nuo 2016 m.)", "Number of deaths in Lithuania (data by road type since 2016)"),
            "Šaltinis: Eurostat, sdg_11_40", vnt="", nulio_linija=False, metiniai=True)

    lentele = (lt.rename("LT_100k").to_frame().join(es.rename("ES27_100k")).join(sk_lt.rename("LT_zuvusiuju_sk")))
    for kodas, s in tipai.items():
        lentele = lentele.join(s.rename(f"LT_{kodas}_sk"))
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = t("sumažėjo", "fell by") if pokytis < 0 else t("padidėjo", "rose by")
    return Rodiklis(
        id="zuvusieji-keliuose",
        pavadinimas=t("Žuvusieji keliuose", "Road deaths"),
        trumpas_aprasas=t("100 tūkst. gyventojų", "per 100,000 inhabitants"),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai rodiklis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} "
                             f"žuvusiojo 100 tūkst. gyv.; prastėja, kai tiek pat padidėja; kitu atveju – stabilu.",
                             f"Improving when the rate falls by more than {sk(SLENKSTIS, False)} deaths per 100,000 "
                             f"inhabitants in a year; worsening when it rises by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. žuvusiųjų keliuose – {sk(sk_lt.iloc[-1], False, 0)}, arba "
                                 f"{sk(pask, False)} 100 tūkst. gyventojų ({ankst} m. – {sk(pries, False)}). "
                                 f"Rodiklis {kryptis} {sk(abs(pokytis), False)}; ES vidurkis – {sk(es.iloc[-1], False)}.",
                                 f"In {metai}, {sk(sk_lt.iloc[-1], False, 0)} people died on the roads, or "
                                 f"{sk(pask, False)} per 100,000 inhabitants ({ankst}: {sk(pries, False)}). The rate "
                                 f"{kryptis} {sk(abs(pokytis), False)}; the EU average is {sk(es.iloc[-1], False)}."),
        sparkline=lt[lt.index >= nuo],
        grafikai=[f1, f2],
        apibrezimas=t("Kelių eismo įvykiuose žuvusių asmenų (mirusių per 30 dienų po įvykio) skaičius, "
                      "tenkantis 100 tūkst. gyventojų. ES siekia iki 2030 m. žuvusiųjų skaičių sumažinti perpus, "
                      "palyginti su 2019 m.",
                      "Number of people killed in road traffic accidents (died within 30 days) per 100,000 "
                      "inhabitants. The EU aims to halve road deaths by 2030 compared with 2019."),
        pastabos=[
            t("Programoje numatytas kelių būklės (pažeidimų) rodiklis viešai skelbiamų duomenų neturi, todėl "
              "infrastruktūros kokybę šiuo metu atspindi eismo saugumo rezultatas.",
              "The road condition (defects) indicator planned in the programme has no publicly available data, so "
              "infrastructure quality is currently reflected by the road safety outcome."),
            t("Lietuvoje žuvusiųjų skaičius nedidelis (apie 120–190 per metus), todėl pavieniai metai gali svyruoti.",
              "The number of road deaths in Lithuania is small (about 120–190 a year), so individual years may fluctuate."),
        ],
        saltiniai=[("Eurostat – sdg_11_40", "https://ec.europa.eu/eurostat/databrowser/view/sdg_11_40/default/table?lang=en")],
        papildomai=[(sk(sk_lt.iloc[-1], False, 0), t(f"žuvusiųjų {metai} m.", f"deaths in {metai}")),
                    (sk(lt[lt.index.year == 2019].iloc[0], False), t("2019 m. (ES tikslo atskaitos metai)", "2019 (EU target baseline)"))],
        lentele=lentele,
    )
