"""3.3 Darbo našumas (Eurostat nama_10_lp_ulc)."""
from .bendra import dalis, Rodiklis, ivertink, sk
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

    g1 = grafikas([("Lietuva", idx_lt), ("ES-27", idx_es)], "Realus darbo našumas vienai dirbtai valandai",
                  "Indeksas, 2015 m. = 100", "Šaltinis: Eurostat, nama_10_lp_ulc", nuo="2005-01-01",
                  vnt="", nulio_linija=False, nuo_nulio=False, metiniai=True)
    g1.add_hline(y=100, line=dict(color="#52514e", width=1, dash="dot"))
    g2 = grafikas([("Lietuva", lygis)], "Darbo našumas vienai valandai, palyginti su ES",
                  "Pagal perkamosios galios standartą, ES-27 = 100", "Šaltinis: Eurostat, nama_10_lp_ulc",
                  nuo="2005-01-01", vnt="", nulio_linija=False, metiniai=True)
    g2.add_hline(y=100, line=dict(color="#52514e", width=1, dash="dot"),
                 annotation_text="ES vidurkis", annotation_position="top left")
    g2.update_yaxes(range=[0, 110])

    lentele = (aug.rename("LT_nasumo_pokytis_proc").to_frame().join(aug_es.rename("ES27_nasumo_pokytis_proc"))
               .join(lygis.rename("LT_nasumas_ES100")))
    lentele = lentele[lentele.index >= "2005-01-01"]
    lentele.insert(0, "metai", lentele.index.year)


    _dalys = [dalis("Našumas, palyginti su ES (PGS, ES = 100)", lygis, "didesne", 1.0, vienetai="", slenkscio_vnt=" punkto")]
    return Rodiklis(
        dalys=_dalys,
        id="darbo-nasumas", pavadinimas="Darbo našumas",
        trumpas_aprasas="realus pokytis per metus, vienai valandai", reiksme=pask, vienetai="%",
        laikotarpis=str(metai), busena=busena,
        vertinimo_taisykle=(f"Gerėja, kai realus darbo našumas vienai dirbtai valandai per metus padidėja daugiau nei "
                            f"{sk(SLENKSTIS, False)} %; prastėja, kai sumažėja daugiau nei {sk(SLENKSTIS, False)} %; "
                            "kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. realus darbo našumas vienai dirbtai valandai pakito {sk(pask)} % "
                                f"(ES – {sk(aug_es.iloc[-1])} %). Pastarųjų penkerių metų vidutinis pokytis – {sk(vid5)} % per metus. "
                                f"Pagal perkamosios galios standartą Lietuvos našumas siekia {sk(lygis.iloc[-1], False)} % ES vidurkio."),
        sparkline=aug[aug.index >= "2010-01-01"], grafikai=[g1, g2],
        apibrezimas=("Pridėtinė vertė (BVP) palyginamosiomis kainomis, tenkanti vienai faktiškai dirbtai valandai. "
                     "Rodo, ar ekonomikos augimas grindžiamas didesniu darbo efektyvumu, o ne vien daugiau dirbant."),
        pastabos=["Metiniai duomenys; naujausi metai gali būti tikslinami.",
                  "Lygis, palyginti su ES, priklauso ir nuo kainų lygio skirtumų (PGS), todėl gali kisti kita kryptimi nei "
                  "realus našumo pokytis."],
        saltiniai=[("Eurostat – nama_10_lp_ulc", "https://ec.europa.eu/eurostat/databrowser/view/nama_10_lp_ulc/default/table?lang=en"),
                   ("OSP – pridėtinė vertė vienai dirbtai valandai", "https://osp.stat.gov.lt/")],
        papildomai=[(f"{sk(lygis.iloc[-1], False)}", f"našumas vienai valandai, ES = 100 (PGS), {lygis.index[-1].year} m."),
                    (f"{sk(vid5)} %", "vidutinis metinis realaus našumo pokytis per 5 metus")],
        lentele=lentele,
    )
