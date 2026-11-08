"""2.1 Negavo gydymo dėl laukimo eilių (Eurostat apklausos rodiklis)."""
import plotly.graph_objects as go

from .bendra import dalis, SERIJOS, TEKSTAS_ANTR, Rodiklis, ivertink, linijos, sk, stilius
from .eurostat_duomenys import serija

KODAS = "hlth_silc_08"
FAILAS = "hlth_silc_08_nepatenkinti_poreikiai.csv"
SLENKSTIS = 0.3     # proc. punkto: apklausos duomenys, mažesni pokyčiai gali būti atsitiktiniai
SALTINIS = "Šaltinis: Eurostat, hlth_silc_08 (EU-SILC), 16 m. ir vyresni gyventojai"


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
    stilius(f1, "Negavo reikalingos medicininės pagalbos dėl laukimo eilių",
            "Gyventojų dalis, %, per pastaruosius 12 mėnesių", SALTINIS,
            nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    # 2 grafikas – pajamų nelygybė Lietuvoje
    q1, q5 = _s("LT", quantile="QU1"), _s("LT", quantile="QU5")
    f2 = go.Figure()
    linijos(f2, [("20 % mažiausias pajamas gaunančių", q1, SERIJOS[1]),
                 ("20 % didžiausias pajamas gaunančių", q5, SERIJOS[0])],
            zenklas=False, zymekliai=True)
    stilius(f2, "Laukimo eilės pagal pajamas Lietuvoje",
            "Gyventojų dalis, %, negavusių pagalbos dėl laukimo eilių", SALTINIS,
            nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    # 3 grafikas – visi trys barjerai (ES socialinių teisių švieslentės rodiklis)
    lt3, es3 = _s("LT", "TXP_TFAR_WLIST"), _s("EU27_2020", "TXP_TFAR_WLIST")
    f3 = go.Figure()
    linijos(f3, [("Lietuva", lt3, SERIJOS[0]), ("ES-27", es3, SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f3, "Negavo pagalbos dėl kainos, atstumo arba eilių",
            "Gyventojų dalis, % (ES socialinių teisių švieslentės rodiklis)", SALTINIS,
            nulio_linija=False, metiniai=True)
    f3.update_yaxes(rangemode="tozero")

    lentele = (lt.rename("LT_eiles_proc").to_frame().join(es.rename("ES27_eiles_proc"))
               .join(q1.rename("LT_1_kvintilis_proc")).join(q5.rename("LT_5_kvintilis_proc"))
               .join(lt3.rename("LT_kaina_atstumas_eiles_proc")).join(es3.rename("ES27_kaina_atstumas_eiles_proc")))
    lentele.insert(0, "metai", lentele.index.year)

    santykis = pask / es.iloc[-1] if es.index[-1] == lt.index[-1] else None
    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"

    _dalys = [dalis("Mažiausių pajamų 20 % gyventojų", q1, "mazesne", SLENKSTIS),
              dalis("Didžiausių pajamų 20 % gyventojų", q5, "mazesne", SLENKSTIS),
              dalis("Negavo dėl kainos, atstumo ar eilių", lt3, "mazesne", SLENKSTIS)]
    return Rodiklis(
        dalys=_dalys,
        id="sveikatos-prieziuros-eiles",
        pavadinimas="Negavo gydymo dėl laukimo eilių",
        trumpas_aprasas="16 m. ir vyresnių gyventojų, apklausos duomenys",
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai dalis per metus sumažėja daugiau nei {sk(SLENKSTIS, False)} proc. punkto; "
                            f"prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)} proc. punkto; kitu atveju – stabilu. "
                            "Mažesni pokyčiai gali būti atsitiktiniai, nes tai apklausos duomenys."),
        vertinimo_paaiskinimas=(f"{metai} m. {sk(pask, False)} % gyventojų negavo reikalingos medicininės pagalbos dėl "
                                f"laukimo eilių ({ankst} m. – {sk(pries, False)} %). Dalis {kryptis} "
                                f"{sk(abs(pokytis), False)} proc. punkto."
                                + (f" Tai {sk(santykis, False)} karto daugiau nei ES vidurkis ({sk(es.iloc[-1], False)} %)."
                                   if santykis else "")),
        sparkline=lt[lt.index.year >= 2015],
        grafikai=[f1, f2, f3],
        apibrezimas=("16 m. ir vyresnių gyventojų dalis, kurie per pastaruosius 12 mėnesių nurodė, kad jiems reikėjo "
                     "medicininės apžiūros ar gydymo, bet jo negavo dėl per ilgos laukimo eilės. "
                     "Skaičiuojama nuo visų gyventojų, įskaitant tuos, kuriems pagalbos nereikėjo."),
        pastabos=[
            "Tai gyventojų apklausos (EU-SILC) rodiklis, o ne faktinis laukimo laikas. Dokumente numatytas rodiklis – "
            "pacientų, gavusių paslaugą per X valandų ar dienų, dalis – viešai neprieinamas atsisiuntimui.",
            "Faktinius laukimo pas specialistus duomenis (IPR IS) galima peržiūrėti OSP pacientų eilių švieslentėje, "
            "tačiau jų negalima atsisiųsti; rekomenduojama kreiptis į VLK ar SAM dėl duomenų atvėrimo.",
            "Naujausių metų duomenys gali būti preliminarūs.",
        ],
        saltiniai=[("Eurostat – hlth_silc_08", "https://ec.europa.eu/eurostat/databrowser/view/hlth_silc_08/default/table?lang=en"),
                   ("OSP – pacientų eilių švieslentė", "https://osp.stat.gov.lt/pacientu-eiles"),
                   ("VLK – kur ir kiek reikia laukti", "https://ligoniukasa.lrv.lt/lt/paslaugos/e-paslaugos/kur-ir-kiek-reikia-laukti-norint-gauti-sveikatos-prieziuros-paslaugas/")],
        papildomai=[(f"{sk(es.iloc[-1], False)} %", f"ES-27 vidurkis, {es.index[-1].year} m."),
                    (f"{sk(q1.iloc[-1], False)} % / {sk(q5.iloc[-1], False)} %",
                     f"mažiausias / didžiausias pajamas gaunantys, {q1.index[-1].year} m.")],
        lentele=lentele,
    )
