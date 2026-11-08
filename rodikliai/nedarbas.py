"""3.2 Nedarbo lygis (Eurostat une_rt_m) ir užimtumo lygis (lfsi_emp_q)."""
from .bendra import dalis, Rodiklis, ivertink, sk, zmoniu_laikotarpis
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

    g1 = grafikas([("Lietuva", lt), ("ES-27", es), ("Lietuva – jaunimas iki 25 m.", jaun)],
                  "Nedarbo lygis", "Bedarbių dalis darbo jėgoje, %; pašalinta sezono įtaka",
                  "Šaltinis: Eurostat, une_rt_m", nuo="2015-01-01")
    g2 = grafikas([("Lietuva", u_lt), ("ES-27", u_es)], "Užimtumo lygis, 20–64 m.",
                  "Dirbančiųjų dalis gyventojų, %; ES tikslas 2030 m. – 78 %",
                  "Šaltinis: Eurostat, lfsi_emp_q", nuo="2015-01-01", nulio_linija=False)

    lentele = (lt.rename("LT_nedarbas_proc").to_frame().join(es.rename("ES27_nedarbas_proc"))
               .join(jaun.rename("LT_jaunimo_nedarbas_proc")))
    lentele = lentele[lentele.index >= "2015-01-01"]
    lentele.insert(0, "laikotarpis", [laikotarpis(d, "M") for d in lentele.index])

    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"

    _dalys = [dalis("Jaunimo (iki 25 m.) nedarbas", jaun, "mazesne", 1.0),
              dalis("Užimtumo lygis (20–64 m.)", u_lt, "didesne", SLENKSTIS)]
    return Rodiklis(
        dalys=_dalys,
        id="nedarbas", pavadinimas="Nedarbo lygis",
        trumpas_aprasas="darbo jėgos", reiksme=pask, vienetai="%", laikotarpis=laik, busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Lyginama su tuo pačiu mėnesiu prieš metus. Gerėja, kai nedarbo lygis sumažėja daugiau nei "
                            f"{sk(SLENKSTIS, False)} proc. punkto; prastėja, kai padidėja daugiau nei {sk(SLENKSTIS, False)} "
                            "proc. punkto; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{zmoniu_laikotarpis(laik, kada=True)} nedarbo lygis buvo {sk(pask, False)} % "
                                f"(prieš metus – {sk(pries_metus, False)} %; {kryptis} {sk(abs(pokytis), False)} proc. punkto). "
                                f"ES vidurkis – {sk(es.iloc[-1], False)} %."),
        sparkline=lt[lt.index >= "2019-01-01"], grafikai=[g1, g2],
        apibrezimas=("15–74 m. bedarbių dalis darbo jėgoje (Tarptautinės darbo organizacijos apibrėžtis), pašalinus "
                     "sezono įtaką. Papildomai – užimtumo lygis (20–64 m. dirbančiųjų dalis gyventojų)."),
        pastabos=["Mėnesiniai Eurostat nedarbo duomenys apskaičiuojami pagal Darbo jėgos tyrimą ir vėliau tikslinami.",
                  "Užimtųjų skaičius (OSP sd002731) nėra užimtumo lygis – švieslentėje naudojamas užimtumo lygis, %."],
        saltiniai=[("Eurostat – une_rt_m", "https://ec.europa.eu/eurostat/databrowser/view/une_rt_m/default/table?lang=en"),
                   ("Eurostat – lfsi_emp_q", "https://ec.europa.eu/eurostat/databrowser/view/lfsi_emp_q/default/table?lang=en")],
        papildomai=[(f"{sk(u_lt.iloc[-1], False)} %", f"užimtumo lygis 20–64 m., {zmoniu_laikotarpis(laikotarpis(u_lt.index[-1], 'Q'))} "
                                                     f"(ES – {sk(u_es.iloc[-1], False)} %)"),
                    (f"{sk(jaun.iloc[-1], False)} %", f"jaunimo (iki 25 m.) nedarbas, {zmoniu_laikotarpis(laikotarpis(jaun.index[-1], 'M'))}")],
        lentele=lentele,
    )
