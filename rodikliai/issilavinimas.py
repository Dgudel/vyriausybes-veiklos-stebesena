"""2.4 Švietimo rezultatai: anksti mokslus palikę jaunuoliai ir aukštasis išsilavinimas."""
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, ivertink, linijos, sk, stilius
from .eurostat_duomenys import serija

SLENKSTIS = 0.5     # proc. punkto (LFS apklausa – mažesni pokyčiai gali būti atsitiktiniai)


def rodiklis() -> Rodiklis:
    f = dict(wstatus="POP", age="Y18-24", sex="T", unit="PC")
    lt, es = serija("sdg_04_10", "LT", **f), serija("sdg_04_10", "EU27_2020", **f)
    a = dict(sex="T", age="Y25-34", unit="PC", isced11="ED5-8")
    alt, aes = serija("sdg_04_20", "LT", **a), serija("sdg_04_20", "EU27_2020", **a)
    m = dict(wstatus="POP", age="Y18-24", unit="PC")
    lt_v, lt_m = serija("sdg_04_10", "LT", sex="M", **m), serija("sdg_04_10", "LT", sex="F", **m)

    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)

    nuo = "2010-01-01"
    f1 = go.Figure()
    linijos(f1, [("Lietuva", lt[lt.index >= nuo], SERIJOS[0]), ("ES-27", es[es.index >= nuo], SERIJOS[1]),
                 ("Lietuva – vaikinai", lt_v[lt_v.index >= nuo], SERIJOS[2])],
            zenklas=False, zymekliai=True)
    stilius(f1, "Anksti mokslus palikę jaunuoliai",
            "18–24 m. asmenų, turinčių tik pagrindinį išsilavinimą ir nesimokančių, dalis, %",
            "Šaltinis: Eurostat, sdg_04_10 (Darbo jėgos tyrimas)", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    linijos(f2, [("Lietuva", alt[alt.index >= nuo], SERIJOS[0]), ("ES-27", aes[aes.index >= nuo], SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f2, "Aukštąjį išsilavinimą įgiję 25–34 m. asmenys",
            "Dalis, % (ES tikslas 2030 m. – bent 45 %)",
            "Šaltinis: Eurostat, sdg_04_20 (Darbo jėgos tyrimas)", nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    lentele = (lt.rename("LT_anksti_palike_proc").to_frame().join(es.rename("ES27_anksti_palike_proc"))
               .join(lt_v.rename("LT_vaikinai_proc")).join(lt_m.rename("LT_merginos_proc"))
               .join(alt.rename("LT_aukstasis_25_34_proc")).join(aes.rename("ES27_aukstasis_25_34_proc")))
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"
    return Rodiklis(
        id="anksti-mokslus-palike",
        pavadinimas="Anksti mokslus palikę jaunuoliai",
        trumpas_aprasas="18–24 m. jaunuolių",
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai dalis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} proc. punkto; "
                            f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)} proc. punkto; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. {sk(pask, False)} % 18–24 m. jaunuolių buvo palikę mokslus turėdami tik "
                                f"pagrindinį išsilavinimą ({ankst} m. – {sk(pries, False)} %). Dalis {kryptis} "
                                f"{sk(abs(pokytis), False)} proc. punkto; ES vidurkis – {sk(es.iloc[-1], False)} %."),
        sparkline=lt[lt.index >= nuo],
        grafikai=[f1, f2],
        apibrezimas=("18–24 m. asmenų, kurie įgijo ne aukštesnį nei pagrindinį išsilavinimą ir per pastarąsias "
                     "4 savaites nesimokė ir nedalyvavo mokymuose, dalis. ES tikslas 2030 m. – mažiau nei 9 %. "
                     "Papildomai rodoma aukštąjį išsilavinimą įgijusių 25–34 m. asmenų dalis."),
        pastabos=[
            "Duomenys iš Darbo jėgos tyrimo (apklausos); Lietuvoje imtis nedidelė, todėl metiniai svyravimai "
            "gali būti dideli – žiūrėkite kelerių metų tendenciją.",
            "Vaikinų rodiklis paprastai gerokai aukštesnis nei merginų – lentelėje pateikiami abu.",
        ],
        saltiniai=[("Eurostat – sdg_04_10", "https://ec.europa.eu/eurostat/databrowser/view/sdg_04_10/default/table?lang=en"),
                   ("Eurostat – sdg_04_20", "https://ec.europa.eu/eurostat/databrowser/view/sdg_04_20/default/table?lang=en")],
        papildomai=[(f"{sk(alt.iloc[-1], False)} %", f"25–34 m. turi aukštąjį išsilavinimą, {alt.index[-1].year} m. "
                                                     f"(ES – {sk(aes.iloc[-1], False)} %)"),
                    (f"{sk(lt_v.iloc[-1], False)} % / {sk(lt_m.iloc[-1], False)} %",
                     f"vaikinai / merginos, {lt_v.index[-1].year} m.")],
        lentele=lentele,
    )
