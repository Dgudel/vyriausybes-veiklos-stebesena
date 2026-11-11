"""2.4 Švietimo rezultatai: anksti mokslus palikę jaunuoliai ir aukštasis išsilavinimas."""
import plotly.graph_objects as go

from .bendra import dalis, papildomas_grafikas, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, t
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
                 (t("Lietuva – vaikinai", "Lithuania – young men"), lt_v[lt_v.index >= nuo], SERIJOS[2])],
            zenklas=False, zymekliai=True)
    stilius(f1, t("Anksti mokslus palikę jaunuoliai", "Early leavers from education and training"),
            t("18–24 m. asmenų, turinčių tik pagrindinį išsilavinimą ir nesimokančių, dalis, %",
              "Share of 18–24-year-olds with at most lower secondary education and not in education, %"),
            t("Šaltinis: Eurostat, sdg_04_10 (Darbo jėgos tyrimas)", "Source: Eurostat, sdg_04_10 (Labour Force Survey)"),
            nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    f2 = go.Figure()
    linijos(f2, [("Lietuva", alt[alt.index >= nuo], SERIJOS[0]), ("ES-27", aes[aes.index >= nuo], SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f2, t("Aukštąjį išsilavinimą įgiję 25–34 m. asmenys", "25–34-year-olds with tertiary education"),
            t("Dalis, % (ES tikslas 2030 m. – bent 45 %)", "Share, % (EU 2030 target – at least 45%)"),
            t("Šaltinis: Eurostat, sdg_04_20 (Darbo jėgos tyrimas)", "Source: Eurostat, sdg_04_20 (Labour Force Survey)"),
            nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    lentele = (lt.rename("LT_anksti_palike_proc").to_frame().join(es.rename("ES27_anksti_palike_proc"))
               .join(lt_v.rename("LT_vaikinai_proc")).join(lt_m.rename("LT_merginos_proc"))
               .join(alt.rename("LT_aukstasis_25_34_proc")).join(aes.rename("ES27_aukstasis_25_34_proc")))
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = t("sumažėjo", "fell by") if pokytis < 0 else t("padidėjo", "rose by")

    _dalys = [dalis(t("Anksti mokslus palikę vaikinai", "Early school leavers – young men"), lt_v, "mazesne", SLENKSTIS),
              dalis(t("Aukštasis išsilavinimas (25–34 m.)", "Tertiary education (aged 25–34)"), alt, "didesne", SLENKSTIS)]
    neet = serija("edat_lfse_20", "LT", sex="T", age="Y15-29", training="NO_FE_NO_NFE", wstatus="NEMP", unit="PC")
    neet_es = serija("edat_lfse_20", "EU27_2020", sex="T", age="Y15-29", training="NO_FE_NO_NFE", wstatus="NEMP", unit="PC")
    mok = serija("trng_lfse_01", "LT", sex="T", age="Y25-64", unit="PC")
    mok_es = serija("trng_lfse_01", "EU27_2020", sex="T", age="Y25-64", unit="PC")
    _dalys += [dalis(t("Nedirbantis ir nesimokantis jaunimas (NEET, 15–29 m.)", "Young people not in employment, education or training (NEET, 15–29)"),
                     neet, "mazesne", SLENKSTIS),
               dalis(t("Suaugusiųjų mokymasis (25–64 m., per 4 sav.)", "Adult learning (aged 25–64, last 4 weeks)"),
                     mok, "didesne", SLENKSTIS)]
    _r = Rodiklis(
        dalys=_dalys,
        id="anksti-mokslus-palike",
        pavadinimas=t("Anksti mokslus palikę jaunuoliai", "Early leavers from education"),
        trumpas_aprasas=t("18–24 m. jaunuolių", "of 18–24-year-olds"),
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai dalis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} proc. punkto; "
                             f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)} proc. punkto; kitu atveju – stabilu.",
                             f"Improving when the share falls by more than {sk(SLENKSTIS, False)} percentage point in a "
                             f"year; worsening when it rises by more than {sk(SLENKSTIS, False)} percentage point; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. {sk(pask, False)} % 18–24 m. jaunuolių buvo palikę mokslus turėdami tik "
                                 f"pagrindinį išsilavinimą ({ankst} m. – {sk(pries, False)} %). Dalis {kryptis} "
                                 f"{sk(abs(pokytis), False)} proc. punkto; ES vidurkis – {sk(es.iloc[-1], False)} %.",
                                 f"In {metai}, {sk(pask, False)}% of 18–24-year-olds had left education with at most "
                                 f"lower secondary education ({ankst}: {sk(pries, False)}%). The share {kryptis} "
                                 f"{sk(abs(pokytis), False)} percentage points; the EU average is {sk(es.iloc[-1], False)}%."),
        sparkline=lt[lt.index >= nuo],
        grafikai=[f1, f2],
        apibrezimas=t("18–24 m. asmenų, kurie įgijo ne aukštesnį nei pagrindinį išsilavinimą ir per pastarąsias "
                      "4 savaites nesimokė ir nedalyvavo mokymuose, dalis. ES tikslas 2030 m. – mažiau nei 9 %. "
                      "Papildomai rodoma aukštąjį išsilavinimą įgijusių 25–34 m. asmenų dalis.",
                      "Share of 18–24-year-olds with at most lower secondary education who were not in education or "
                      "training in the previous 4 weeks. EU 2030 target – below 9%. The share of 25–34-year-olds with "
                      "tertiary education is also shown."),
        pastabos=[
            t("Duomenys iš Darbo jėgos tyrimo (apklausos); Lietuvoje imtis nedidelė, todėl metiniai svyravimai "
              "gali būti dideli – žiūrėkite kelerių metų tendenciją.",
              "Data come from the Labour Force Survey; the sample in Lithuania is small, so annual fluctuations can be "
              "large – look at the trend over several years."),
            t("Vaikinų rodiklis paprastai gerokai aukštesnis nei merginų – lentelėje pateikiami abu.",
              "The rate for young men is usually much higher than for young women – both are given in the table."),
        ],
        saltiniai=[("Eurostat – sdg_04_10", "https://ec.europa.eu/eurostat/databrowser/view/sdg_04_10/default/table?lang=en"),
                   ("Eurostat – sdg_04_20", "https://ec.europa.eu/eurostat/databrowser/view/sdg_04_20/default/table?lang=en")],
        papildomai=[(f"{sk(alt.iloc[-1], False)} %", t(f"25–34 m. turi aukštąjį išsilavinimą, {alt.index[-1].year} m. "
                                                       f"(ES – {sk(aes.iloc[-1], False)} %)",
                                                       f"of 25–34-year-olds have tertiary education, {alt.index[-1].year} "
                                                       f"(EU: {sk(aes.iloc[-1], False)}%)")),
                    (f"{sk(lt_v.iloc[-1], False)} % / {sk(lt_m.iloc[-1], False)} %",
                     t(f"vaikinai / merginos, {lt_v.index[-1].year} m.", f"young men / young women, {lt_v.index[-1].year}"))],
        lentele=lentele,
    )
    _r.grafikai.append(papildomas_grafikas(
        t("Nedirbantis ir nesimokantis jaunimas (NEET)", "Young people not in employment, education or training (NEET)"),
        t("15–29 m. jaunuoliai, kurie nedirba ir nesimoko, %", "15–29-year-olds neither working nor studying, %"),
        "Šaltinis: Eurostat, edat_lfse_20", [("Lietuva", neet), ("ES-27", neet_es)], vnt=" %", nuo="2005-01-01"))
    _r.grafikai.append(papildomas_grafikas(
        t("Suaugusiųjų mokymasis", "Adult learning"),
        t("25–64 m. gyventojai, per paskutines 4 savaites dalyvavę mokymesi, %", "People aged 25–64 who took part in learning in the last 4 weeks, %"),
        "Šaltinis: Eurostat, trng_lfse_01", [("Lietuva", mok), ("ES-27", mok_es)], vnt=" %", nuo="2005-01-01"))
    return _r
