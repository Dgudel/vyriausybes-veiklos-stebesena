"""2.3 Švietimo rezultatai: mokinių pasiekimai (PUPP – 10 kl., PISA – 15 m.)."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import dalis, DUOMENYS, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, t
from .eurostat_duomenys import serija

SLENKSTIS = 2.0     # proc. punkto: PUPP užduotys kasmet skirtingos, mažesni pokyčiai nelaikomi pokyčiu
PUPP_FAILAS = "pupp_salies_eilutes.csv"   # sugeneruoja pupp_rezultatai.py (NŠA PDF → šalies eilutės)


def pupp_serija(dalyko_pradzia: str) -> pd.DataFrame:
    """Šalies rezultatai pagal metus, sudėjus visus to dalyko variantus
    (pvz. matematika lietuvių, lenkų, rusų mokomąja kalba)."""
    d = pd.read_csv(DUOMENYS / PUPP_FAILAS)
    d = d[d["dalykas"].str.startswith(dalyko_pradzia)]
    balai = [f"b{i}" for i in range(1, 11)]
    g = d.groupby("metai")[["kandidatai"] + balai].sum()
    g["vidurkis"] = sum(g[f"b{i}"] * i for i in range(1, 11)) / g[balai].sum(axis=1)
    g["nepasieke_proc"] = (g["b1"] + g["b2"] + g["b3"]) / g["kandidatai"] * 100
    g["aukstas_proc"] = (g["b9"] + g["b10"]) / g["kandidatai"] * 100
    g.index = pd.to_datetime([f"{m}-01-01" for m in g.index])
    return g


def rodiklis() -> Rodiklis:
    mat, lt = pupp_serija("Matematika"), pupp_serija("Lietuvių")
    s = mat["nepasieke_proc"]
    pask, pries = s.iloc[-1], s.iloc[-2]
    metai, ankst = s.index[-1].year, s.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)
    vid3 = s.iloc[-4:-1].mean()   # ankstesnių 3 patikrinimų vidurkis – kontekstui

    # 1 – PUPP: nepasiekusių patenkinamo lygio dalis
    f1 = go.Figure()
    linijos(f1, [("Matematika", s, SERIJOS[0]), ("Lietuvių kalba", lt["nepasieke_proc"], SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f1, t("Nepasiekė patenkinamo lygio (PUPP, 10 klasė)", "Below the satisfactory level (PUPP, grade 10)"),
            t("Mokinių, gavusių 1–3 balus, dalis, %. 2020 m. patikrinimas nevyko",
              "Share of pupils scoring 1–3 points, %. No assessment in 2020"),
            t("Šaltinis: NŠA, PUPP rezultatai pagal savivaldybes (šalies eilutė)",
              "Source: National Agency for Education (NŠA), PUPP results by municipality (national row)"),
            nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    # 2 – PUPP vidurkiai
    f2 = go.Figure()
    linijos(f2, [("Matematika", mat["vidurkis"], SERIJOS[0]), ("Lietuvių kalba", lt["vidurkis"], SERIJOS[1])],
            vnt="", zenklas=False, dec=2, zymekliai=True, asis=(0, 10))
    stilius(f2, t("PUPP įvertinimų vidurkis", "PUPP mean score"), t("Balai (1–10 skalė)", "Points (1–10 scale)"),
            t("Šaltinis: NŠA, PUPP rezultatai", "Source: NŠA, PUPP results"), vnt="", nulio_linija=False, metiniai=True)
    f2.update_yaxes(range=[0, 10])

    # 3 – PISA: žemų pasiekimų 15-mečiai, Lietuva ir ES
    pisa = {k: (serija("sdg_04_40", "LT", field=k, sex="T", unit="PC"),
                serija("sdg_04_40", "EU27_2020", field=k, sex="T", unit="PC"))
            for k in ["EF461", "READ", "SCI"]}
    f3 = go.Figure()
    linijos(f3, [(t("Lietuva – matematika", "Lithuania – mathematics"), pisa["EF461"][0], SERIJOS[0]),
                 (t("ES-27 – matematika", "EU-27 – mathematics"), pisa["EF461"][1], SERIJOS[1]),
                 (t("Lietuva – skaitymas", "Lithuania – reading"), pisa["READ"][0], SERIJOS[2]),
                 (t("Lietuva – gamtos mokslai", "Lithuania – science"), pisa["SCI"][0], SERIJOS[3])],
            zenklas=False, zymekliai=True)
    stilius(f3, t("Žemų pasiekimų 15-mečiai (PISA)", "Low-achieving 15-year-olds (PISA)"),
            t("Mokinių, nepasiekusių 2-ojo (bazinio) lygio, dalis, %. Tyrimas vyksta kas 3–4 metus",
              "Share of pupils below level 2 (baseline), %. The survey takes place every 3–4 years"),
            t("Šaltinis: Eurostat, sdg_04_40 (EBPO PISA)", "Source: Eurostat, sdg_04_40 (OECD PISA)"), nulio_linija=False, metiniai=True)
    f3.update_yaxes(rangemode="tozero")

    lentele = pd.DataFrame({
        "metai": mat.index.year,
        "matematika_kandidatai": mat["kandidatai"].values,
        "matematika_nepasieke_proc": mat["nepasieke_proc"].round(2).values,
        "matematika_9_10_balu_proc": mat["aukstas_proc"].round(2).values,
        "matematika_vidurkis": mat["vidurkis"].round(2).values,
    }).merge(pd.DataFrame({
        "metai": lt.index.year,
        "lietuviu_nepasieke_proc": lt["nepasieke_proc"].round(2).values,
        "lietuviu_vidurkis": lt["vidurkis"].round(2).values,
    }), on="metai", how="outer")

    pm_lt, pm_es = pisa["EF461"][0], pisa["EF461"][1]
    kryptis = t("sumažėjo", "fell by") if pokytis < 0 else t("padidėjo", "rose by")
    balo = t(" balo", " points")

    _dalys = [dalis(t("Lietuvių k.: nepasiekė patenkinamo lygio", "Lithuanian: below the satisfactory level"),
                    lt["nepasieke_proc"], "mazesne", SLENKSTIS),
              dalis(t("Matematikos PUPP vidurkis", "Mathematics PUPP mean score"), mat["vidurkis"], "didesne", 0.2,
                    vienetai="", slenkscio_vnt=balo, dec=2),
              dalis(t("Lietuvių k. PUPP vidurkis", "Lithuanian PUPP mean score"), lt["vidurkis"], "didesne", 0.2,
                    vienetai="", slenkscio_vnt=balo, dec=2),
              dalis(t("PISA: žemi pasiekimai – matematika", "PISA: low achievement – mathematics"), pisa["EF461"][0], "mazesne", SLENKSTIS),
              dalis(t("PISA: žemi pasiekimai – skaitymas", "PISA: low achievement – reading"), pisa["READ"][0], "mazesne", SLENKSTIS),
              dalis(t("PISA: žemi pasiekimai – gamtos mokslai", "PISA: low achievement – science"), pisa["SCI"][0], "mazesne", SLENKSTIS)]
    return Rodiklis(
        dalys=_dalys,
        id="svietimo-pasiekimai",
        pavadinimas=t("Matematikos pasiekimai (PUPP)", "Mathematics achievement (PUPP)"),
        trumpas_aprasas=t("10 kl. mokinių nepasiekė patenkinamo lygio", "of grade 10 pupils below the satisfactory level"),
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Gerėja, kai nepasiekusių patenkinamo lygio dalis per metus sumažėja daugiau nei "
                             f"{sk(SLENKSTIS, False)} proc. punkto; prastėja, kai padidėja daugiau nei "
                             f"{sk(SLENKSTIS, False)} proc. punkto; kitu atveju – stabilu. Slenkstis didesnis, nes "
                             "patikrinimo užduotys kasmet skiriasi ir rezultatai svyruoja.",
                             f"Improving when the share below the satisfactory level falls by more than "
                             f"{sk(SLENKSTIS, False)} percentage points in a year; worsening when it rises by more than "
                             f"{sk(SLENKSTIS, False)} percentage points; otherwise stable. The threshold is higher "
                             "because the test tasks differ every year and results fluctuate."),
        vertinimo_paaiskinimas=t(f"{metai} m. matematikos PUPP patenkinamo lygio nepasiekė {sk(pask, False)} % "
                                 f"dešimtokų ({ankst} m. – {sk(pries, False)} %, t. y. dalis {kryptis} "
                                 f"{sk(abs(pokytis), False)} proc. punkto). Ankstesnių trijų patikrinimų vidurkis – "
                                 f"{sk(vid3, False)} %.",
                                 f"In {metai}, {sk(pask, False)}% of tenth-graders did not reach the satisfactory level "
                                 f"in the mathematics PUPP ({ankst}: {sk(pries, False)}%, i.e. the share {kryptis} "
                                 f"{sk(abs(pokytis), False)} percentage points). The average of the three previous "
                                 f"assessments is {sk(vid3, False)}%."),
        sparkline=s,
        grafikai=[f1, f2, f3],
        apibrezimas=t("Pagrindinio ugdymo pasiekimų patikrinimas (PUPP) – visų 10 klasės mokinių matematikos ir "
                      "lietuvių kalbos patikrinimas. Rodiklis – mokinių, gavusių 1–3 balus (nepasiekusių patenkinamo "
                      "lygio), dalis. Sudėti visi matematikos patikrinimo variantai (lietuvių, lenkų, rusų ir kt. "
                      "mokomąja kalba). Tarptautiniam palyginimui – EBPO PISA tyrimo žemų pasiekimų 15-mečių dalis.",
                      "The basic education achievement assessment (PUPP) is a test in mathematics and Lithuanian taken "
                      "by all grade 10 pupils. The indicator is the share of pupils scoring 1–3 points (below the "
                      "satisfactory level). All versions of the mathematics test (taught in Lithuanian, Polish, Russian, "
                      "etc.) are combined. For international comparison – the share of low-achieving 15-year-olds in the OECD PISA survey."),
        pastabos=[
            t("PUPP užduotys ir vertinimas kasmet skiriasi, todėl metų rezultatai nėra visiškai palyginami; "
              "patikimiau vertinti kelerių metų tendenciją.",
              "PUPP tasks and marking differ every year, so annual results are not fully comparable; the trend over "
              "several years is more reliable."),
            t("2013–2017 m. lietuvių kalbos patikrinimas buvo atskiras gimtosios ir valstybinės kalbos; nuo 2018 m. – "
              "bendras lietuvių kalbos ir literatūros. 2020 m. patikrinimas nevyko (COVID-19).",
              "In 2013–2017 the Lithuanian test was split into native and state language; since 2018 it has been a "
              "single Lithuanian language and literature test. No assessment took place in 2020 (COVID-19)."),
            t("Duomenys ištraukti iš NŠA PDF lentelių (šalies eilutė); kiekviena eilutė patikrinta – balų skaičių suma "
              "atitinka kandidatų skaičių. Atnaujinama kartą per metus paleidus pupp_rezultatai.py.",
              "Data were extracted from NŠA PDF tables (national row); each row was checked – the sum of score counts "
              "matches the number of candidates. Updated once a year by running pupp_rezultatai.py."),
        ],
        saltiniai=[(t("NŠA – PUPP rezultatai", "NŠA – PUPP results (in Lithuanian)"), "https://www.nsa.smsm.lt/pasiekimu-departamentas/egzaminai-ir-pasiekimu-patikrinimai/pagrindinio-ugdymo-pasiekimu-patikrinimai/pupp-rezultatai/"),
                   ("Eurostat – sdg_04_40 (PISA)", "https://ec.europa.eu/eurostat/databrowser/view/sdg_04_40/default/table?lang=en")],
        papildomai=[(f"{sk(mat['vidurkis'].iloc[-1], False, 2)}", t(f"matematikos PUPP vidurkis, {metai} m.",
                                                                    f"mathematics PUPP mean score, {metai}")),
                    (f"{sk(pm_lt.iloc[-1], False)} %", t(f"žemų matematikos pasiekimų 15-mečių (PISA {pm_lt.index[-1].year}), "
                                                         f"ES – {sk(pm_es.iloc[-1], False)} %",
                                                         f"of 15-year-olds low-achieving in mathematics (PISA {pm_lt.index[-1].year}), "
                                                         f"EU: {sk(pm_es.iloc[-1], False)}%"))],
        lentele=lentele,
    )
