"""2.5 Švietimo rezultatai: valstybiniai brandos egzaminai (VBE)."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import DUOMENYS, SERIJOS, TEKSTAS_ANTR, Rodiklis, ivertink, linijos, sk, stilius

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
    stilius(f1, "Išlaikė valstybinį brandos egzaminą",
            "Laikiusių mokyklų mokinių dalis, %, surinkusi bent 16 balų",
            "Šaltinis: NŠA, VBE rezultatai savivaldybėse (susumuota)", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    # 2 – aukšti įvertinimai (86–100 balų)
    f2 = go.Figure()
    linijos(f2, [("Matematika", _serija(MAT, "b86_100_proc"), SERIJOS[0]),
                 ("Lietuvių kalba ir literatūra", _serija(LKL, "b86_100_proc"), SERIJOS[1])],
            zenklas=False, zymekliai=True)
    stilius(f2, "Aukšti įvertinimai (86–100 balų)", "Laikiusių mokinių dalis, %",
            "Šaltinis: NŠA, VBE rezultatai savivaldybėse (susumuota)", nulio_linija=False, metiniai=True)
    f2.update_yaxes(rangemode="tozero")

    # 3 – 2025–2026 m. (nauja VBE struktūra): mokyklų vidurkių mediana
    m = pd.read_csv(DUOMENYS / MOKYKLOS)
    rodomi = ["Matematika (A)", "Matematika (B)", "Lietuvių kalba ir literatūra (A)",
              "Lietuvių kalba ir literatūra (B)", "Užsienio (anglų) kalba"]
    med = m[m["dalykas"].isin(rodomi)].groupby(["metai", "dalykas"])["vidurkis"].median().unstack(0).reindex(rodomi)
    f3 = go.Figure()
    for i, metai_n in enumerate(med.columns):
        f3.add_trace(go.Bar(x=med.index, y=med[metai_n], name=f"{metai_n} m.", marker_color=SERIJOS[i],
                            marker_line=dict(color="white", width=2),
                            text=[sk(v, False) for v in med[metai_n]], textposition="outside",
                            textfont=dict(color=TEKSTAS_ANTR, size=12),
                            hovertemplate=f"%{{x}}<br>{metai_n} m.: %{{y:.1f}} balo<extra></extra>"))
    stilius(f3, "Naujos struktūros VBE (nuo 2025 m.): mokyklų vidurkių mediana",
            "Balai. A ir B – skirtingi egzamino lygiai; nelyginama su 2013–2024 m.",
            "Šaltinis: NŠA, VBE vidurkiai pagal mokyklas", vnt="", nulio_linija=False)
    f3.update_layout(barmode="group", bargap=0.3, hovermode="closest")
    f3.update_xaxes(tickformat="", tickangle=0)
    f3.update_yaxes(range=[0, 100])

    d = pd.read_csv(DUOMENYS / SALIS)
    lentele = d[d["dalykas"].isin([MAT, LKL])][["metai", "dalykas", "laike", "islaike", "islaike_proc",
                                                 "b16_35", "b36_85", "b86_100", "b86_100_proc"]]

    mat_med = med.loc[["Matematika (A)", "Matematika (B)"]]
    kryptis = "padidėjo" if pokytis > 0 else "sumažėjo"
    return Rodiklis(
        id="brandos-egzaminai",
        pavadinimas="Matematikos VBE išlaikymas",
        trumpas_aprasas="laikiusių mokinių išlaikė",
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=False,
        vertinimo_taisykle=(f"Gerėja, kai išlaikiusiųjų dalis per metus padidėja daugiau nei {sk(SLENKSTIS, False)} "
                            f"proc. punkto; prastėja, kai sumažėja daugiau nei {sk(SLENKSTIS, False)} proc. punkto; "
                            "kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. matematikos VBE išlaikė {sk(pask, False)} % laikiusių mokyklų mokinių "
                                f"({ankst} m. – {sk(pries, False)} %; dalis {kryptis} {sk(abs(pokytis), False)} proc. punkto). "
                                "Tai paskutiniai senosios struktūros egzaminų duomenys; nuo 2025 m. VBE vyksta A ir B lygiais, "
                                "o NŠA skelbia tik mokyklų vidurkius."),
        sparkline=s,
        grafikai=[f1, f2, f3],
        apibrezimas=("Valstybinio brandos egzamino išlaikiusių (surinkusių 16–100 balų) mokyklų mokinių dalis. "
                     "Šalies rodiklis apskaičiuotas susumavus NŠA skelbiamus savivaldybių rezultatus "
                     "(be eksternų ir buvusių mokinių)."),
        pastabos=[
            "Egzamino užduotys kasmet skiriasi, todėl metų rezultatai nėra visiškai palyginami; 2020 ir 2022 m. "
            "matematikos rezultatai buvo išskirtinai žemi.",
            "Nuo 2025 m. VBE struktūra pasikeitė (A ir B lygiai, nauji dalykai). NŠA šiems metams skelbia tik mokyklų "
            "vidurkius be laikiusiųjų skaičių, todėl išlaikiusiųjų dalies apskaičiuoti negalima; grafike rodoma "
            "nesverta mokyklų vidurkių mediana.",
            f"2026 m. mokyklų vidurkių medianos daugelyje dalykų gerokai žemesnės nei 2025 m. (pvz. matematikos A: "
            f"2026 m. – {sk(mat_med.loc['Matematika (A)'].iloc[-1], False)}, 2025 m. – "
            f"{sk(mat_med.loc['Matematika (A)'].iloc[0], False)} balo) – "
            "prieš darant išvadas verta pasitikslinti NŠA, ar nesikeitė skaičiavimo metodika.",
            "2022 ir 2024 m. viename savivaldybių PDF neatpažinta vienos savivaldybės eilutė (59 iš 60) – šalies suma "
            "dėl to šiek tiek mažesnė.",
        ],
        saltiniai=[("NŠA – VBE rezultatai", "https://www.nsa.smsm.lt/pasiekimu-departamentas/egzaminai-ir-pasiekimu-patikrinimai/valstybiniai-brandos-egzaminai/vbe-rezultatai/")],
        papildomai=[(f"{sk(_serija(LKL, 'islaike_proc').iloc[-1], False)} %",
                     f"išlaikė lietuvių kalbos ir literatūros VBE, {metai} m."),
                    (f"{sk(_serija(MAT, 'b86_100_proc').iloc[-1], False)} %", f"matematikos VBE gavo 86–100 balų, {metai} m.")],
        lentele=lentele,
    )
