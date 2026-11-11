"""2.2 Sveikatos priežiūros rezultatai: išvengiamas mirtingumas dėl gydymo, gyvenimo trukmė."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, Rodiklis, linijos, sk, stilius, ivertink, t
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
    stilius(f1, t("Išvengiamas mirtingumas dėl gydymo", "Treatable mortality"),
            t("Mirtys 100 000 gyventojų (standartizuotas rodiklis), kurių būtų galima išvengti laiku suteikus kokybišką gydymą",
              "Deaths per 100,000 inhabitants (standardised) that could be avoided through timely, high-quality treatment"),
            "Šaltinis: Eurostat, hlth_cd_apr", vnt="", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    nuo = gt_lt.index >= "2000-01-01"
    linijos(f2, [("Lietuva", gt_lt[nuo], SERIJOS[0]), ("ES-27", gt_es[gt_es.index >= "2000-01-01"], SERIJOS[1])],
            vnt=t(" m.", " yrs"), zenklas=False, dec=1, nuo_nulio=False)
    stilius(f2, t("Vidutinė tikėtina gyvenimo trukmė gimus", "Life expectancy at birth"), t("Metai", "Years"),
            "Šaltinis: Eurostat, demo_mlexpec",
            vnt="", nulio_linija=False, metiniai=True)

    f3 = go.Figure()
    linijos(f3, [("Lietuva", gs_lt, SERIJOS[0]), ("ES-27", gs_es, SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f3, t("Gyventojai, gerai ar labai gerai vertinantys savo sveikatą", "People rating their health as good or very good"),
            t("16 m. ir vyresnių gyventojų dalis, %", "Share of people aged 16 and over, %"), "Šaltinis: Eurostat, hlth_silc_01 (EU-SILC)",
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

    kryptis = t("sumažėjo", "fell by") if pokytis_proc < 0 else t("padidėjo", "rose by")
    santykis = pask / trt_es.iloc[-1]
    m_ = t(" m.", " yrs")

    _dalys = [dalis(t("Tikėtina gyvenimo trukmė", "Life expectancy"), gt_lt, "didesne", 0.2, vienetai=m_, slenkscio_vnt=m_),
              dalis(t("Gerai vertinantys savo sveikatą", "Rating own health as good"), gs_lt, "didesne", 1.0)]
    return Rodiklis(
        dalys=_dalys,
        id="sveikatos-prieziuros-rezultatai",
        pavadinimas=t("Išvengiamas mirtingumas dėl gydymo", "Treatable mortality"),
        trumpas_aprasas=t("mirčių 100 000 gyv.", "deaths per 100,000 inhabitants"),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena,
        zenklas=False, dec=0, spark_nuo_nulio=False,
        vertinimo_taisykle=t(f"Gerėja, kai rodiklis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} %; "
                             f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)} %; kitu atveju – stabilu.",
                             f"Improving when the rate falls by more than {sk(SLENKSTIS, False)}% in a year; "
                             f"worsening when it rises by more than {sk(SLENKSTIS, False)}%; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. Lietuvoje {sk(pask, False, 0)} iš 100 000 gyventojų mirė nuo priežasčių, "
                                 f"kurių būtų galima išvengti laiku suteikus kokybišką gydymą ({ankst} m. – {sk(pries, False, 0)}). "
                                 f"Rodiklis {kryptis} {sk(abs(pokytis_proc), False)} %, tačiau yra {sk(santykis, False)} karto "
                                 f"didesnis nei ES vidurkis ({sk(trt_es.iloc[-1], False, 0)}).",
                                 f"In {metai}, {sk(pask, False, 0)} per 100,000 inhabitants in Lithuania died of causes "
                                 f"that could have been avoided through timely, high-quality treatment ({ankst}: "
                                 f"{sk(pries, False, 0)}). The rate {kryptis} {sk(abs(pokytis_proc), False)}%, but it is "
                                 f"{sk(santykis, False)} times the EU average ({sk(trt_es.iloc[-1], False, 0)})."),
        sparkline=trt_lt,
        grafikai=[f1, f2, f3],
        apibrezimas=t("Išvengiamas mirtingumas dėl gydymo (angl. treatable mortality) – jaunesnių nei 75 m. asmenų mirtys "
                      "nuo ligų, kurių daugumos būtų galima išvengti laiku suteikus veiksmingą sveikatos priežiūrą. "
                      "Tai vienas pagrindinių tarptautinių sveikatos sistemos veiklos rezultatų rodiklių (EBPO ir Eurostat). "
                      "Standartizuotas pagal amžių, todėl palyginamas tarp šalių.",
                      "Treatable mortality – deaths of people under 75 from diseases that could mostly be avoided through "
                      "timely and effective health care. It is one of the main international indicators of health "
                      "system performance (OECD and Eurostat). It is age-standardised and therefore comparable across countries."),
        pastabos=[
            t("Eurostat mirtingumo duomenys skelbiami su maždaug 2–3 metų vėlavimu.",
              "Eurostat mortality data are published with a delay of about 2–3 years."),
            t("2020–2021 m. rodiklius stipriai paveikė COVID-19 pandemija.",
              "The 2020–2021 figures were strongly affected by the COVID-19 pandemic."),
            t("Papildomi grafikai – gyvenimo trukmė ir sveikatos vertinimas – rodo bendrą gyventojų sveikatos būklę, "
              "kurią lemia ne tik sveikatos priežiūra.",
              "The additional charts – life expectancy and self-rated health – show the overall health of the "
              "population, which depends on more than health care."),
        ],
        saltiniai=[("Eurostat – hlth_cd_apr", "https://ec.europa.eu/eurostat/databrowser/view/hlth_cd_apr/default/table?lang=en"),
                   ("Eurostat – demo_mlexpec", "https://ec.europa.eu/eurostat/databrowser/view/demo_mlexpec/default/table?lang=en"),
                   ("Eurostat – hlth_silc_01", "https://ec.europa.eu/eurostat/databrowser/view/hlth_silc_01/default/table?lang=en")],
        papildomai=[(f"{sk(gt_lt.iloc[-1], False)}{m_}", t(f"tikėtina gyvenimo trukmė, {gt_lt.index[-1].year} m. "
                                                           f"(ES – {sk(gt_es.iloc[-1], False)} m.)",
                                                           f"life expectancy, {gt_lt.index[-1].year} "
                                                           f"(EU: {sk(gt_es.iloc[-1], False)} yrs)")),
                    (f"{sk(gs_lt.iloc[-1], False)} %", t(f"gerai vertina savo sveikatą, {gs_lt.index[-1].year} m. "
                                                         f"(ES – {sk(gs_es.iloc[-1], False)} %)",
                                                         f"rate their health as good, {gs_lt.index[-1].year} "
                                                         f"(EU: {sk(gs_es.iloc[-1], False)}%)"))],
        lentele=lentele,
    )
