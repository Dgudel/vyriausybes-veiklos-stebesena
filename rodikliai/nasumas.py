"""3.3 Darbo našumas (Eurostat nama_10_lp_ulc)."""
from .bendra import dalis, Rodiklis, ivertink, sk, t
from .ekonomika_bendra import grafikas
from .eurostat_duomenys import serija

SLENKSTIS = 0.5     # % per metus


def rodiklis() -> Rodiklis:
    aug = serija("nama_10_lp_ulc", "LT", unit="PCH_PRE", na_item="RLPR_HW")
    aug_es = serija("nama_10_lp_ulc", "EU27_2020", unit="PCH_PRE", na_item="RLPR_HW")
    lygis = serija("nama_10_lp_ulc", "LT", unit="PC_EU27_2020_MPPS_CP", na_item="NLPR_HW")
    idx_lt = serija("nama_10_lp_ulc", "LT", unit="I15", na_item="RLPR_HW")
    idx_es = serija("nama_10_lp_ulc", "EU27_2020", unit="I15", na_item="RLPR_HW")

    pask, metai = aug.iloc[-1], aug.index[-1].year
    busena = ivertink(pask, "didesne", SLENKSTIS)
    vid5 = aug.iloc[-5:].mean()

    g1 = grafikas([("Lietuva", idx_lt), ("ES-27", idx_es)], t("Realus darbo našumas vienai dirbtai valandai", "Real labour productivity per hour worked"),
                  t("Indeksas, 2015 m. = 100", "Index, 2015 = 100"), "Šaltinis: Eurostat, nama_10_lp_ulc", nuo="2005-01-01",
                  vnt="", nulio_linija=False, nuo_nulio=False, metiniai=True)
    g1.add_hline(y=100, line=dict(color="#52514e", width=1, dash="dot"))
    g2 = grafikas([("Lietuva", lygis)], t("Darbo našumas vienai valandai, palyginti su ES", "Labour productivity per hour relative to the EU"),
                  t("Pagal perkamosios galios standartą, ES-27 = 100", "In purchasing power standards, EU-27 = 100"), "Šaltinis: Eurostat, nama_10_lp_ulc",
                  nuo="2005-01-01", vnt="", nulio_linija=False, metiniai=True)
    g2.add_hline(y=100, line=dict(color="#52514e", width=1, dash="dot"),
                 annotation_text=t("ES vidurkis", "EU average"), annotation_position="top left")
    g2.update_yaxes(range=[0, 110])

    lentele = (aug.rename("LT_nasumo_pokytis_proc").to_frame().join(aug_es.rename("ES27_nasumo_pokytis_proc"))
               .join(lygis.rename("LT_nasumas_ES100")))
    lentele = lentele[lentele.index >= "2005-01-01"]
    lentele.insert(0, "metai", lentele.index.year)


    _dalys = [dalis(t("Našumas, palyginti su ES (PGS, ES = 100)", "Productivity relative to the EU (PPS, EU = 100)"), lygis,
                    "didesne", 1.0, vienetai="", slenkscio_vnt=t(" punkto", " points"))]
    return Rodiklis(
        dalys=_dalys,
        id="darbo-nasumas", pavadinimas=t("Darbo našumas", "Labour productivity"),
        trumpas_aprasas=t("realus pokytis per metus, vienai valandai", "real annual change, per hour worked"), reiksme=pask, vienetai="%",
        laikotarpis=str(metai), busena=busena,
        vertinimo_taisykle=t(f"Gerėja, kai realus darbo našumas vienai dirbtai valandai per metus padidėja daugiau nei "
                             f"{sk(SLENKSTIS, False)} %; prastėja, kai sumažėja daugiau nei {sk(SLENKSTIS, False)} %; "
                             "kitu atveju – stabilu.",
                             f"Improving when real labour productivity per hour worked rises by more than "
                             f"{sk(SLENKSTIS, False)}% in a year; worsening when it falls by more than {sk(SLENKSTIS, False)}%; "
                             "otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. realus darbo našumas vienai dirbtai valandai pakito {sk(pask)} % "
                                 f"(ES – {sk(aug_es.iloc[-1])} %). Pastarųjų penkerių metų vidutinis pokytis – {sk(vid5)} % per metus. "
                                 f"Pagal perkamosios galios standartą Lietuvos našumas siekia {sk(lygis.iloc[-1], False)} % ES vidurkio.",
                                 f"In {metai}, real labour productivity per hour worked changed by {sk(pask)}% "
                                 f"(EU: {sk(aug_es.iloc[-1])}%). The average change over the last five years was "
                                 f"{sk(vid5)}% a year. In purchasing power standards, Lithuania's productivity is "
                                 f"{sk(lygis.iloc[-1], False)}% of the EU average."),
        sparkline=aug[aug.index >= "2010-01-01"], grafikai=[g1, g2],
        apibrezimas=t("Pridėtinė vertė (BVP) palyginamosiomis kainomis, tenkanti vienai faktiškai dirbtai valandai. "
                      "Rodo, ar ekonomikos augimas grindžiamas didesniu darbo efektyvumu, o ne vien daugiau dirbant.",
                      "Value added (GDP) at constant prices per hour actually worked. Shows whether economic growth is "
                      "driven by greater labour efficiency rather than simply working more."),
        pastabos=[t("Metiniai duomenys; naujausi metai gali būti tikslinami.", "Annual data; the latest year may be revised."),
                  t("Lygis, palyginti su ES, priklauso ir nuo kainų lygio skirtumų (PGS), todėl gali kisti kita kryptimi nei "
                    "realus našumo pokytis.",
                    "The level relative to the EU also depends on price level differences (PPS), so it may move in a "
                    "different direction from real productivity growth.")],
        saltiniai=[("Eurostat – nama_10_lp_ulc", "https://ec.europa.eu/eurostat/databrowser/view/nama_10_lp_ulc/default/table?lang=en"),
                   (t("OSP – pridėtinė vertė vienai dirbtai valandai", "Official Statistics Portal – value added per hour worked"), "https://osp.stat.gov.lt/")],
        papildomai=[(f"{sk(lygis.iloc[-1], False)}", t(f"našumas vienai valandai, ES = 100 (PGS), {lygis.index[-1].year} m.",
                                                       f"productivity per hour, EU = 100 (PPS), {lygis.index[-1].year}")),
                    (f"{sk(vid5)} %", t("vidutinis metinis realaus našumo pokytis per 5 metus", "average annual real productivity change over 5 years"))],
        lentele=lentele,
    )
