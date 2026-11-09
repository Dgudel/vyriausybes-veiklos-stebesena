"""2. Savižudybių lygis (standartizuotas mirtingumas 100 tūkst. gyv.)."""
import pandas as pd

from .bendra import Rodiklis, dalis, ivertink, papildomas_grafikas, sk
from .eurostat_duomenys import serija

SLENKSTIS = 3.0     # % per metus (nedideli skaičiai – atsitiktiniai svyravimai)


def _s(geo, sex="T"):
    return serija("hlth_cd_asdr2", geo, icd10="X60-X84_Y870", sex=sex, age="TOTAL", unit="RT")


def rodiklis() -> Rodiklis:
    lt, es, vyr, mot = _s("LT"), _s("EU27_2020"), _s("LT", "M"), _s("LT", "F")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = (pask / pries - 1) * 100
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)
    f1 = papildomas_grafikas("Savižudybių lygis", "Standartizuotas mirtingumo nuo savižudybių rodiklis, 100 tūkst. gyv.",
                             "Šaltinis: Eurostat, hlth_cd_asdr2", [("Lietuva", lt), ("ES-27", es)])
    f2 = papildomas_grafikas("Savižudybės pagal lytį", "100 tūkst. atitinkamos lyties gyventojų, Lietuva",
                             "Šaltinis: Eurostat, hlth_cd_asdr2", [("Vyrai", vyr), ("Moterys", mot)])
    lentele = pd.DataFrame({"LT": lt, "ES27": es, "LT_vyrai": vyr, "LT_moterys": mot})
    lentele.insert(0, "metai", lentele.index.year)
    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"
    return Rodiklis(
        dalys=[dalis("Vyrų savižudybių lygis", vyr, "mazesne", SLENKSTIS, budas="proc", vienetai=""),
               dalis("Moterų savižudybių lygis", mot, "mazesne", SLENKSTIS, budas="proc", vienetai="")],
        id="savizudybes", pavadinimas="Savižudybių lygis", trumpas_aprasas="100 tūkst. gyventojų",
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena, zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai rodiklis per metus sumažėja daugiau nei {sk(SLENKSTIS, False, 0)} %; "
                            f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False, 0)} %; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. standartizuotas savižudybių lygis – {sk(pask, False)} 100 tūkst. gyventojų "
                                f"({ankst} m. – {sk(pries, False)}); rodiklis {kryptis} {sk(abs(pokytis), False)} %. "
                                f"ES vidurkis – {sk(es.iloc[-1], False)}, t. y. Lietuvoje "
                                f"{sk(pask / es.iloc[-1], False)} karto daugiau. Vyrų lygis – {sk(vyr.iloc[-1], False)}, "
                                f"moterų – {sk(mot.iloc[-1], False)}."),
        sparkline=lt[lt.index >= "2011-01-01"], grafikai=[f1, f2],
        apibrezimas=("Tyčinio savęs žalojimo (TLK-10 X60–X84, Y87.0) sukeltų mirčių skaičius 100 tūkst. gyventojų, "
                     "standartizuotas pagal ES gyventojų amžiaus struktūrą, kad šalis būtų galima palyginti."),
        pastabos=["Mirties priežasčių duomenys skelbiami su maždaug 2 metų vėlavimu.",
                  "Jei jums ar artimam žmogui reikia pagalbos, kreipkitės į emocinės paramos linijas, pvz., "
                  "„Vilties linija“ 116 123."],
        saltiniai=[("Eurostat – hlth_cd_asdr2", "https://ec.europa.eu/eurostat/databrowser/view/hlth_cd_asdr2/default/table?lang=en")],
        papildomai=[(sk(es.iloc[-1], False), "ES vidurkis")], lentele=lentele)
