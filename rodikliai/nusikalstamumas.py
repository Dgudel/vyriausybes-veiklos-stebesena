"""5. Saugumas: užregistruotos nusikalstamos veikos, neįskaitant sukčiavimo (IRD)."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import MENESIAI, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius
from . import ird
from .eurostat_duomenys import serija

SPALVOS = ["#6b6b6b", SERIJOS[1], SERIJOS[2], SERIJOS[3], SERIJOS[0]]   # sukčiavimas – pagrindine spalva

KATEGORIJOS = [("ICCS0101", "Tyčiniai nužudymai"), ("ICCS0401", "Plėšimai"),
               ("ICCS0501", "Įsilaužimai"), ("ICCS0502", "Vagystės"), ("ICCS0701", "Sukčiavimas")]

VISOS_ITEM, SUKC_ITEM = 439622, 438141
SLENKSTIS = 2.0     # % per metus
TRUMPI = ["saus.", "vas.", "kov.", "bal.", "geg.", "birž.", "liep.", "rugp.", "rugs.", "spal.", "lapkr.", "gruod."]


def _tukst(v: float) -> str:
    return f"{v:,.0f}".replace(",", " ")


def rodiklis() -> Rodiklis:
    visos = ird.lentele(VISOS_ITEM, "ird_visos_veikos.csv")
    sukc = ird.lentele(SUKC_ITEM, "ird_sukciavimas.csv")
    d = visos.merge(sukc, on=["metai", "men"], suffixes=("_visos", "_sukc"))
    d["be_sukc"] = d["reiksme_visos"] - d["reiksme_sukc"]

    # Naujausias kaupiamasis laikotarpis ir tas pats laikotarpis prieš metus
    pask = d.sort_values(["metai", "men"]).iloc[-1]
    metai, men = int(pask.metai), int(pask.men)
    pernai = d[(d.metai == metai - 1) & (d.men == men)]
    if pernai.empty:
        raise ValueError(f"IRD: nėra {metai - 1} m. {men} mėn. duomenų palyginimui")
    pernai = pernai.iloc[0]
    pokytis = (pask.be_sukc / pernai.be_sukc - 1) * 100
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)
    laikas = "sausis" if men == 1 else f"sausis–{MENESIAI[men - 1]}"
    laikotarpis = f"{metai} m. {laikas}"

    metiniai = d[d.men == 12].set_index("metai").sort_index()
    x = pd.to_datetime(metiniai.index.astype(str) + "-01-01")

    f1 = go.Figure()
    for i, (stulp, vardas) in enumerate([("be_sukc", "Be sukčiavimo"), ("reiksme_sukc", "Sukčiavimas (BK 182 str.)")]):
        f1.add_trace(go.Bar(x=x, y=metiniai[stulp] / 1000, name=vardas, marker_color=SERIJOS[i],
                            marker_line=dict(color="white", width=1),
                            hovertemplate=f"{vardas}: %{{y:.1f}} tūkst.<extra></extra>"))
    f1.update_layout(barmode="stack")
    stilius(f1, "Užregistruotos nusikalstamos veikos", "Tūkst. per metus",
            "Šaltinis: IRD prie VRM, Nusikalstamų veikų žinybinis registras", vnt="", nulio_linija=False, metiniai=True)

    # Kaupiamai nuo metų pradžios: šie ir praėję metai
    f2 = go.Figure()
    for i, m in enumerate([metai - 1, metai]):
        s = d[d.metai == m].set_index("men")["be_sukc"].sort_index()
        f2.add_trace(go.Scatter(x=list(s.index), y=s.values / 1000,
                                name=f"{m} m.", mode="lines+markers",
                                line=dict(color=SERIJOS[1 - i] if i == 0 else SERIJOS[0], width=3 if i else 2,
                                          dash=None if i else "dot"),
                                hovertemplate=f"{m} m.: %{{y:.1f}} tūkst.<extra></extra>"))
    stilius(f2, "Šie metai palyginti su praėjusiais", "Nusikalstamos veikos be sukčiavimo, kaupiamai nuo sausio, tūkst.",
            "Šaltinis: IRD prie VRM", vnt="", nulio_linija=False)
    f2.update_yaxes(rangemode="tozero")
    f2.update_xaxes(tickmode="array", tickvals=list(range(1, 13)), ticktext=TRUMPI, range=[0.5, 12.5])

    # Eurostat: kategorijos 100 tūkst. gyv., indeksas (2016 = 100)
    f3 = go.Figure()
    kat = []
    for kodas, vardas in KATEGORIJOS:
        try:
            s = serija("crim_off_cat", "LT", iccs=kodas, unit="P_HTHAB")
        except Exception:
            continue
        s = s[s.index >= "2016-01-01"]
        if s.empty:
            continue
        kat.append((vardas, s / s.iloc[0] * 100, SPALVOS[len(kat) % len(SPALVOS)]))
    if kat:
        linijos(f3, kat, vnt="", zenklas=False, dec=0)
        f3.add_hline(y=100, line=dict(color="#9a9994", width=1))
        stilius(f3, "Kaip keičiasi skirtingos nusikalstamos veikos",
                "Užregistruota 100 tūkst. gyventojų, indeksas (2016 m. = 100)",
                "Šaltinis: Eurostat, crim_off_cat", vnt="", nulio_linija=False, metiniai=True)

    lentele = d.rename(columns={"reiksme_visos": "visos_veikos", "reiksme_sukc": "sukciavimas",
                                "be_sukc": "be_sukciavimo", "men": "iki_menesio"})
    lentele = lentele.sort_values(["metai", "iki_menesio"])

    kryptis = "sumažėjo" if pokytis < 0 else "padidėjo"
    return Rodiklis(
        id="nusikalstamumas",
        pavadinimas="Nusikalstamumas (be sukčiavimo)",
        trumpas_aprasas="registruotų veikų pokytis per metus",
        reiksme=pokytis, vienetai="%", laikotarpis=laikotarpis, busena=busena,
        zenklas=True, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Lyginama su tuo pačiu praėjusių metų laikotarpiu. Gerėja, kai veikų sumažėja daugiau "
                            f"nei {sk(SLENKSTIS, False, 0)} %; prastėja, kai padaugėja daugiau nei "
                            f"{sk(SLENKSTIS, False, 0)} %; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. ({laikas}) užregistruotų nusikalstamų veikų, neskaičiuojant sukčiavimo, "
                                f"skaičius – {_tukst(pask.be_sukc)} ({metai - 1} m. tuo pačiu laikotarpiu – "
                                f"{_tukst(pernai.be_sukc)}). Šis skaičius {kryptis} {sk(abs(pokytis), False)} %. "
                                f"Sukčiavimo atvejų – {_tukst(pask.reiksme_sukc)}."),
        sparkline=pd.Series(metiniai["be_sukc"].values, index=x)[x >= "2010-01-01"],
        grafikai=[f1, f2] + ([f3] if kat else []),
        apibrezimas=("Visos Nusikalstamų veikų žinybiniame registre užregistruotos nusikalstamos veikos "
                     "(nusikaltimai ir baudžiamieji nusižengimai), atėmus sukčiavimą (BK 182 str.). Sukčiavimas "
                     "atskiriamas, nes jo, ypač nuotolinio, skaičius sparčiai kinta dėl kitų priežasčių nei "
                     "bendras saugumas gatvėse ir namuose."),
        pastabos=["Rodikliai kaupiami nuo metų pradžios, todėl lyginama su tuo pačiu praėjusių metų laikotarpiu.",
                  "Registruotų veikų skaičius priklauso ir nuo to, kiek žmonės praneša policijai."],
        saltiniai=[("IRD – visos užregistruotos nusikalstamos veikos",
                    f"https://www.ird.lt/lt/indicators/opendata/item.{VISOS_ITEM}"),
                   ("IRD – sukčiavimas (BK 182 str.)", f"https://www.ird.lt/lt/indicators/opendata/item.{SUKC_ITEM}"),
                   ("Eurostat – crim_off_cat", "https://ec.europa.eu/eurostat/databrowser/view/crim_off_cat/default/table?lang=en")],
        papildomai=[(_tukst(pask.be_sukc), f"veikų be sukčiavimo, {laikotarpis}"),
                    (_tukst(metiniai["be_sukc"].iloc[-1]), f"per {metiniai.index[-1]} m.")],
        lentele=lentele,
    )
