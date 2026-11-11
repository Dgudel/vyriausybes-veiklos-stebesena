"""5. Saugumas: užregistruotos nusikalstamos veikos, neįskaitant sukčiavimo (IRD)."""
import pandas as pd
import plotly.graph_objects as go

from .bendra import (dalis, palyginimo_tekstas, MENESIAI, SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, t, en,
                     nuo_metu_pradzios, menuo)
from . import ird
from .eurostat_duomenys import serija

SPALVOS = ["#6b6b6b", SERIJOS[1], SERIJOS[2], SERIJOS[3], SERIJOS[0]]   # sukčiavimas – pagrindine spalva

KATEGORIJOS = [("ICCS0101", "Tyčiniai nužudymai"), ("ICCS0401", "Plėšimai"),
               ("ICCS0501", "Įsilaužimai"), ("ICCS0502", "Vagystės"), ("ICCS0701", "Sukčiavimas")]
KATEGORIJOS_EN = {"Tyčiniai nužudymai": "Intentional homicide", "Plėšimai": "Robbery", "Įsilaužimai": "Burglary",
                  "Vagystės": "Theft", "Sukčiavimas": "Fraud"}


def _kat(v: str) -> str:
    return KATEGORIJOS_EN.get(v, v) if en() else v

VISOS_ITEM, SUKC_ITEM = 439622, 438141
# Sunkūs ir labai sunkūs nusikaltimai: A – ištirta, B – užregistruota, C – užregistruota, tyrimas nebaigtas
SUNKUS_A, SUNKUS_B, SUNKUS_C = 447130, 447126, 447125
ISTIRTA_SLENKSTIS = 1.0   # p. p.


def _istirtu_dalis():
    """X = A / (B + C) × 100 %, kiekvienais metais tam pačiam kaupiamajam laikotarpiui (sausis–naujausias mėnuo).
    Grąžina (metinė serija, naujausias mėnuo, lentelė)."""
    a = ird.lentele(SUNKUS_A, "ird_sunkus_istirta.csv")
    b = ird.lentele(SUNKUS_B, "ird_sunkus_uzregistruota.csv")
    c = ird.lentele(SUNKUS_C, "ird_sunkus_nebaigta.csv")
    d = (a.rename(columns={"reiksme": "A"}).merge(b.rename(columns={"reiksme": "B"}), on=["metai", "men"])
          .merge(c.rename(columns={"reiksme": "C"}), on=["metai", "men"]).sort_values(["metai", "men"]))
    d["X"] = d.A / (d.B + d.C) * 100
    men = int(d.iloc[-1].men)
    m = d[d.men == men].set_index("metai")
    s = pd.Series(m.X.values, index=pd.to_datetime(m.index.astype(str) + "-01-01"))
    return s, men, d
SLENKSTIS = 2.0     # % per metus
TRUMPI = ["saus.", "vas.", "kov.", "bal.", "geg.", "birž.", "liep.", "rugp.", "rugs.", "spal.", "lapkr.", "gruod."]


def _tukst(v: float) -> str:
    return f"{v:,.0f}" if en() else f"{v:,.0f}".replace(",", " ")


