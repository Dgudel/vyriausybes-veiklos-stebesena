"""Bendros priemonės visiems rodikliams: duomenų skaitymas, vertinimas, grafikų stilius."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

SAKNIS = Path(__file__).resolve().parent.parent
DUOMENYS = SAKNIS / "duomenys"

# ---------------- Spalvos ----------------
SERIJOS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]      # kategorinė paletė, fiksuota tvarka
TEKSTAS, TEKSTAS_ANTR, TINKLELIS, FONAS = "#0b0b0b", "#52514e", "#e6e5e1", "#ffffff"
SRIFTAS = "system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif"

MENESIAI_KADA = ["sausį", "vasarį", "kovą", "balandį", "gegužę", "birželį", "liepą",
                 "rugpjūtį", "rugsėjį", "spalį", "lapkritį", "gruodį"]
MENESIAI_SU = ["sausiu", "vasariu", "kovu", "balandžiu", "gegužiu", "birželiu", "liepa",
               "rugpjūčiu", "rugsėju", "spaliu", "lapkričiu", "gruodžiu"]
MENESIAI = ["sausis", "vasaris", "kovas", "balandis", "gegužė", "birželis", "liepa",
            "rugpjūtis", "rugsėjis", "spalis", "lapkritis", "gruodis"]


# ---------------- Rodiklio aprašas ----------------
@dataclass
class Dalis:
    """Papildomas (sudedamasis) rodiklio grafiko matas su savo vertinimu."""
    pavadinimas: str
    reiksme: float
    vienetai: str
    laikotarpis: str          # 2026M09 / 2026K2 / 2025
    busena: str
    pokytis: str              # pvz. „−0,4 p. p.“ arba „+3,0 %“
    palyginimas: str          # pvz. „lyginant su 2025 m. rugsėju“
    taisykle: str
    zenklas: bool = False
    dec: int = 1
    serija: "pd.Series | None" = None      # duomenys grafikui ir mažajam grafikui


@dataclass
class Rodiklis:
    id: str
    pavadinimas: str
    trumpas_aprasas: str                 # po skaičiumi kortelėje
    reiksme: float | None = None
    vienetai: str = "%"
    laikotarpis: str = ""                # pvz. "2026M08"
    busena: str = "nera"                 # gereja / stabilu / prasteja / nera
    vertinimo_taisykle: str = ""         # kaip nustatyta būsena – rodoma puslapyje
    vertinimo_paaiskinimas: str = ""     # konkreti šio laikotarpio išvada
    sparkline: pd.Series | None = None   # indeksas – datos
    grafikai: list = field(default_factory=list)
    apibrezimas: str = ""
    pastabos: list[str] = field(default_factory=list)
    saltiniai: list[tuple[str, str]] = field(default_factory=list)   # (pavadinimas, nuoroda)
    papildomai: list[tuple[str, str]] = field(default_factory=list)  # (skaičius, paaiškinimas)
    lentele: pd.DataFrame | None = None  # atsisiunčiami duomenys
    zenklas: bool = True                 # rodyti +/− (pokyčiams); False – lygio reikšmėms
    dec: int = 1                         # skaitmenų po kablelio
    spark_nuo_nulio: bool = True         # ar mažame grafike rodyti nulį (pokyčiams – taip)
    palyginimas: str | None = None       # palyginimo pagrindas; jei None – nustatomas automatiškai pagal laikotarpį
    dalys: list[Dalis] = field(default_factory=list)   # sudedamosios dalys su savo vertinimu


# ---------------- Duomenys ----------------
DATAPORTAL_API = "https://api.dataportal.gov.lt/namespaces/188600177/tables"


def atsisiusk_dataportal(lentele: str, puslapis: int = 1000) -> pd.DataFrame:
    """Atsisiunčia visą lentelę iš Lietuvos duomenų portalo API.

    API puslapiuoja pagal puslapio numerį (atsakyme yra current_page / total_pages), todėl pirmiausia
    sužinome eilučių skaičių ir bandome gauti viską viena užklausa; jei API riboja dydį – einame
    per puslapius. Dublikatai pašalinami pagal row_id ir patikrinama, ar gautos visos eilutės."""
    import requests
    url = f"{DATAPORTAL_API}/{lentele}/query"

    def uzklausa(**kuno):
        r = requests.post(url, json=kuno, timeout=120)
        r.raise_for_status()
        return r.json()

    viso = uzklausa(limit=1, offset=0)["total"]
    d = uzklausa(limit=viso, offset=0)
    eilutes = d["data"]
    if len(eilutes) < viso:                      # API ribojo puslapio dydį – einame per puslapius
        eilutes = []
        dydis = len(d["data"]) or puslapis
        for nr in range(1, -(-viso // dydis) + 1):
            eilutes += uzklausa(limit=dydis, offset=(nr - 1) * dydis, page=nr)["data"]

    df = pd.DataFrame(eilutes)
    if "row_id" in df.columns:
        df = df.drop_duplicates(subset="row_id")
    if len(df) != viso:
        raise RuntimeError(f"{lentele}: gauta {len(df)} skirtingų eilučių iš {viso}")
    return df


def skaityk(failas: str, api_lentele: str | None = None) -> pd.DataFrame:
    """Skaito duomenis iš duomenys/ aplanko. Jei nurodyta duomenų portalo lentelė ir aplinkoje
    ATNAUJINTI=1 (taip daro GitHub Actions), pirmiausia bando atsisiųsti naujausią versiją per API.
    Jei nepavyksta – naudojamas esamas failas, todėl švieslentė niekada nelieka tuščia."""
    kelias = DUOMENYS / failas
    if api_lentele and os.environ.get("ATNAUJINTI") == "1":
        try:
            df = atsisiusk_dataportal(api_lentele)
            df.to_csv(kelias.with_name(f"{api_lentele}.csv"), index=False)
            print(f"  ↓ Duomenų portalas {api_lentele}: {len(df)} eilučių")
            return df
        except Exception as e:
            print(f"  ⚠ {api_lentele} neatsisiųsta ({e}); naudojamas {failas}")
    if kelias.suffix in (".xlsx", ".xls"):
        return pd.read_excel(kelias)
    return pd.read_csv(kelias)


def i_data(laikotarpis: str) -> pd.Timestamp:
    x = str(laikotarpis).strip()
    if m := re.fullmatch(r"(\d{4})M(\d{1,2})", x):
        return pd.Timestamp(int(m[1]), int(m[2]), 1)
    if m := re.fullmatch(r"(\d{4})[KQ](\d)", x):
        return pd.Timestamp(int(m[1]), 3 * int(m[2]) - 2, 1)
    if re.fullmatch(r"\d{4}", x):
        return pd.Timestamp(int(x), 1, 1)
    return pd.to_datetime(x)


def zmoniu_laikotarpis(laikotarpis: str, kada: bool = False) -> str:
    """2026M08 -> „2026 m. rugpjūtis“; kada=True -> „2026 m. rugpjūtį“ (sakinio viduje)."""
    x = str(laikotarpis)
    if m := re.fullmatch(r"(\d{4})M(\d{1,2})", x):
        return f"{m[1]} m. {(MENESIAI_KADA if kada else MENESIAI)[int(m[2]) - 1]}"
    if m := re.fullmatch(r"(\d{4})[KQ](\d)", x):
        return f"{m[1]} m. {m[2]} ketv."
    return f"{x} m." if re.fullmatch(r"\d{4}", x) else x


def metinis_pokytis(indeksas: pd.Series) -> pd.Series:
    """Lygio indekso (datos indeksas) metinis pokytis, %: reikšmė / prieš 12 mėn. − 1."""
    s = indeksas.sort_index()
    pries = s.shift(12, freq="MS").reindex(s.index)
    return ((s / pries - 1) * 100).dropna()


def sk(v: float | None, zenklas: bool = True, dec: int = 1) -> str:
    """Skaičius lietuvišku formatu: +3,2"""
    if v is None or pd.isna(v):
        return "–"
    grupuoti = "," if abs(v) >= 10000 or (abs(v) >= 1000 and dec == 0) else ""   # 9 457, 12 345,6
    t = f"{v:+{grupuoti}.{dec}f}" if zenklas else f"{v:{grupuoti}.{dec}f}"
    return t.replace(",", "\u202f").replace(".", ",").replace("-", "−")


# ---------------- Vertinimas ----------------
def ivertink(reiksme: float, gera_kryptis: str, slenkstis: float) -> str:
    """gera_kryptis: 'didesne' arba 'mazesne'. Pokytis, mažesnis už slenkstį, laikomas stabiliu."""
    if reiksme is None or pd.isna(reiksme):
        return "nera"
    reiksme = round(float(reiksme), 6)          # kad 0,4999999 ar −0,5000001 nebūtų vertinami atsitiktinai
    if abs(reiksme) <= slenkstis:       # taisyklė: keičiasi tik pokytis, DIDESNIS už slenkstį
        return "stabilu"
    gerai = reiksme > 0 if gera_kryptis == "didesne" else reiksme < 0
    return "gereja" if gerai else "prasteja"


# ---------------- Grafikai ----------------
def stilius(fig: go.Figure, pavadinimas: str, paantraste: str, saltinis: str, aukstis: int = 440,
            vnt: str = " %", nulio_linija: bool = True, metiniai: bool = False):
    if nulio_linija:
        fig.add_hline(y=0, line=dict(color=TEKSTAS_ANTR, width=1))
    fig.add_annotation(text=saltinis, xref="paper", yref="paper", x=0, y=-0.25, showarrow=False,
                       xanchor="left", font=dict(size=11, color=TEKSTAS_ANTR))
    fig.update_layout(
        title=dict(text=f"<b>{pavadinimas}</b><br><span style='font-size:13px;color:{TEKSTAS_ANTR}'>{paantraste}</span>",
                   x=0, xanchor="left", font=dict(size=17, color=TEKSTAS)),
        font=dict(family=SRIFTAS, size=13, color=TEKSTAS_ANTR),
        plot_bgcolor=FONAS, paper_bgcolor=FONAS, height=aukstis,
        margin=dict(l=10, r=70, t=120, b=95),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font=dict(family=SRIFTAS, color=TEKSTAS)),
        legend=dict(orientation="h", y=1.0, x=0, yanchor="bottom", font=dict(size=12)),
        separators=", ",
    )
    fig.update_xaxes(showgrid=False, ticklabelstandoff=10, tickformat="%Y" if metiniai else "%Y-%m")
    fig.update_yaxes(gridcolor=TINKLELIS, zeroline=False, ticksuffix=vnt, ticklabelstandoff=8)
    if metiniai:
        fig.update_layout(hovermode="x unified", xaxis_hoverformat="%Y")
    return fig


def linijos(fig: go.Figure, serijos: list[tuple[str, pd.Series, str]],
            vnt: str = " %", zenklas: bool = True, dec: int = 1, zymekliai: bool = False,
            asis: tuple[float, float] | None = None, nuo_nulio: bool = True):
    """serijos: [(pavadinimas, Series su datų indeksu, spalva)]. Prideda linijas ir galines etiketes."""
    galai = []
    for vardas, s, spalva in serijos:
        s = s.dropna()
        fmt = f"{'+' if zenklas else ''}.{dec}f"
        fig.add_trace(go.Scatter(x=s.index, y=s.values, name=vardas,
                                 mode="lines+markers" if zymekliai else "lines",
                                 marker=dict(size=8, line=dict(color=FONAS, width=2)),
                                 line=dict(color=spalva, width=2),
                                 hovertemplate=f"{vardas}: %{{y:{fmt}}}{vnt}<extra></extra>"))
        galai.append((s.index[-1], s.iloc[-1]))
    # Mažiausias tarpas tarp galinių etikečių ≈ 16 px: perskaičiuojame į ašies vienetus
    visos = pd.concat([s for _, s, _ in serijos])
    if asis:
        apimtis = asis[1] - asis[0]
    elif nuo_nulio:
        apimtis = max(visos.max(), 0) - min(visos.min(), 0)
    else:
        apimtis = visos.max() - visos.min()
    tarpas = (apimtis or 1) * 16 / 230
    tvarka = sorted(range(len(galai)), key=lambda i: galai[i][1])
    poz, ankst = {}, None
    for i in tvarka:
        y = galai[i][1] if ankst is None else max(galai[i][1], ankst + tarpas)
        poz[i] = ankst = y
    for i, (x, y) in enumerate(galai):
        fig.add_annotation(x=x, y=poz[i], text=f"<b>{sk(y, zenklas, dec)}{vnt}</b>", showarrow=False,
                           xanchor="left", xshift=8, font=dict(color=TEKSTAS, size=12))
    return fig


def sparkline_svg(s: pd.Series, plotis: int = 140, aukstis: int = 40, nuo_nulio: bool = True) -> str:
    """Mažas tendencijos grafikas kortelei (SVG, be JavaScript)."""
    s = s.dropna()
    if len(s) < 2:
        return ""
    y0, y1 = (min(s.min(), 0), max(s.max(), 0)) if nuo_nulio else (s.min(), s.max())
    rng = (y1 - y0) or 1
    xs = [i / (len(s) - 1) * (plotis - 8) + 4 for i in range(len(s))]
    ys = [aukstis - 4 - (v - y0) / rng * (aukstis - 8) for v in s.values]
    tasku = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    nulis = aukstis - 4 - (0 - y0) / rng * (aukstis - 8)
    linija = (f'<line x1="0" x2="{plotis}" y1="{nulis:.1f}" y2="{nulis:.1f}" class="spark-nulis"/>'
              if nuo_nulio else "")
    return (f'<svg class="spark" viewBox="0 0 {plotis} {aukstis}" width="{plotis}" height="{aukstis}" aria-hidden="true">'
            f'{linija}'
            f'<polyline points="{tasku}" class="spark-linija"/>'
            f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="3" class="spark-taskas"/></svg>')


def palyginimo_tekstas(laikotarpis: str) -> str:
    """Iš rodiklio laikotarpio – su kuo lyginama: tas pats laikotarpis prieš metus."""
    import re
    if m := re.match(r"^(\d{4})M(\d{2})$", laikotarpis):
        return f"lyginant su {int(m[1]) - 1} m. {MENESIAI_SU[int(m[2]) - 1]}"
    if m := re.match(r"^(\d{4})K(\d)$", laikotarpis):
        return f"lyginant su {int(m[1]) - 1} m. {m[2]} ketv."
    if m := re.match(r"^(\d{4}) m\. sausis(?:–(\w+))?$", laikotarpis):
        iki = f"–{MENESIAI_SU[MENESIAI.index(m[2])]}" if m[2] else ""
        return f"lyginant su {int(m[1]) - 1} m. sausiu{iki}"
    if m := re.match(r"^(\d{4})", laikotarpis):
        return f"lyginant su {int(m[1]) - 1} m."
    return ""


def _daznis(s: pd.Series) -> str:
    if len(s) < 2:
        return "A"
    tarpas = pd.Series(s.index).diff().dt.days.median()
    return "M" if tarpas < 40 else ("Q" if tarpas < 100 else "A")


def _laik(d: pd.Timestamp, daznis: str) -> str:
    if daznis == "M":
        return f"{d.year}M{d.month:02d}"
    if daznis == "Q":
        return f"{d.year}K{(d.month - 1) // 3 + 1}"
    return str(d.year)


def dalis(pavadinimas: str, s: pd.Series, kryptis: str, slenkstis: float, budas: str = "pp",
          vienetai: str = "%", dec: int = 1, zenklas: bool = False, slenkscio_vnt: str | None = None) -> Dalis:
    """Įvertina papildomą matą ta pačia logika kaip pagrindinius rodiklius: naujausia reikšmė lyginama su tuo pačiu
    laikotarpiu prieš metus (metiniams – su ankstesniu turimu tašku).
    budas: „pp“ – skirtumas (proc. punktai ar vienetai), „proc“ – santykinis pokytis %, „lygis“ – vertinama pati
    reikšmė (ji jau yra metinis pokytis ar skirtumas), „info“ – nevertinama."""
    s = pd.to_numeric(s, errors="coerce").dropna().sort_index()
    daznis = _daznis(s)
    d, v = s.index[-1], float(s.iloc[-1])
    laik = _laik(d, daznis)
    if daznis == "A":
        pries_d = s.index[-2] if len(s) > 1 else None
        palyg = f"lyginant su {pries_d.year} m." if pries_d is not None else ""
    else:
        pries_d = d - pd.DateOffset(years=1)
        pries_d = pries_d if pries_d in s.index else None
        palyg = palyginimo_tekstas(laik)
    sd = 2 if 0 < slenkstis < 0.1 else 1          # slenksčio skaitmenys po kablelio
    u = slenkscio_vnt if slenkscio_vnt is not None else (" p. p." if vienetai.strip() == "%" else vienetai)
    if budas == "info":
        return Dalis(pavadinimas, v, vienetai, laik, "info", "", "nevertinama",
                     "Informacinis matas – jo kryptis savaime nėra nei gera, nei bloga.", zenklas, dec, s)
    if budas == "lygis":
        pok = v
        tekstas = f"{sk(v, True, dec)}{' %' if vienetai.strip() == '%' else vienetai}"
        auga, mazeja = "didesnis nei", "mažesnis nei"
        taisykle = (f"Gerėja, kai reikšmė {'didesnė' if kryptis == 'didesne' else 'mažesnė'} nei "
                    f"{sk(slenkstis if kryptis == 'didesne' else -slenkstis, True, sd)}{u}; prastėja, kai "
                    f"{'mažesnė' if kryptis == 'didesne' else 'didesnė'} nei "
                    f"{sk(-slenkstis if kryptis == 'didesne' else slenkstis, True, sd)}{u}; kitu atveju – stabilu.")
    else:
        if pries_d is None:
            return Dalis(pavadinimas, v, vienetai, laik, "nera", "", "nėra palyginimo",
                         "Nėra ankstesnio laikotarpio duomenų.", zenklas, dec, s)
        pv = float(s[pries_d])
        if budas == "proc":
            pok = (v / pv - 1) * 100 if pv else float("nan")
            tekstas, u = f"{sk(pok)} %", " %"
        else:
            pok = v - pv
            tekstas = f"{sk(pok, True, dec)}{u}"
        geras, blogas = ("padidėja", "sumažėja") if kryptis == "didesne" else ("sumažėja", "padidėja")
        taisykle = (f"Gerėja, kai {geras} daugiau nei {sk(slenkstis, False, sd)}{u}; prastėja, kai {blogas} "
                    f"daugiau nei {sk(slenkstis, False, sd)}{u}; kitu atveju – stabilu.")
    return Dalis(pavadinimas, v, vienetai, laik, ivertink(pok, kryptis, slenkstis), tekstas, palyg, taisykle,
                 zenklas, dec, s)


def papildomas_grafikas(pavadinimas: str, paantraste: str, saltinis: str, serijos: list, vnt: str = "",
                        dec: int = 1, nuo: str | None = None, nuo_nulio: bool = True, zenklas: bool = False):
    """Paprastas linijinis grafikas sudedamosioms dalims: serijos = [(vardas, pd.Series), ...]."""
    import plotly.graph_objects as go
    f = go.Figure()
    rinkinys = []
    for i, (vardas, s) in enumerate(serijos):
        s = s.dropna()
        if nuo:
            s = s[s.index >= nuo]
        rinkinys.append((vardas, s, SERIJOS[i % len(SERIJOS)]))
    linijos(f, rinkinys, vnt=vnt, zenklas=zenklas, dec=dec, zymekliai=True)
    stilius(f, pavadinimas, paantraste, saltinis, vnt=vnt, nulio_linija=zenklas, metiniai=True)
    if nuo_nulio:
        f.update_yaxes(rangemode="tozero")
    return f


def slugas(tekstas: str) -> str:
    import unicodedata
    x = unicodedata.normalize("NFKD", tekstas).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", x).strip("-")[:60]
