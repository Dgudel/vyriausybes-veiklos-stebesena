"""2.2 Sveikatos priežiūros rezultatai: išvengiamas mirtingumas dėl gydymo, gyvenimo trukmė."""
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, linijos, sk, stilius, ivertink
from .eurostat_duomenys import serija

SLENKSTIS = 2.0     # % santykinis pokytis per metus – mažesnis laikomas stabiliu


def rodiklis() -> Rodiklis:
    # Išvengiamas mirtingumas dėl gydymo (treatable), standartizuotas rodiklis 100 000 gyv.
    trt_lt = serija("hlth_cd_apr", "LT", mortalit="TRT", icd10="TOTAL", sex="T", unit="RT")
    trt_es = serija("hlth_cd_apr", "EU27_2020", mortalit="TRT", icd10="TOTAL", sex="T", unit="RT")
    # Tikėtina gyvenimo trukmė gimus
    gt_lt = serija("demo_mlexpec", "LT", age="Y_LT1", sex="T", unit="YR")
    gt_es = serija("demo_mlexpec", "EU27_2020", age="Y_LT1", sex="T", unit="YR")
    # Gera ar labai gera savo sveikata
    gs_lt = serija("hlth_silc_01", "LT", levels="VG_G", wstatus="POP", age="Y_GE16", sex="T", unit="PC")
    gs_es = serija("hlth_silc_01", "EU27_2020", levels="VG_G", wstatus="POP", age="Y_GE16", sex="T", unit="PC")

    pask, pries = trt_lt.iloc[-1], trt_lt.iloc[-2]
    metai, ankst = trt_lt.index[-1].year, trt_lt.index[-2].year
    pokytis_proc = (pask / pries - 1) * 100
    busena = ivertink(pokytis_proc, "mazesne", SLENKSTIS)

    f1 = go.Figure()
    linijos(f1, [("Lietuva", trt_lt, SERIJOS[0]), ("ES-27", trt_es, SERIJOS[1])],
            vnt="", zenklas=False, dec=0, zymekliai=True)
    stilius(f1, "Išvengiamas mirtingumas dėl gydymo",
            "Mirtys 100 000 gyventojų (standartizuotas rodiklis), kurių būtų galima išvengti laiku suteikus kokybišką gydymą",
            "Šaltinis: Eurostat, hlth_cd_apr", vnt="", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    nuo = gt_lt.index >= "2000-01-01"
    linijos(f2, [("Lietuva", gt_lt[nuo], SERIJOS[0]), ("ES-27", gt_es[gt_es.index >= "2000-01-01"], SERIJOS[1])],
            vnt=" m.", zenklas=False, dec=1, nuo_nulio=False)
    stilius(f2, "Vidutinė tikėtina gyvenimo trukmė gimus", "Metai", "Šaltinis: Eurostat, demo_mlexpec",
            vnt="", nulio_linija=False, metiniai=True)

    f3 = go.Figure()
    linijos(f3, [("Lietuva", gs_lt, SERIJOS[0]), ("ES-27", gs_es, SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f3, "Gyventojai, gerai ar labai gerai vertinantys savo sveikatą",
            "16 m. ir vyresnių gyventojų dalis, %", "Šaltinis: Eurostat, hlth_silc_01 (EU-SILC)",
            nulio_linija=False, metiniai=True)
    f3.update_yaxes(rangemode="tozero")

    lentele = (trt_lt.rename("LT_isvengiamas_mirtingumas_100k").to_frame()
               .join(trt_es.rename("ES27_isvengiamas_mirtingumas_100k"), how="outer")
               .join(gt_lt.rename("LT_gyvenimo_trukme_m"), how="outer")
               .join(gt_es.rename("ES27_gyvenimo_trukme_m"), how="outer")
               .join(gs_lt.rename("LT_gera_sveikata_proc"), how="outer")
               .join(gs_es.rename("ES27_gera_sveikata_proc"), how="outer"))
    lentele = lentele[lentele.index.year >= 2000]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = "sumažėjo" if pokytis_proc < 0 else "padidėjo"
    santykis = pask / trt_es.iloc[-1]
    return Rodiklis(
        id="sveikatos-prieziuros-rezultatai",
        pavadinimas="Išvengiamas mirtingumas dėl gydymo",
        trumpas_aprasas="mirčių 100 000 gyv.",
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena,
        zenklas=False, dec=0, spark_nuo_nulio=False,
        vertinimo_taisykle=(f"Gerėja, kai rodiklis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} %; "
                            f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)} %; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. Lietuvoje {sk(pask, False, 0)} iš 100 000 gyventojų mirė nuo priežasčių, "
                                f"kurių būtų galima išvengti laiku suteikus kokybišką gydymą ({ankst} m. – {sk(pries, False, 0)}). "
                                f"Rodiklis {kryptis} {sk(abs(pokytis_proc), False)} %, tačiau yra {sk(santykis, False)} karto "
                                f"didesnis nei ES vidurkis ({sk(trt_es.iloc[-1], False, 0)})."),
        sparkline=trt_lt,
        grafikai=[f1, f2, f3],
        apibrezimas=("Išvengiamas mirtingumas dėl gydymo (angl. treatable mortality) – jaunesnių nei 75 m. asmenų mirtys "
                     "nuo ligų, kurių daugumos būtų galima išvengti laiku suteikus veiksmingą sveikatos priežiūrą. "
                     "Tai vienas pagrindinių tarptautinių sveikatos sistemos veiklos rezultatų rodiklių (EBPO ir Eurostat). "
                     "Standartizuotas pagal amžių, todėl palyginamas tarp šalių."),
        pastabos=[
            "Eurostat mirtingumo duomenys skelbiami su maždaug 2–3 metų vėlavimu.",
            "2020–2021 m. rodiklius stipriai paveikė COVID-19 pandemija.",
            "Papildomi grafikai – gyvenimo trukmė ir sveikatos vertinimas – rodo bendrą gyventojų sveikatos būklę, "
            "kurią lemia ne tik sveikatos priežiūra.",
        ],
        saltiniai=[("Eurostat – hlth_cd_apr", "https://ec.europa.eu/eurostat/databrowser/view/hlth_cd_apr/default/table?lang=en"),
                   ("Eurostat – demo_mlexpec", "https://ec.europa.eu/eurostat/databrowser/view/demo_mlexpec/default/table?lang=en"),
                   ("Eurostat – hlth_silc_01", "https://ec.europa.eu/eurostat/databrowser/view/hlth_silc_01/default/table?lang=en")],
        papildomai=[(f"{sk(gt_lt.iloc[-1], False)} m.", f"tikėtina gyvenimo trukmė, {gt_lt.index[-1].year} m. "
                                                        f"(ES – {sk(gt_es.iloc[-1], False)} m.)"),
                    (f"{sk(gs_lt.iloc[-1], False)} %", f"gerai vertina savo sveikatą, {gs_lt.index[-1].year} m. "
                                                       f"(ES – {sk(gs_es.iloc[-1], False)} %)")],
        lentele=lentele,
    )
