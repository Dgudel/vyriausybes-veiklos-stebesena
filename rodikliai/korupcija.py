"""7. Valstybės valdymo kokybė: korupcijos suvokimo indeksas (CPI) ir teismų nepriklausomumo vertinimas."""
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, dalis, ivertink, linijos, sk, stilius, t
from .eurostat_duomenys import serija

SLENKSTIS = 1.0     # CPI balas (skalė 0–100)


def rodiklis() -> Rodiklis:
    lt, es = serija("sdg_16_50", "LT", unit="SC"), serija("sdg_16_50", "EU27_2020", unit="SC")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    f1 = go.Figure()
    linijos(f1, [("Lietuva", lt, SERIJOS[0]), ("ES-27", es.dropna(), SERIJOS[1])], vnt="", zenklas=False, dec=0, zymekliai=True)
    stilius(f1, t("Korupcijos suvokimo indeksas", "Corruption Perceptions Index"),
            t("Balai: 0 – labai korumpuota, 100 – labai skaidri", "Score: 0 – highly corrupt, 100 – very clean"),
            t("Šaltinis: Transparency International per Eurostat, sdg_16_50",
              "Source: Transparency International via Eurostat, sdg_16_50"), vnt="", nulio_linija=False, metiniai=True)

    _dalys, grafikai = [], [f1]
    try:
        gerai = serija("sdg_16_40", "LT", lev_perc="VG_FG", unit="PC")
        gerai_es = serija("sdg_16_40", "EU27_2020", lev_perc="VG_FG", unit="PC")
        _dalys.append(dalis(t("Teismų nepriklausomumą vertina gerai", "Rate the independence of courts as good"),
                            gerai, "didesne", 2.0))
        f2 = go.Figure()
        linijos(f2, [("Lietuva", gerai, SERIJOS[0]), ("ES-27", gerai_es.dropna(), SERIJOS[1])], zenklas=False, zymekliai=True)
        stilius(f2, t("Suvokiamas teismų nepriklausomumas", "Perceived independence of the justice system"),
                t("Gyventojai, teismų ir teisėjų nepriklausomumą vertinantys labai arba gana gerai, %",
                  "Population rating the independence of courts and judges as very or fairly good, %"),
                t("Šaltinis: Eurostat, sdg_16_40 (Eurobarometras, ES teisingumo rezultatų suvestinė)",
                  "Source: Eurostat, sdg_16_40 (Eurobarometer, EU Justice Scoreboard)"), nulio_linija=False, metiniai=True)
        f2.update_yaxes(rangemode="tozero")
        grafikai.append(f2)
    except Exception as e:
        print(f"  ⚠ sdg_16_40 neįtrauktas: {e}")

    lentele = lt.rename("LT_CPI").to_frame().join(es.rename("ES27_CPI"))
    lentele.insert(0, "metai", lentele.index.year)
    kryptis = t("padidėjo", "rose by") if pokytis > 0 else t("sumažėjo", "fell by")
    return Rodiklis(
        dalys=_dalys,
        id="korupcijos-suvokimas",
        pavadinimas=t("Korupcijos suvokimo indeksas", "Corruption Perceptions Index"),
        trumpas_aprasas=t("balai iš 100 (daugiau – skaidriau)", "score out of 100 (higher – cleaner)"),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena, dec=0,
        zenklas=False, spark_nuo_nulio=False,
        vertinimo_taisykle=t(f"Gerėja, kai indeksas per metus padidėja daugiau nei {sk(SLENKSTIS, False, 0)} balu; "
                             f"prastėja, kai tiek pat sumažėja; kitu atveju – stabilu.",
                             f"Improving when the index rises by more than {sk(SLENKSTIS, False, 0)} point in a year; "
                             f"worsening when it falls by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. Lietuvos korupcijos suvokimo indeksas – {sk(pask, False, 0)} balų iš 100 "
                                 f"({ankst} m. – {sk(pries, False, 0)}); ES vidurkis – {sk(es.iloc[-1], False, 0)}. "
                                 f"Indeksas {kryptis} {sk(abs(pokytis), False, 0)} balo.",
                                 f"In {metai}, Lithuania's Corruption Perceptions Index was {sk(pask, False, 0)} out of 100 "
                                 f"({ankst}: {sk(pries, False, 0)}); the EU average is {sk(es.iloc[-1], False, 0)}. "
                                 f"The index {kryptis} {sk(abs(pokytis), False, 0)} points."),
        sparkline=lt,
        grafikai=grafikai,
        apibrezimas=t("Transparency International korupcijos suvokimo indeksas apibendrina ekspertų ir verslo atstovų "
                      "vertinimus, kiek korumpuotas laikomas viešasis sektorius: 0 – labai korumpuotas, 100 – labai skaidrus.",
                      "Transparency International's Corruption Perceptions Index aggregates expert and business "
                      "assessments of how corrupt the public sector is perceived to be: 0 – highly corrupt, 100 – very clean."),
        pastabos=[t("Tai suvokimo, ne faktinės korupcijos matas; metinis pokytis dažnai būna statistiškai nereikšmingas, "
                    "todėl svarbesnė ilgesnio laikotarpio tendencija.",
                    "This is a measure of perception, not of actual corruption; year-on-year changes are often not "
                    "statistically significant, so the longer-term trend matters more.")],
        saltiniai=[("Eurostat – sdg_16_50", "https://ec.europa.eu/eurostat/databrowser/view/sdg_16_50/default/table?lang=en"),
                   ("Eurostat – sdg_16_40", "https://ec.europa.eu/eurostat/databrowser/view/sdg_16_40/default/table?lang=en"),
                   ("Transparency International – CPI", "https://www.transparency.org/en/cpi")],
        lentele=lentele,
    )