def _metinis_pokytis(d: pd.DataFrame, stulp: str) -> pd.Series:
    """Kaupiamoji reikšmė, palyginta su tuo pačiu praėjusių metų mėnesiu, % (indeksas – mėnesio data)."""
    d = d.dropna(subset=[stulp])
    menesiniai = d.groupby("metai")["men"].nunique()
    d = d[d.metai.isin(menesiniai[menesiniai > 1].index)]      # tik metai su mėnesiniais duomenimis
    s = d.set_index(["metai", "men"])[stulp]
    pries = s.copy()
    pries.index = pd.MultiIndex.from_tuples([(m + 1, mm) for m, mm in pries.index], names=s.index.names)
    p = ((s / pries - 1) * 100).dropna()
    p.index = pd.to_datetime([f"{m}-{mm:02d}-01" for m, mm in p.index])
    return p.sort_index()


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
    laikas = t("sausis" if men == 1 else f"sausis–{MENESIAI[men - 1]}",
               "January" if men == 1 else f"January–{menuo(men)}")
    laikotarpis = nuo_metu_pradzios(metai, men)

    metiniai = d[d.men == 12].set_index("metai").sort_index()
    x = pd.to_datetime(metiniai.index.astype(str) + "-01-01")

    f1 = go.Figure()
    for i, (stulp, vardas) in enumerate([("be_sukc", t("Be sukčiavimo", "Excluding fraud")),
                                         ("reiksme_sukc", t("Sukčiavimas (BK 182 str.)", "Fraud (Criminal Code Art. 182)"))]):
        f1.add_trace(go.Bar(x=x, y=metiniai[stulp] / 1000, name=vardas, marker_color=SERIJOS[i],
                            marker_line=dict(color="white", width=1),
                            hovertemplate=f"{vardas}: %{{y:.1f}}{t(' tūkst.', 'k')}<extra></extra>"))
    f1.update_layout(barmode="stack")
    stilius(f1, t("Užregistruotos nusikalstamos veikos", "Recorded criminal offences"), t("Tūkst. per metus", "Thousands per year"),
            "Šaltinis: IRD prie VRM, Nusikalstamų veikų žinybinis registras", vnt="", nulio_linija=False, metiniai=True)

    # Pokytis, palyginti su tuo pačiu laikotarpiu prieš metus (kaupiamieji duomenys lyginami su kaupiamaisiais)
    f2 = go.Figure()
    f2.add_hrect(y0=-SLENKSTIS, y1=SLENKSTIS, fillcolor="#9a9994", opacity=0.12, line_width=0,
                 annotation_text=t(f"stabilu (±{sk(SLENKSTIS, False, 0)} %)", f"stable (±{sk(SLENKSTIS, False, 0)}%)"),
                 annotation_position="top left",
                 annotation_font=dict(size=11, color="#6b6b6b"))
    serijos = [(t("Visos veikos", "All offences"), _metinis_pokytis(visos.rename(columns={"reiksme": "v"}), "v"), "#9a9994"),
               (t("Be sukčiavimo", "Excluding fraud"), _metinis_pokytis(d, "be_sukc"), SERIJOS[0]),
               (t("Sukčiavimas", "Fraud"), _metinis_pokytis(d, "reiksme_sukc"), SERIJOS[1])]
    serijos = [(v, s[s.index >= "2019-01-01"], c) for v, s, c in serijos if len(s[s.index >= "2019-01-01"])]
    linijos(f2, serijos, vnt=" %", zenklas=True, dec=1)
    stilius(f2, t("Pokytis, palyginti su tuo pačiu laikotarpiu prieš metus", "Change compared with the same period a year earlier"),
            t("Užregistruota nuo metų pradžios iki nurodyto mėnesio, palyginti su tuo pačiu praėjusių metų laikotarpiu, %",
              "Recorded from the start of the year to the given month, compared with the same period of the previous year, %"),
            "Šaltinis: IRD prie VRM", vnt=" %")
    f2.update_traces(hovertemplate="%{fullData.name}: %{y:+.1f} %<br>%{x|%Y-%m}<extra></extra>",
                     selector=dict(type="scatter", mode="lines"))
    f2.update_xaxes(tickformat="%Y", dtick="M12")

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
        kat.append((_kat(vardas), s / s.iloc[0] * 100, SPALVOS[len(kat) % len(SPALVOS)]))
    if kat:
        linijos(f3, kat, vnt="", zenklas=False, dec=0)
        f3.add_hline(y=100, line=dict(color="#9a9994", width=1))
        stilius(f3, t("Kaip keičiasi skirtingos nusikalstamos veikos", "How different offences are changing"),
                t("Užregistruota 100 tūkst. gyventojų, indeksas (2016 m. = 100)", "Recorded per 100,000 inhabitants, index (2016 = 100)"),
                "Šaltinis: Eurostat, crim_off_cat", vnt="", nulio_linija=False, metiniai=True)

    lentele = d.rename(columns={"reiksme_visos": "visos_veikos", "reiksme_sukc": "sukciavimas",
                                "be_sukc": "be_sukciavimo", "men": "iki_menesio"})
    lentele = lentele.sort_values(["metai", "iki_menesio"])

    kryptis = t("sumažėjo", "fell by") if pokytis < 0 else t("padidėjo", "rose by")

    _dalys = []
    for vardas, s in [(t("Sukčiavimas", "Fraud"), _metinis_pokytis(d, "reiksme_sukc")),
                      (t("Visos veikos", "All offences"), _metinis_pokytis(visos.rename(columns={"reiksme": "v"}), "v"))]:
        dx = dalis(vardas, s, "mazesne", SLENKSTIS, budas="lygis", zenklas=True, slenkscio_vnt=" %")
        dx.laikotarpis, dx.palyginimas = laikotarpis, palyginimo_tekstas(laikotarpis)
        _dalys.append(dx)
    f4 = None
    try:
        ist, ist_men, _ = _istirtu_dalis()
        ist_laik = nuo_metu_pradzios(ist.index[-1].year, ist_men)
        dx = dalis(t("Ištirtų sunkių ir labai sunkių nusikaltimų dalis", "Clearance rate of serious and very serious crimes"),
                   ist, "didesne", ISTIRTA_SLENKSTIS)
        dx.laikotarpis, dx.palyginimas = ist_laik, palyginimo_tekstas(ist_laik)
        _dalys.append(dx)
        f4 = go.Figure()
        linijos(f4, [(t("Ištirta dalis", "Share cleared"), ist[ist.index >= "2010-01-01"], SERIJOS[0])], vnt=" %", zenklas=False, dec=1)
        laik_zod = t("sausis" if ist_men == 1 else f"sausis–{MENESIAI[ist_men - 1]}",
                     "January" if ist_men == 1 else f"January–{menuo(ist_men)}")
        stilius(f4, t("Ištirtų sunkių ir labai sunkių nusikaltimų dalis", "Clearance rate of serious and very serious crimes"),
                t(f"Ištirta / (užregistruota + nebaigti tyrimai) × 100, kiekvienų metų {laik_zod}, %",
                  f"Investigated / (recorded + pending investigations) × 100, {laik_zod} of each year, %"),
                "Šaltinis: IRD prie VRM, Nusikalstamų veikų žinybinis registras", vnt=" %", nulio_linija=False,
                metiniai=True)
        f4.update_yaxes(rangemode="tozero")
    except Exception as e:
        print(f"  ⚠ ištirtų dalis neapskaičiuota: {e}")
    for kodas, vardas in KATEGORIJOS[:4]:
        try:
            s = serija("crim_off_cat", "LT", iccs=kodas, unit="P_HTHAB")
            _dalys.append(dalis(t(f"{vardas} (100 tūkst. gyv.)", f"{_kat(vardas)} (per 100,000 inhabitants)"),
                                s, "mazesne", 5.0, budas="proc", vienetai=""))
        except Exception:
            pass
    return Rodiklis(
        dalys=_dalys,
        id="nusikalstamumas",
        pavadinimas=t("Nusikalstamumas (be sukčiavimo)", "Crime (excluding fraud)"),
        trumpas_aprasas=t("registruotų veikų pokytis per metus", "year-on-year change in recorded offences"),
        reiksme=pokytis, vienetai="%", laikotarpis=laikotarpis, busena=busena,
        zenklas=True, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Lyginama su tuo pačiu praėjusių metų laikotarpiu. Gerėja, kai veikų sumažėja daugiau "
                             f"nei {sk(SLENKSTIS, False, 0)} %; prastėja, kai padaugėja daugiau nei "
                             f"{sk(SLENKSTIS, False, 0)} %; kitu atveju – stabilu.",
                             f"Compared with the same period of the previous year. Improving when offences fall by more "
                             f"than {sk(SLENKSTIS, False, 0)}%; worsening when they rise by more than "
                             f"{sk(SLENKSTIS, False, 0)}%; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. ({laikas}) užregistruotų nusikalstamų veikų, neskaičiuojant sukčiavimo, "
                                 f"skaičius – {_tukst(pask.be_sukc)} ({metai - 1} m. tuo pačiu laikotarpiu – "
                                 f"{_tukst(pernai.be_sukc)}). Šis skaičius {kryptis} {sk(abs(pokytis), False)} %. "
                                 f"Sukčiavimo atvejų – {_tukst(pask.reiksme_sukc)}.",
                                 f"In {laikas} {metai}, {_tukst(pask.be_sukc)} criminal offences excluding fraud were "
                                 f"recorded (same period of {metai - 1}: {_tukst(pernai.be_sukc)}). The number {kryptis} "
                                 f"{sk(abs(pokytis), False)}%. Fraud cases: {_tukst(pask.reiksme_sukc)}."),
        sparkline=pd.Series(metiniai["be_sukc"].values, index=x)[x >= "2010-01-01"],
        grafikai=[f1, f2] + ([f3] if kat else []) + ([f4] if f4 is not None else []),
        apibrezimas=t("Visos Nusikalstamų veikų žinybiniame registre užregistruotos nusikalstamos veikos "
                      "(nusikaltimai ir baudžiamieji nusižengimai), atėmus sukčiavimą (BK 182 str.). Sukčiavimas "
                      "atskiriamas, nes jo, ypač nuotolinio, skaičius sparčiai kinta dėl kitų priežasčių nei "
                      "bendras saugumas gatvėse ir namuose.",
                      "All criminal offences (crimes and criminal misdemeanours) recorded in the Departmental Register "
                      "of Criminal Offences, excluding fraud (Criminal Code Art. 182). Fraud is separated because its "
                      "numbers, especially of online fraud, change rapidly for reasons other than general safety on "
                      "the streets and at home."),
        pastabos=[t("IRD skelbia kaupiamuosius duomenis (nuo metų pradžios), todėl jų skaičius per metus visada auga. "
                    "Kad tai nebūtų klaidinanti, antrasis grafikas rodo pokytį, palyginti su tuo pačiu praėjusių metų "
                    "laikotarpiu: pvz., 2026 m. sausis–spalis lyginamas su 2025 m. sausiu–spaliu.",
                    "IRD publishes cumulative (year-to-date) figures, so the numbers always rise during the year. To "
                    "avoid a misleading picture, the second chart shows the change compared with the same period of "
                    "the previous year: e.g. January–October 2026 is compared with January–October 2025."),
                  t("Registruotų veikų skaičius priklauso ir nuo to, kiek žmonės praneša policijai.",
                    "The number of recorded offences also depends on how often people report to the police."),
                  t("Ištirtų sunkių ir labai sunkių nusikaltimų dalis skaičiuojama pagal formulę X = A / (B + C) × 100 %: "
                    "A – ištirtų sunkių ir labai sunkių nusikaltimų skaičius, B – užregistruotų per ataskaitinį "
                    "laikotarpį, C – užregistruotų, kurių ikiteisminis tyrimas nebaigtas. Kiekvienų metų reikšmė "
                    "skaičiuojama tam pačiam laikotarpiui nuo metų pradžios, todėl metai tarpusavyje palyginami.",
                    "The clearance rate of serious and very serious crimes is calculated as X = A / (B + C) × 100%: "
                    "A – number of serious and very serious crimes investigated, B – recorded in the reporting period, "
                    "C – recorded with the pre-trial investigation not completed. Each year's value is calculated for "
                    "the same period from the start of the year, so years are comparable.")],
        saltiniai=[(t("IRD – visos užregistruotos nusikalstamos veikos", "IRD – all recorded criminal offences"),
                    f"https://www.ird.lt/lt/indicators/opendata/item.{VISOS_ITEM}"),
                   (t("IRD – sukčiavimas (BK 182 str.)", "IRD – fraud (Criminal Code Art. 182)"),
                    f"https://www.ird.lt/lt/indicators/opendata/item.{SUKC_ITEM}"),
                   (t("IRD – sunkūs ir labai sunkūs nusikaltimai: ištirta", "IRD – serious and very serious crimes: investigated"),
                    f"https://www.ird.lt/lt/indicators/opendata/item.{SUNKUS_A}"),
                   (t("IRD – sunkūs ir labai sunkūs nusikaltimai: užregistruota", "IRD – serious and very serious crimes: recorded"),
                    f"https://www.ird.lt/lt/indicators/opendata/item.{SUNKUS_B}"),
                   (t("IRD – sunkūs ir labai sunkūs nusikaltimai: tyrimas nebaigtas", "IRD – serious and very serious crimes: investigation pending"),
                    f"https://www.ird.lt/lt/indicators/opendata/item.{SUNKUS_C}"),
                   ("Eurostat – crim_off_cat", "https://ec.europa.eu/eurostat/databrowser/view/crim_off_cat/default/table?lang=en")],
        papildomai=[(_tukst(pask.be_sukc), t(f"veikų be sukčiavimo, {laikotarpis}", f"offences excluding fraud, {laikotarpis}")),
                    (_tukst(metiniai["be_sukc"].iloc[-1]), t(f"per {metiniai.index[-1]} m.", f"in {metiniai.index[-1]}"))],
        lentele=lentele,
    )
