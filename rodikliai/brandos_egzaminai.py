"""2.5 Švietimo rezultatai: valstybiniai brandos egzaminai (VBE)."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import dalis, DUOMENYS, SERIJOS, TEKSTAS_ANTR, Rodiklis, ivertink, linijos, sk, stilius, t, legenda

SLENKSTIS = 2.0      # proc. punkto: egzamino užduotys kasmet skiriasi
SALIS = "vbe_salies_eilutes.csv"                       # irankiai/vbe_rezultatai.py (2013–2024 m., PDF)
MOKYKLOS = "vbe_mokyklu_vidurkiai.csv"                   # NŠA Excel „VBE vidurkiai pagal mokyklas“
MAT, LKL = "Matematika", "Lietuvių kalba ir literatūra"


def _serija(dalykas: str, stulpelis: str) -> pd.Series:
    d = pd.read_csv(DUOMENYS / SALIS)
    d = d[d["dalykas"] == dalykas].sort_values("metai")
    return pd.Series(d[stulpelis].values, index=pd.to_datetime([f"{m}-01-01" for m in d["metai"]]))


def rodiklis() -> Rodiklis:
    s = _serija(MAT, "islaike_proc")
    pask, pries = s.iloc[-1], s.iloc[-2]
    metai, ankst = s.index[-1].year, s.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    # 1 – išlaikiusiųjų dalis
    f1 = go.Figure()
    linijos(f1, [("Matematika", s, SERIJOS[0]), ("Lietuvių kalba ir literatūra", _serija(LKL, "islaike_proc"), SERIJOS[1])],
            zenklas=False, zymekliai=True)
    VBE_SALT = t("Šaltinis: NŠA, VBE rezultatai savivaldybėse (susumuota)",
                 "Source: National Agency for Education (NŠA), state matura exam results by municipality (summed)")
    stilius(f1, t("Išlaikė valstybinį brandos egzaminą", "Passed the state matura examination"),
            t("Laikiusių mokyklų mokinių dalis, %, surinkusi bent 16 balų", "Share of school pupils taking the exam, %, scoring at least 16 points"),
            VBE_SALT, nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    # 2 – aukšti įvertinimai (86–100 balų)
    f2 = go.Figure()
    linijos(f2, [("Matematika", _serija(MAT, "b86_100_proc"), SERIJOS[0]),
                 ("Lietuvių kalba ir literatūra", _serija(LKL, "b86_100_proc"), SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f2, t("Aukšti įvertinimai (86–100 balų)", "High scores (86–100 points)"),
            t("Laikiusių mokinių dalis, %", "Share of pupils taking the exam, %"), VBE_SALT, nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    # 3 – 2025–2026 m. (nauja VBE struktūra): mokyklų vidurkių mediana
    m = pd.read_csv(DUOMENYS / MOKYKLOS)
    rodomi = ["Matematika (A)", "Matematika (B)", "Lietuvių kalba ir literatūra (A)",
              "Lietuvių kalba ir literatūra (B)", "Užsienio (anglų) kalba"]
    med = m[m["dalykas"].isin(rodomi)].groupby(["metai", "dalykas"])["vidurkis"].median().unstack(0).reindex(rodomi)
    f3 = go.Figure()
    DALYKAI_EN = {"Matematika (A)": "Mathematics (A)", "Matematika (B)": "Mathematics (B)",
                  "Lietuvių kalba ir literatūra (A)": "Lithuanian (A)", "Lietuvių kalba ir literatūra (B)": "Lithuanian (B)",
                  "Užsienio (anglų) kalba": "Foreign language (English)"}
    x_ = [t(d_, DALYKAI_EN.get(d_, d_)) for d_ in med.index]
    for i, metai_n in enumerate(med.columns):
        f3.add_trace(go.Bar(x=x_, y=med[metai_n], name=t(f"{metai_n} m.", str(metai_n)), marker_color=SERIJOS[i],
                            marker_line=dict(color="white", width=2),
                            text=[sk(v, False) for v in med[metai_n]], textposition="outside",
                            textfont=dict(color=TEKSTAS_ANTR, size=12),
                            hovertemplate=t(f"%{{x}}<br>{metai_n} m.: %{{y:.1f}} balo<extra></extra>",
                                            f"%{{x}}<br>{metai_n}: %{{y:.1f}} points<extra></extra>")))
    stilius(f3, t("Naujos struktūros VBE (nuo 2025 m.): mokyklų vidurkių mediana",
                  "New-format matura exams (since 2025): median of school averages"),
            t("Balai. A ir B – skirtingi egzamino lygiai; nelyginama su 2013–2024 m.",
              "Points. A and B are different exam levels; not comparable with 2013–2024"),
            t("Šaltinis: NŠA, VBE vidurkiai pagal mokyklas", "Source: NŠA, matura exam averages by school"),
            vnt="", nulio_linija=False)
    f3.update_layout(barmode="group", bargap=0.3, hovermode="closest")
    f3.update_xaxes(tickformat="", tickangle=0)
    f3.update_yaxes(range=[0, 100])

    d = pd.read_csv(DUOMENYS / SALIS)
    lentele = d[d["dalykas"].isin([MAT, LKL])][["metai", "dalykas", "laike", "islaike", "islaike_proc",
                                                 "b16_35", "b36_85", "b86_100", "b86_100_proc"]]

    mat_med = med.loc[["Matematika (A)", "Matematika (B)"]]
    kryptis = t("padidėjo", "rose by") if pokytis > 0 else t("sumažėjo", "fell by")

    _dalys = [dalis(t("Lietuvių k. ir literatūra: išlaikė", "Lithuanian language and literature: passed"),
                    _serija(LKL, "islaike_proc"), "didesne", SLENKSTIS),
              dalis(t("Matematika: 86–100 balų", "Mathematics: 86–100 points"), _serija(MAT, "b86_100_proc"), "didesne", 1.0),
              dalis(t("Lietuvių k.: 86–100 balų", "Lithuanian: 86–100 points"), _serija(LKL, "b86_100_proc"), "didesne", 1.0)]
    return Rodiklis(
        dalys=_dalys,
        id="brandos-egzaminai",
        pavadinimas=t("Matematikos VBE išlaikymas", "Mathematics matura pass rate"),
        trumpas_aprasas=t("laikiusių mokinių išlaikė", "of pupils taking the exam passed"),
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=False,
        vertinimo_taisykle=t(f"Gerėja, kai išlaikiusiųjų dalis per metus padidėja daugiau nei {sk(SLENKSTIS, False)} "
                             f"proc. punkto; prastėja, kai sumažėja daugiau nei {sk(SLENKSTIS, False)} proc. punkto; "
                             "kitu atveju – stabilu.",
                             f"Improving when the pass rate rises by more than {sk(SLENKSTIS, False)} percentage points "
                             f"in a year; worsening when it falls by more than {sk(SLENKSTIS, False)} percentage points; "
                             "otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. matematikos VBE išlaikė {sk(pask, False)} % laikiusių mokyklų mokinių "
                                 f"({ankst} m. – {sk(pries, False)} %; dalis {kryptis} {sk(abs(pokytis), False)} proc. punkto). "
                                 "Tai paskutiniai senosios struktūros egzaminų duomenys; nuo 2025 m. VBE vyksta A ir B lygiais, "
                                 "o NŠA skelbia tik mokyklų vidurkius.",
                                 f"In {metai}, {sk(pask, False)}% of school pupils taking the mathematics matura exam "
                                 f"passed ({ankst}: {sk(pries, False)}%; the share {kryptis} {sk(abs(pokytis), False)} "
                                 "percentage points). These are the last data for the old exam format; since 2025 the "
                                 "exams are held at A and B levels and NŠA publishes only school averages."),
        sparkline=s,
        grafikai=[f1, f2, f3],
        apibrezimas=t("Valstybinio brandos egzamino išlaikiusių (surinkusių 16–100 balų) mokyklų mokinių dalis. "
                      "Šalies rodiklis apskaičiuotas susumavus NŠA skelbiamus savivaldybių rezultatus "
                      "(be eksternų ir buvusių mokinių).",
                      "Share of school pupils who passed the state matura examination (scored 16–100 points). The "
                      "national figure is calculated by summing the municipal results published by NŠA (excluding "
                      "external candidates and former pupils)."),
        pastabos=[
            t("Egzamino užduotys kasmet skiriasi, todėl metų rezultatai nėra visiškai palyginami; 2020 ir 2022 m. "
              "matematikos rezultatai buvo išskirtinai žemi.",
              "Exam tasks differ every year, so annual results are not fully comparable; mathematics results were "
              "exceptionally low in 2020 and 2022."),
            t("Nuo 2025 m. VBE struktūra pasikeitė (A ir B lygiai, nauji dalykai). NŠA šiems metams skelbia tik mokyklų "
              "vidurkius be laikiusiųjų skaičių, todėl išlaikiusiųjų dalies apskaičiuoti negalima; grafike rodoma "
              "nesverta mokyklų vidurkių mediana.",
              "Since 2025 the matura exam format has changed (A and B levels, new subjects). For these years NŠA "
              "publishes only school averages without candidate numbers, so the pass rate cannot be calculated; the "
              "chart shows the unweighted median of school averages."),
            t(f"2026 m. mokyklų vidurkių medianos daugelyje dalykų gerokai žemesnės nei 2025 m. (pvz. matematikos A: "
              f"2026 m. – {sk(mat_med.loc['Matematika (A)'].iloc[-1], False)}, 2025 m. – "
              f"{sk(mat_med.loc['Matematika (A)'].iloc[0], False)} balo) – "
              "prieš darant išvadas verta pasitikslinti NŠA, ar nesikeitė skaičiavimo metodika.",
              f"In 2026 the medians of school averages in many subjects were much lower than in 2025 (e.g. "
              f"mathematics A: {sk(mat_med.loc['Matematika (A)'].iloc[-1], False)} in 2026 vs "
              f"{sk(mat_med.loc['Matematika (A)'].iloc[0], False)} points in 2025) – before drawing conclusions it is "
              "worth checking with NŠA whether the calculation method changed."),
            t("2022 ir 2024 m. viename savivaldybių PDF neatpažinta vienos savivaldybės eilutė (59 iš 60) – šalies suma "
              "dėl to šiek tiek mažesnė.",
              "In 2022 and 2024 one municipality's row was not recognised in a PDF (59 of 60), so the national total "
              "is slightly lower."),
        ],
        saltiniai=[(t("NŠA – VBE rezultatai", "NŠA – matura exam results (in Lithuanian)"), "https://www.nsa.smsm.lt/pasiekimu-departamentas/egzaminai-ir-pasiekimu-patikrinimai/valstybiniai-brandos-egzaminai/vbe-rezultatai/")],
        papildomai=[(f"{sk(_serija(LKL, 'islaike_proc').iloc[-1], False)} %",
                     t(f"išlaikė lietuvių kalbos ir literatūros VBE, {metai} m.",
                       f"passed the Lithuanian language and literature matura, {metai}")),
                    (f"{sk(_serija(MAT, 'b86_100_proc').iloc[-1], False)} %",
                     t(f"matematikos VBE gavo 86–100 balų, {metai} m.", f"scored 86–100 points in the mathematics matura, {metai}"))],
        lentele=lentele,
    )
