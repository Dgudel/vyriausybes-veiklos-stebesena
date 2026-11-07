"""3.1 Realus BVP augimas (Eurostat namq_10_gdp) ir BVP vienam gyventojui (nama_10_pc)."""
from .bendra import Rodiklis, ivertink, sk, zmoniu_laikotarpis
from .ekonomika_bendra import grafikas
from .eurostat_duomenys import laikotarpis, serija

AUGIMAS_GERAS, NUOSMUKIS = 1.0, 0.0   # % per metus


def rodiklis() -> Rodiklis:
    f = dict(na_item="B1GQ", unit="CLV_PCH_SM", s_adj="SCA")
    lt, es = serija("namq_10_gdp", "LT", **f), serija("namq_10_gdp", "EU27_2020", **f)
    pc = dict(na_item="B1GQ", unit="PC_EU27_2020_HAB_MPPS_CP")
    pc_lt = serija("nama_10_pc", "LT", **pc)

    pask = lt.iloc[-1]
    laik = laikotarpis(lt.index[-1], "Q")
    busena = "gereja" if pask >= AUGIMAS_GERAS else ("prasteja" if pask < NUOSMUKIS else "stabilu")
    pask4 = lt.iloc[-4:].mean()

    g1 = grafikas([("Lietuva", lt), ("ES-27", es)], "Realus BVP pokytis",
                  "Palyginti su tuo pačiu ketvirčiu prieš metus, %; pašalinta sezono ir darbo dienų įtaka",
                  "Šaltinis: Eurostat, namq_10_gdp", nuo="2015-01-01", zenklas=True, nuo_nulio=False)
    g2 = grafikas([("Lietuva", pc_lt)], "BVP vienam gyventojui pagal perkamosios galios standartą",
                  "ES-27 vidurkis = 100", "Šaltinis: Eurostat, nama_10_pc", nuo="2000-01-01", vnt="",
                  nulio_linija=False, metiniai=True, dec=1)
    g2.add_hline(y=100, line=dict(color="#52514e", width=1, dash="dot"),
                 annotation_text="ES vidurkis", annotation_position="top left")
    g2.update_yaxes(range=[0, 110])

    lentele = lt.rename("LT_BVP_realus_pokytis_proc").to_frame().join(es.rename("ES27_BVP_realus_pokytis_proc"))
    lentele = lentele[lentele.index >= "2015-01-01"]
    lentele.insert(0, "laikotarpis", [laikotarpis(d, "Q") for d in lentele.index])

    return Rodiklis(
        id="bvp-augimas", pavadinimas="Realus BVP augimas",
        trumpas_aprasas="per metus", reiksme=pask, vienetai="%", laikotarpis=laik, busena=busena,
        vertinimo_taisykle=(f"Gerėja (ekonomika auga), kai realus BVP per metus išauga bent {sk(AUGIMAS_GERAS, False)} %; "
                            "prastėja, kai BVP mažėja (nuosmukis); kitu atveju – stabilu (augimas silpnas)."),
        vertinimo_paaiskinimas=(f"{zmoniu_laikotarpis(laik)} Lietuvos realus BVP per metus pakito {sk(pask)} % "
                                f"(ES – {sk(es.iloc[-1])} %). Pastarųjų keturių ketvirčių vidutinis augimas – {sk(pask4, False)} %."),
        sparkline=lt[lt.index >= "2019-01-01"], grafikai=[g1, g2],
        apibrezimas=("Bendrojo vidaus produkto pokytis palyginamosiomis kainomis (grandininiai apimties indeksai), "
                     "palyginti su tuo pačiu praėjusių metų ketvirčiu; pašalinta sezono ir darbo dienų skaičiaus įtaka. "
                     "Papildomai – BVP vienam gyventojui pagal perkamosios galios standartą, palyginti su ES vidurkiu."),
        pastabos=["Naujausių ketvirčių duomenys yra išankstiniai ir vėliau tikslinami.",
                  "BVP vienam gyventojui (PGS) rodo pajamų lygį, palyginti su ES, o realus BVP pokytis – augimo tempą; "
                  "tai skirtingi rodikliai."],
        saltiniai=[("Eurostat – namq_10_gdp", "https://ec.europa.eu/eurostat/databrowser/view/namq_10_gdp/default/table?lang=en"),
                   ("Eurostat – nama_10_pc", "https://ec.europa.eu/eurostat/databrowser/view/nama_10_pc/default/table?lang=en"),
                   ("OSP – nacionalinės sąskaitos", "https://osp.stat.gov.lt/")],
        papildomai=[(f"{sk(pc_lt.iloc[-1], False)}", f"BVP vienam gyventojui (PGS), ES = 100, {pc_lt.index[-1].year} m."),
                    (f"{sk(es.iloc[-1])} %", f"ES-27 realus BVP pokytis, {zmoniu_laikotarpis(laik)}")],
        lentele=lentele,
    )
