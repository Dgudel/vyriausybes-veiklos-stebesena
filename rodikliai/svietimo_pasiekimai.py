"""2.3 Švietimo rezultatai: mokinių pasiekimai (PUPP – 10 kl., PISA – 15 m.)."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import dalis, DUOMENYS, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius
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
    stilius(f1, "Nepasiekė patenkinamo lygio (PUPP, 10 klasė)",
            "Mokinių, gavusių 1–3 balus, dalis, %. 2020 m. patikrinimas nevyko",
            "Šaltinis: NŠA, PUPP rezultatai pagal savivaldybes (šalies eilutė)", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    # 2 – PUPP vidurkiai
    f2 = go.Figure()
    linijos(f2, [("Matematika", mat["vidurkis"], SERIJOS[0]), ("Lietuvių kalba", lt["vidurkis"], SERIJOS[1])],
            vnt="", zenklas=False, dec=2, zymekliai=True, asis=(0, 10))
    stilius(f2, "PUPP įvertinimų vidurkis", "Balai (1–10 skalė)",
            "Šaltinis: NŠA, PUPP rezultatai", vnt="", nulio_linija=False, metiniai=True)
    f2.update_yaxes(range=[0, 10])

    # 3 – PISA: žemų pasiekimų 15-mečiai, Lietuva ir ES
    pisa = {k: (serija("sdg_04_40", "LT", field=k, sex="T", unit="PC"),
                serija("sdg_04_40", "EU27_2020", field=k, sex="T", unit="PC"))
            for k in ["EF461", "READ", "SCI"]}
    f3 = go.Figure()
    linijos(f3, [("Lietuva – matematika", pisa["EF461"][0], SERIJOS[0]),
                 ("ES-27 – matematika", pisa["EF461"][1], SERIJOS[1]),
                 ("Lietuva – skaitymas", pisa["READ"][0], SERIJOS[2]),
                 ("Lietuva – gamtos mokslai", pisa["SCI"][0], SERIJOS[3])],
            zenklas=False, zymekliai=True)
    stilius(f3, "Žemų pasiekimų 15-mečiai (PISA)",
            "Mokinių, nepasiekusių 2-ojo (bazinio) lygio, dalis, %. Tyrimas vyksta kas 3–4 metus",
            "Šaltinis: Eurostat, sdg_04_40 (EBPO PISA)", nulio_linija=False, metiniai=True)
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
    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"

    _dalys = [dalis("Lietuvių k.: nepasiekė patenkinamo lygio", lt["nepasieke_proc"], "mazesne", SLENKSTIS),
              dalis("Matematikos PUPP vidurkis", mat["vidurkis"], "didesne", 0.2, vienetai="", slenkscio_vnt=" balo", dec=2),
              dalis("Lietuvių k. PUPP vidurkis", lt["vidurkis"], "didesne", 0.2, vienetai="", slenkscio_vnt=" balo", dec=2),
              dalis("PISA: žemi pasiekimai – matematika", pisa["EF461"][0], "mazesne", SLENKSTIS),
              dalis("PISA: žemi pasiekimai – skaitymas", pisa["READ"][0], "mazesne", SLENKSTIS),
              dalis("PISA: žemi pasiekimai – gamtos mokslai", pisa["SCI"][0], "mazesne", SLENKSTIS)]
    return Rodiklis(
        dalys=_dalys,
        id="svietimo-pasiekimai",
        pavadinimas="Matematikos pasiekimai (PUPP)",
        trumpas_aprasas="10 kl. mokinių nepasiekė patenkinamo lygio",
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai nepasiekusių patenkinamo lygio dalis per metus sumažėja daugiau nei "
                            f"{sk(SLENKSTIS, False)} proc. punkto; prastėja, kai padidėja daugiau nei "
                            f"{sk(SLENKSTIS, False)} proc. punkto; kitu atveju – stabilu. Slenkstis didesnis, nes "
                            "patikrinimo užduotys kasmet skiriasi ir rezultatai svyruoja."),
        vertinimo_paaiskinimas=(f"{metai} m. matematikos PUPP patenkinamo lygio nepasiekė {sk(pask, False)} % "
                                f"dešimtokų ({ankst} m. – {sk(pries, False)} %, t. y. dalis {kryptis} "
                                f"{sk(abs(pokytis), False)} proc. punkto). Ankstesnių trijų patikrinimų vidurkis – "
                                f"{sk(vid3, False)} %."),
        sparkline=s,
        grafikai=[f1, f2, f3],
        apibrezimas=("Pagrindinio ugdymo pasiekimų patikrinimas (PUPP) – visų 10 klasės mokinių matematikos ir "
                     "lietuvių kalbos patikrinimas. Rodiklis – mokinių, gavusių 1–3 balus (nepasiekusių patenkinamo "
                     "lygio), dalis. Sudėti visi matematikos patikrinimo variantai (lietuvių, lenkų, rusų ir kt. "
                     "mokomąja kalba). Tarptautiniam palyginimui – EBPO PISA tyrimo žemų pasiekimų 15-mečių dalis."),
        pastabos=[
            "PUPP užduotys ir vertinimas kasmet skiriasi, todėl metų rezultatai nėra visiškai palyginami; "
            "patikimiau vertinti kelerių metų tendenciją.",
            "2013–2017 m. lietuvių kalbos patikrinimas buvo atskiras gimtosios ir valstybinės kalbos; nuo 2018 m. – "
            "bendras lietuvių kalbos ir literatūros. 2020 m. patikrinimas nevyko (COVID-19).",
            "Duomenys ištraukti iš NŠA PDF lentelių (šalies eilutė); kiekviena eilutė patikrinta – balų skaičių suma "
            "atitinka kandidatų skaičių. Atnaujinama kartą per metus paleidus pupp_rezultatai.py.",
        ],
        saltiniai=[("NŠA – PUPP rezultatai", "https://www.nsa.smsm.lt/pasiekimu-departamentas/egzaminai-ir-pasiekimu-patikrinimai/pagrindinio-ugdymo-pasiekimu-patikrinimai/pupp-rezultatai/"),
                   ("Eurostat – sdg_04_40 (PISA)", "https://ec.europa.eu/eurostat/databrowser/view/sdg_04_40/default/table?lang=en")],
        papildomai=[(f"{sk(mat['vidurkis'].iloc[-1], False, 2)}", f"matematikos PUPP vidurkis, {metai} m."),
                    (f"{sk(pm_lt.iloc[-1], False)} %", f"žemų matematikos pasiekimų 15-mečių (PISA {pm_lt.index[-1].year}), "
                                                      f"ES – {sk(pm_es.iloc[-1], False)} %")],
        lentele=lentele,
    )
