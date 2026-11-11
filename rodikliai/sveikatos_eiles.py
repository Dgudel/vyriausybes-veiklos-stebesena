"""2.1 Negavo gydymo dėl laukimo eilių (Eurostat apklausos rodiklis)."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, TEKSTAS_ANTR, Rodiklis, ivertink, linijos, sk, stilius, t
from .eurostat_duomenys import serija

KODAS = "hlth_silc_08"
FAILAS = "hlth_silc_08_nepatenkinti_poreikiai.csv"
SLENKSTIS = 0.3     # proc. punkto: apklausos duomenys, mažesni pokyčiai gali būti atsitiktiniai
def _salt():
    return t("Šaltinis: Eurostat, hlth_silc_08 (EU-SILC), 16 m. ir vyresni gyventojai",
             "Source: Eurostat, hlth_silc_08 (EU-SILC), population aged 16 and over")


def _s(geo, reason="WLIST", quantile="TOTAL"):
    return serija(KODAS, geo, FAILAS, reason=reason, quantile=quantile,
                  sex="T", age="Y_GE16", unit="PC")


def rodiklis() -> Rodiklis:
    lt, es = _s("LT"), _s("EU27_2020")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)

    # 1 grafikas – Lietuva ir ES
    f1 = go.Figure()
    linijos(f1, [("Lietuva", lt, SERIJOS[0]), ("ES-27", es, SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f1, t("Negavo reikalingos medicininės pagalbos dėl laukimo eilių", "Unmet need for medical care due to waiting lists"),
            t("Gyventojų dalis, %, per pastaruosius 12 mėnesių", "Share of population, %, in the past 12 months"), _salt(),
            nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    # 2 grafikas – pajamų nelygybė Lietuvoje
    q1, q5 = _s("LT", quantile="QU1"), _s("LT", quantile="QU5")
    f2 = go.Figure()
    linijos(f2, [(t("20 % mažiausias pajamas gaunančių", "Lowest-income 20%"), q1, SERIJOS[1]),
                 (t("20 % didžiausias pajamas gaunančių", "Highest-income 20%"), q5, SERIJOS[0])],
            zenklas=False, zymekliai=True)
    stilius(f2, t("Laukimo eilės pagal pajamas Lietuvoje", "Waiting lists by income in Lithuania"),
            t("Gyventojų dalis, %, negavusių pagalbos dėl laukimo eilių", "Share of population, %, with unmet need due to waiting lists"), _salt(),
            nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    # 3 grafikas – visi trys barjerai (ES socialinių teisių švieslentės rodiklis)
    lt3, es3 = _s("LT", "TXP_TFAR_WLIST"), _s("EU27_2020", "TXP_TFAR_WLIST")
    f3 = go.Figure()
    linijos(f3, [("Lietuva", lt3, SERIJOS[0]), ("ES-27", es3, SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f3, t("Negavo pagalbos dėl kainos, atstumo arba eilių", "Unmet need due to cost, distance or waiting lists"),
            t("Gyventojų dalis, % (ES socialinių teisių švieslentės rodiklis)", "Share of population, % (EU Social Scoreboard indicator)"), _salt(),
            nulio_linija=False, metiniai=True)
    f3.update_yaxes(rangemode="tozero")

    lentele = (lt.rename("LT_eiles_proc").to_frame().join(es.rename("ES27_eiles_proc"))
               .join(q1.rename("LT_1_kvintilis_proc")).join(q5.rename("LT_5_kvintilis_proc"))
               .join(lt3.rename("LT_kaina_atstumas_eiles_proc")).join(es3.rename("ES27_kaina_atstumas_eiles_proc")))
    lentele.insert(0, "metai", lentele.index.year)

    santykis = pask / es.iloc[-1] if es.index[-1] == lt.index[-1] else None
    kryptis = t("sumažėjo", "fell by") if pokytis < 0 else t("padidėjo", "rose by")

    _dalys = [dalis(t("Mažiausių pajamų 20 % gyventojų", "Lowest-income 20% of the population"), q1, "mazesne", SLENKSTIS),
              dalis(t("Didžiausių pajamų 20 % gyventojų", "Highest-income 20% of the population"), q5, "mazesne", SLENKSTIS),
              dalis(t("Negavo dėl kainos, atstumo ar eilių", "Unmet need due to cost, distance or waiting lists"), lt3, "mazesne", SLENKSTIS)]
    return Rodiklis(
        dalys=_dalys,
        id="sveikatos-prieziuros-eiles",
        pavadinimas=t("Negavo gydymo dėl laukimo eilių", "Unmet medical need due to waiting lists"),
        trumpas_aprasas=t("16 m. ir vyresnių gyventojų, apklausos duomenys", "of people aged 16+, survey data"),
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai dalis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} proc. punkto; "
                             f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)} proc. punkto; kitu atveju – stabilu. "
                             "Mažesni pokyčiai gali būti atsitiktiniai, nes tai apklausos duomenys.",
                             f"Improving when the share falls by more than {sk(SLENKSTIS, False)} percentage point in a "
                             f"year; worsening when it rises by more than {sk(SLENKSTIS, False)} percentage point; "
                             "otherwise stable. Smaller changes may be random, as these are survey data."),
        vertinimo_paaiskinimas=t(f"{metai} m. {sk(pask, False)} % gyventojų negavo reikalingos medicininės pagalbos dėl "
                                 f"laukimo eilių ({ankst} m. – {sk(pries, False)} %). Dalis {kryptis} "
                                 f"{sk(abs(pokytis), False)} proc. punkto."
                                 + (f" Tai {sk(santykis, False)} karto daugiau nei ES vidurkis ({sk(es.iloc[-1], False)} %)."
                                    if santykis else ""),
                                 f"In {metai}, {sk(pask, False)}% of the population did not receive needed medical care "
                                 f"because of waiting lists ({ankst}: {sk(pries, False)}%). The share {kryptis} "
                                 f"{sk(abs(pokytis), False)} percentage points."
                                 + (f" This is {sk(santykis, False)} times the EU average ({sk(es.iloc[-1], False)}%)."
                                    if santykis else "")),
        sparkline=lt[lt.index.year >= 2015],
        grafikai=[f1, f2, f3],
        apibrezimas=t("16 m. ir vyresnių gyventojų dalis, kurie per pastaruosius 12 mėnesių nurodė, kad jiems reikėjo "
                      "medicininės apžiūros ar gydymo, bet jo negavo dėl per ilgos laukimo eilės. "
                      "Skaičiuojama nuo visų gyventojų, įskaitant tuos, kuriems pagalbos nereikėjo.",
                      "Share of people aged 16 and over who reported that in the past 12 months they needed a medical "
                      "examination or treatment but did not receive it because the waiting list was too long. "
                      "Calculated over the whole population, including those who did not need care."),
        pastabos=[
            t("Tai gyventojų apklausos (EU-SILC) rodiklis, o ne faktinis laukimo laikas. Dokumente numatytas rodiklis – "
              "pacientų, gavusių paslaugą per X valandų ar dienų, dalis – viešai neprieinamas atsisiuntimui.",
              "This is a population survey (EU-SILC) indicator, not actual waiting time. The planned indicator – the "
              "share of patients served within X hours or days – is not publicly available for download."),
            t("Faktinius laukimo pas specialistus duomenis (IPR IS) galima peržiūrėti OSP pacientų eilių švieslentėje, "
              "tačiau jų negalima atsisiųsti; rekomenduojama kreiptis į VLK ar SAM dėl duomenų atvėrimo.",
              "Actual waiting data for specialists (IPR IS) can be viewed on the OSP patient queue dashboard but cannot "
              "be downloaded; it is recommended to ask the National Health Insurance Fund or the Ministry of Health to open the data."),
            t("Naujausių metų duomenys gali būti preliminarūs.", "Data for the latest year may be provisional."),
        ],
        saltiniai=[("Eurostat – hlth_silc_08", "https://ec.europa.eu/eurostat/databrowser/view/hlth_silc_08/default/table?lang=en"),
                   (t("OSP – pacientų eilių švieslentė", "OSP – patient queue dashboard (in Lithuanian)"), "https://osp.stat.gov.lt/pacientu-eiles"),
                   (t("VLK – kur ir kiek reikia laukti", "National Health Insurance Fund – waiting times (in Lithuanian)"),
                    "https://ligoniukasa.lrv.lt/lt/paslaugos/e-paslaugos/kur-ir-kiek-reikia-laukti-norint-gauti-sveikatos-prieziuros-paslaugas/")],
        papildomai=[(f"{sk(es.iloc[-1], False)} %", t(f"ES-27 vidurkis, {es.index[-1].year} m.", f"EU-27 average, {es.index[-1].year}")),
                    (f"{sk(q1.iloc[-1], False)} % / {sk(q5.iloc[-1], False)} %",
                     t(f"mažiausias / didžiausias pajamas gaunantys, {q1.index[-1].year} m.",
                       f"lowest / highest income groups, {q1.index[-1].year}"))],
        lentele=lentele,
    )
