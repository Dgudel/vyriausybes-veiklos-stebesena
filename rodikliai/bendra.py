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
MENESIAI = ["sausis", "vasaris", "kovas", "balandis", "gegužė", "birželis", "liepa",
            "rugpjūtis", "rugsėjis", "spalis", "lapkritis", "gruodis"]


# ---------------- Rodiklio aprašas ----------------
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


# ---------------- Duomenys ----------------
def skaityk(failas: str, datagov_modelis: str | None = None) -> pd.DataFrame:
    """Skaito duomenis iš duomenys/ aplanko. Jei nurodytas data.gov.lt modelis ir aplinkoje
    ATNAUJINTI=1 (taip daro GitHub Actions), prieš tai atsisiunčia naujausią versiją."""
    kelias = DUOMENYS / failas
    if datagov_modelis and os.environ.get("ATNAUJINTI") == "1":
        import urllib.request
        url = f"https://get.data.gov.lt/{datagov_modelis.strip('/')}/:format/csv"
        kelias = kelias.with_suffix(".csv")
        print(f"  ↓ {url}")
        urllib.request.urlretrieve(url, kelias)
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
    t = f"{v:+.{dec}f}" if zenklas else f"{v:.{dec}f}"
    return t.replace(".", ",").replace("-", "−")


# ---------------- Vertinimas ----------------
def ivertink(reiksme: float, gera_kryptis: str, slenkstis: float) -> str:
    """gera_kryptis: 'didesne' arba 'mazesne'. Pokytis, mažesnis už slenkstį, laikomas stabiliu."""
    if reiksme is None or pd.isna(reiksme):
        return "nera"
    if abs(reiksme) < slenkstis:
        return "stabilu"
    gerai = reiksme > 0 if gera_kryptis == "didesne" else reiksme < 0
    return "gereja" if gerai else "prasteja"


# ---------------- Grafikai ----------------
def stilius(fig: go.Figure, pavadinimas: str, paantraste: str, saltinis: str, aukstis: int = 440):
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
    fig.update_xaxes(showgrid=False, ticklabelstandoff=10, tickformat="%Y-%m")
    fig.update_yaxes(gridcolor=TINKLELIS, zeroline=False, ticksuffix=" %", ticklabelstandoff=8)
    return fig


def linijos(fig: go.Figure, serijos: list[tuple[str, pd.Series, str]]):
    """serijos: [(pavadinimas, Series su datų indeksu, spalva)]. Prideda linijas ir galines etiketes."""
    galai = []
    for vardas, s, spalva in serijos:
        s = s.dropna()
        fig.add_trace(go.Scatter(x=s.index, y=s.values, name=vardas, mode="lines",
                                 line=dict(color=spalva, width=2),
                                 hovertemplate=f"{vardas}: %{{y:+.1f}} %<extra></extra>"))
        galai.append((s.index[-1], s.iloc[-1]))
    visos = pd.concat([s for _, s, _ in serijos])
    tarpas = 0.07 * ((visos.max() - visos.min()) or 1)
    tvarka = sorted(range(len(galai)), key=lambda i: galai[i][1])
    poz, ankst = {}, None
    for i in tvarka:
        y = galai[i][1] if ankst is None else max(galai[i][1], ankst + tarpas)
        poz[i] = ankst = y
    for i, (x, y) in enumerate(galai):
        fig.add_annotation(x=x, y=poz[i], text=f"<b>{sk(y)} %</b>", showarrow=False,
                           xanchor="left", xshift=8, font=dict(color=TEKSTAS, size=12))
    return fig


def sparkline_svg(s: pd.Series, plotis: int = 140, aukstis: int = 40) -> str:
    """Mažas tendencijos grafikas kortelei (SVG, be JavaScript)."""
    s = s.dropna()
    if len(s) < 2:
        return ""
    y0, y1 = min(s.min(), 0), max(s.max(), 0)
    rng = (y1 - y0) or 1
    xs = [i / (len(s) - 1) * (plotis - 8) + 4 for i in range(len(s))]
    ys = [aukstis - 4 - (v - y0) / rng * (aukstis - 8) for v in s.values]
    tasku = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    nulis = aukstis - 4 - (0 - y0) / rng * (aukstis - 8)
    return (f'<svg class="spark" viewBox="0 0 {plotis} {aukstis}" width="{plotis}" height="{aukstis}" aria-hidden="true">'
            f'<line x1="0" x2="{plotis}" y1="{nulis:.1f}" y2="{nulis:.1f}" class="spark-nulis"/>'
            f'<polyline points="{tasku}" class="spark-linija"/>'
            f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="3" class="spark-taskas"/></svg>')
