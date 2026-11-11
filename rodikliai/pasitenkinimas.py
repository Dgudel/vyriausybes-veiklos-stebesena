"""1. Pasitenkinimas gyvenimu (EU-SILC, 0–10 skalė)."""
import pandas as pd

from .bendra import Rodiklis, dalis, ivertink, papildomas_grafikas, sk, t
from .eurostat_duomenys import serija

SLENKSTIS = 0.1     # balo


def _s(geo, age="Y_GE16"):
    return serija("ilc_pw01", geo, statinfo="AVG", unit="RTG", isced11="TOTAL", life_sat="LIFE", sex="T", age=age)


def rodiklis() -> Rodiklis:
    lt, es = _s("LT"), _s("EU27_2020")
    jauni, seni = _s("LT", "Y16-29"), _s("LT", "Y_GE65")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    f1 = papildomas_grafikas(t("Pasitenkinimas gyvenimu", "Life satisfaction"),
                             t("Vidutinis įvertinimas 0–10 skalėje, 16 m. ir vyresni", "Mean rating on a 0–10 scale, aged 16 and over"),
                             "Šaltinis: Eurostat, ilc_pw01 (EU-SILC)", [("Lietuva", lt), ("ES-27", es)])
    f2 = papildomas_grafikas(t("Pasitenkinimas gyvenimu pagal amžių", "Life satisfaction by age"),
                             t("Vidutinis įvertinimas 0–10 skalėje, Lietuva", "Mean rating on a 0–10 scale, Lithuania"),
                             "Šaltinis: Eurostat, ilc_pw01", [(t("16–29 m.", "Aged 16–29"), jauni),
                                                             (t("65 m. ir vyresni", "Aged 65 and over"), seni)])
    lentele = pd.DataFrame({"LT": lt, "ES27": es, "LT_16_29": jauni, "LT_65plus": seni})
    lentele.insert(0, "metai", lentele.index.year)
    kryptis = (t("padidėjo", "rose by") if pokytis > 0 else
               (t("sumažėjo", "fell by") if pokytis < 0 else t("nepasikeitė", "was unchanged")))
    balo = t(" balo", " points")
    return Rodiklis(
        dalys=[dalis(t("Jaunimas (16–29 m.)", "Young people (16–29)"), jauni, "didesne", SLENKSTIS, vienetai="", slenkscio_vnt=balo),
               dalis(t("Vyresni (65 m. ir daugiau)", "Older people (65+)"), seni, "didesne", SLENKSTIS, vienetai="", slenkscio_vnt=balo)],
        id="pasitenkinimas", pavadinimas=t("Pasitenkinimas gyvenimu", "Life satisfaction"),
        trumpas_aprasas=t("vidutinis įvertinimas, 0–10", "mean rating, 0–10"),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena, zenklas=False, spark_nuo_nulio=False,
        vertinimo_taisykle=t(f"Gerėja, kai vidutinis įvertinimas per metus padidėja daugiau nei {sk(SLENKSTIS, False)} "
                             f"balo; prastėja, kai tiek pat sumažėja; kitu atveju – stabilu.",
                             f"Improving when the mean rating rises by more than {sk(SLENKSTIS, False)} points in a "
                             f"year; worsening when it falls by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. gyventojai savo gyvenimą vidutiniškai vertino {sk(pask, False)} balo iš 10 "
                                 f"({ankst} m. – {sk(pries, False)}); įvertinimas {kryptis}"
                                 + (f" {sk(abs(pokytis), False)} balo" if pokytis else "")
                                 + f". ES vidurkis – {sk(es.iloc[-1], False)}. Jaunimas vertina {sk(jauni.iloc[-1], False)}, "
                                 f"vyresni nei 65 m. – {sk(seni.iloc[-1], False)}.",
                                 f"In {metai}, people rated their life at {sk(pask, False)} out of 10 on average "
                                 f"({ankst}: {sk(pries, False)}); the rating {kryptis}"
                                 + (f" {sk(abs(pokytis), False)} points" if pokytis else "")
                                 + f". The EU average is {sk(es.iloc[-1], False)}. Young people rate it "
                                 f"{sk(jauni.iloc[-1], False)}, people over 65 – {sk(seni.iloc[-1], False)}."),
        sparkline=lt, grafikai=[f1, f2],
        apibrezimas=t("Atsakymų į klausimą „Kiek apskritai esate patenkinti savo gyvenimu?“ (0 – visiškai nepatenkintas, "
                      "10 – visiškai patenkintas) vidurkis, Gyventojų pajamų ir gyvenimo sąlygų tyrimas (EU-SILC).",
                      "Mean answer to the question “Overall, how satisfied are you with your life these days?” "
                      "(0 – not at all satisfied, 10 – completely satisfied), Survey on Income and Living Conditions (EU-SILC)."),
        pastabos=[t("Klausimas užduodamas ne kasmet visose šalyse; 2013 ir 2018 m. – specialieji tyrimo moduliai.",
                    "The question is not asked every year in all countries; 2013 and 2018 were special survey modules.")],
        saltiniai=[("Eurostat – ilc_pw01", "https://ec.europa.eu/eurostat/databrowser/view/ilc_pw01/default/table?lang=en")],
        papildomai=[(sk(es.iloc[-1], False), t("ES vidurkis", "EU average"))], lentele=lentele)
