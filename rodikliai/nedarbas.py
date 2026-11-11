"""3.2 Nedarbo lygis (Eurostat une_rt_m) ir užimtumo lygis (lfsi_emp_q)."""
from .bendra import dalis, Rodiklis, ivertink, sk, zmoniu_laikotarpis, t
from .ekonomika_bendra import grafikas
from .eurostat_duomenys import laikotarpis, serija

SLENKSTIS = 0.3     # proc. punkto per metus


def rodiklis() -> Rodiklis:
    f = dict(s_adj="SA", age="TOTAL", unit="PC_ACT", sex="T")
    lt, es = serija("une_rt_m", "LT", **f), serija("une_rt_m", "EU27_2020", **f)
    jaun = serija("une_rt_m", "LT", s_adj="SA", age="Y_LT25", unit="PC_ACT", sex="T")
    e = dict(indic_em="EMP_LFS", s_adj="SA", age="Y20-64", unit="PC_POP", sex="T")
    u_lt, u_es = serija("lfsi_emp_q", "LT", **e), serija("lfsi_emp_q", "EU27_2020", **e)

    pask, data = lt.iloc[-1], lt.index[-1]
    pries_metus = lt.get(data - __import__("pandas").DateOffset(years=1))
    pokytis = pask - pries_metus
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)
    laik = laikotarpis(data, "M")

    g1 = grafikas([("Lietuva", lt), ("ES-27", es), (t("Lietuva – jaunimas iki 25 m.", "Lithuania – under 25"), jaun)],
                  t("Nedarbo lygis", "Unemployment rate"),
                  t("Bedarbių dalis darbo jėgoje, %; pašalinta sezono įtaka", "Unemployed as a share of the labour force, %; seasonally adjusted"),
                  "Šaltinis: Eurostat, une_rt_m", nuo="2015-01-01")
    g2 = grafikas([("Lietuva", u_lt), ("ES-27", u_es)], t("Užimtumo lygis, 20–64 m.", "Employment rate, aged 20–64"),
                  t("Dirbančiųjų dalis gyventojų, %; ES tikslas 2030 m. – 78 %", "Employed as a share of the population, %; EU 2030 target – 78%"),
                  "Šaltinis: Eurostat, lfsi_emp_q", nuo="2015-01-01", nulio_linija=False)

    lentele = (lt.rename("LT_nedarbas_proc").to_frame().join(es.rename("ES27_nedarbas_proc"))
               .join(jaun.rename("LT_jaunimo_nedarbas_proc")))
    lentele = lentele[lentele.index >= "2015-01-01"]
    lentele.insert(0, "laikotarpis", [laikotarpis(d, "M") for d in lentele.index])

    kryptis = t("sumažėjo", "down") if pokytis < 0 else t("padidėjo", "up")

    _dalys = [dalis(t("Jaunimo (iki 25 m.) nedarbas", "Youth unemployment (under 25)"), jaun, "mazesne", 1.0),
              dalis(t("Užimtumo lygis (20–64 m.)", "Employment rate (aged 20–64)"), u_lt, "didesne", SLENKSTIS)]
    return Rodiklis(
        dalys=_dalys,
        id="nedarbas", pavadinimas=t("Nedarbo lygis", "Unemployment rate"),
        trumpas_aprasas=t("darbo jėgos", "of the labour force"), reiksme=pask, vienetai="%", laikotarpis=laik, busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Lyginama su tuo pačiu mėnesiu prieš metus. Gerėja, kai nedarbo lygis sumažėja daugiau nei "
                             f"{sk(SLENKSTIS, False)} proc. punkto; prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)} "
                             "proc. punkto; kitu atveju – stabilu.",
                             f"Compared with the same month a year earlier. Improving when the unemployment rate falls "
                             f"by more than {sk(SLENKSTIS, False)} percentage point; worsening when it rises by more than "
                             f"{sk(SLENKSTIS, False)} percentage point; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{zmoniu_laikotarpis(laik, kada=True)} nedarbo lygis buvo {sk(pask, False)} % "
                                 f"(prieš metus – {sk(pries_metus, False)} %; {kryptis} {sk(abs(pokytis), False)} proc. punkto). "
                                 f"ES vidurkis – {sk(es.iloc[-1], False)} %.",
                                 f"In {zmoniu_laikotarpis(laik)}, the unemployment rate was {sk(pask, False)}% "
                                 f"(a year earlier: {sk(pries_metus, False)}%; {kryptis} {sk(abs(pokytis), False)} "
                                 f"percentage points). The EU average is {sk(es.iloc[-1], False)}%."),
        sparkline=lt[lt.index >= "2019-01-01"], grafikai=[g1, g2],
        apibrezimas=t("15–74 m. bedarbių dalis darbo jėgoje (Tarptautinės darbo organizacijos apibrėžtis), pašalinus "
                      "sezono įtaką. Papildomai – užimtumo lygis (20–64 m. dirbančiųjų dalis gyventojų).",
                      "Unemployed people aged 15–74 as a share of the labour force (International Labour Organization "
                      "definition), seasonally adjusted. Also shown: the employment rate (share of people aged 20–64 in work)."),
        pastabos=[t("Mėnesiniai Eurostat nedarbo duomenys apskaičiuojami pagal Darbo jėgos tyrimą ir vėliau tikslinami.",
                    "Eurostat's monthly unemployment data are based on the Labour Force Survey and are revised later."),
                  t("Užimtųjų skaičius (OSP sd002731) nėra užimtumo lygis – švieslentėje naudojamas užimtumo lygis, %.",
                    "The number of employed people (OSP sd002731) is not the employment rate – the dashboard uses the employment rate, %.")],
        saltiniai=[("Eurostat – une_rt_m", "https://ec.europa.eu/eurostat/databrowser/view/une_rt_m/default/table?lang=en"),
                   ("Eurostat – lfsi_emp_q", "https://ec.europa.eu/eurostat/databrowser/view/lfsi_emp_q/default/table?lang=en")],
        papildomai=[(f"{sk(u_lt.iloc[-1], False)} %", t(f"užimtumo lygis 20–64 m., {zmoniu_laikotarpis(laikotarpis(u_lt.index[-1], 'Q'))} "
                                                       f"(ES – {sk(u_es.iloc[-1], False)} %)",
                                                       f"employment rate, aged 20–64, {zmoniu_laikotarpis(laikotarpis(u_lt.index[-1], 'Q'))} "
                                                       f"(EU: {sk(u_es.iloc[-1], False)}%)")),
                    (f"{sk(jaun.iloc[-1], False)} %", t(f"jaunimo (iki 25 m.) nedarbas, {zmoniu_laikotarpis(laikotarpis(jaun.index[-1], 'M'))}",
                                                        f"youth unemployment (under 25), {zmoniu_laikotarpis(laikotarpis(jaun.index[-1], 'M'))}"))],
        lentele=lentele,
    )
