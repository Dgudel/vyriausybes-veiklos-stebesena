"""7. Valstybės valdymo kokybė: pasitikėjimas institucijomis ir pasitenkinimas demokratija (Standartinis Eurobarometras).

Duomenys – duomenys/eurobarometras_lt.csv (banga, laikotarpis, rodiklis, LT, ES). Kai ATNAUJINTI=1, per data.europa.eu
API ieškoma naujų Standartinio Eurobarometro bangų, atsisiunčiamas jų „Volume A“ Excel failas ir iš jo pagal klausimo
tekstą ištraukiamos Lietuvos ir ES-27 reikšmės. Eurobarometras vyksta du kartus per metus (pavasarį ir rudenį), todėl
naujausia banga lyginama su tos pačios metų pusės banga prieš metus."""
import io
import os
import re

import pandas as pd
import plotly.graph_objects as go

from .bendra import DUOMENYS, SERIJOS, Rodiklis, dalis, ivertink, linijos, sk, stilius, t

FAILAS = DUOMENYS / "eurobarometras_lt.csv"
SLENKSTIS = 3.0     # proc. punktai (~1000 respondentų imties paklaida yra apie ±3 p. p.)
API = "https://data.europa.eu/api/hub/search/"

KLAUSIMAI = {   # rodiklis: (žodžiai klausimo tekste, draudžiami žodžiai, eilutės etiketės)
    "vyriausybe": (["trust", "government"], ["european", "regional", "local", "response", "russia", "ukraine"],
                   ["tend to trust"]),
    "seimas": (["trust", "parliament"], ["european parliament"], ["tend to trust"]),
    "teismai": (["trust", "justice"], [], ["tend to trust"]),
    "policija": (["trust", "police"], [], ["tend to trust"]),
    "partijos": (["trust", "political parties"], [], ["tend to trust"]),
    "demokratija": (["democracy works in (our country)"], ["in the eu", "european union"],
                    ["total 'satisfied'", "total satisfied", "total ‘satisfied’"]),
}
PAV = {"vyriausybe": ("Pasitiki Vyriausybe", "Trust the Government"),
       "seimas": ("Pasitiki Seimu", "Trust the Seimas (parliament)"),
       "teismai": ("Pasitiki teismais ir teisine sistema", "Trust justice and the legal system"),
       "policija": ("Pasitiki policija", "Trust the police"),
       "partijos": ("Pasitiki politinėmis partijomis", "Trust political parties"),
       "demokratija": ("Patenkinti demokratijos veikimu Lietuvoje", "Satisfied with the way democracy works in Lithuania")}


# ---------------- atnaujinimas ----------------
def _reiksmes(df, etiketes):
    hdr = next((i for i in range(min(len(df), 30)) if "LT" in [str(v).strip() for v in df.iloc[i].values]), None)
    if hdr is None:
        return None
    row = [str(v).strip() for v in df.iloc[hdr].values]
    lt = row.index("LT")
    eu = next((j for j, v in enumerate(row) if re.search(r"\b(EU|UE)\s?27\b", v)), None)
    for i in range(hdr + 1, len(df) - 1):
        lab = " ".join(str(v) for v in df.iloc[i, :max(3, eu or 2)].values if isinstance(v, str)).lower().strip()
        if any(lab.endswith(e) for e in etiketes) and not lab.endswith("very satisfied"):
            for k in (i, i + 1):        # procentai – toje pačioje arba kitoje eilutėje (dalis nuo 1)
                a = pd.to_numeric(df.iloc[k, lt], errors="coerce")
                if pd.notna(a) and a <= 1:
                    b = pd.to_numeric(df.iloc[k, eu], errors="coerce") if eu is not None else float("nan")
                    return round(a * 100, 1), (round(b * 100, 1) if pd.notna(b) else None)
    return None


def _is_failo(turinys: bytes) -> tuple[dict, str]:
    knyga = pd.read_excel(io.BytesIO(turinys), sheet_name=None, header=None)
    laikas = ""
    for lapas, df in knyga.items():
        if lapas.lower() == "content":
            for r in df.itertuples(index=False):
                if str(r[0]).startswith("Fieldwork"):
                    m = re.search(r"/(\d{1,2})/(\d{4})", str(r[1]))      # pradžios mėnuo: „9/10 - 5/11/2025“
                    d = re.match(r"\s*\d{1,2}/(\d{1,2})", str(r[1]))
                    if m and d:
                        laikas = f"{m[2]}-{int(d[1]):02d}"
    rez = {}
    for lapas, df in knyga.items():
        if lapas.lower() in ("index", "content") or df.empty:
            continue
        q = re.sub(r"\s+", " ", " ".join(str(v) for v in df.iloc[:8].values.ravel() if isinstance(v, str))).lower()
        for rod, (zod, draud, etik) in KLAUSIMAI.items():
            if rod not in rez and all(z in q for z in zod) and not any(z in q for z in draud):
                v = _reiksmes(df, etik)
                if v:
                    rez[rod] = (*v, lapas)
    return rez, laikas


def _atnaujink():
    import requests
    seni = pd.read_csv(FAILAS)
    turimos = set(seni.banga)
    naujos = []
    for psl in range(3):
        r = requests.get(API + "search", params={"q": "Standard Eurobarometer", "filter": "dataset", "limit": 100,
                                                 "page": psl}, timeout=60).json()["result"]["results"]
        for it in r:
            m = re.match(r"Standard Eurobarometer (?:STD)?(\d+)", (it.get("title") or {}).get("en", ""))
            if m and int(m[1]) > max(turimos) and int(m[1]) not in [n for n, _ in naujos]:
                naujos.append((int(m[1]), it["id"]))
    eil = []
    for n, rid in sorted(naujos):
        d = requests.get(API + "datasets/" + rid, timeout=60).json()["result"]
        vol = [x for x in d.get("distributions", [])
               if re.search(r"vol(?:ume)?[ _]?A(?![A-Za-z])", (x.get("title") or {}).get("en", ""), re.I)
               and (x.get("title") or {}).get("en", "").lower().endswith(".xlsx")]
        if not vol:
            print(f"  ⚠ Eurobarometras {n}: „Volume A“ .xlsx nerastas")
            continue
        b = requests.get(vol[0]["access_url"][0], timeout=300).content
        rez, laikas = _is_failo(b)
        if not rez or not laikas:
            print(f"  ⚠ Eurobarometras {n}: reikšmių nepavyko ištraukti")
            continue
        eil += [{"banga": n, "laikotarpis": laikas, "rodiklis": k, "LT": v[0], "ES": v[1], "lapas": v[2]}
                for k, v in rez.items()]
        print(f"  ↓ Eurobarometras {n} ({laikas}): {len(rez)} rodikliai")
    if eil:
        pd.concat([seni, pd.DataFrame(eil)]).to_csv(FAILAS, index=False)


# ---------------- rodiklis ----------------
def _serijos(rod: str):
    d = pd.read_csv(FAILAS)
    d = d[d.rodiklis == rod].copy()
    d["data"] = pd.to_datetime(d.laikotarpis + "-01")
    d = d.sort_values("data").set_index("data")
    return d.LT.astype(float), d.ES.astype(float)


def _ta_pati_puse(s: pd.Series) -> pd.Series:
    """Tik tos pačios metų pusės bangos kaip naujausia (pavasaris – I pusmetis, ruduo – II), kad palyginimas
    būtų su ta pačia banga prieš metus; data – sausio 1 d., kad būtų atpažinta kaip metinė eilutė."""
    puse = s.index[-1].month <= 6
    x = s[(s.index.month <= 6) == puse]
    x = x[~x.index.year.duplicated(keep="last")]
    x.index = [pd.Timestamp(d.year, 1, 1) for d in x.index]
    return x


def _banga(d: pd.Timestamp) -> str:
    return t(f"{d.year} m. {'pavasaris' if d.month <= 6 else 'ruduo'}", f"{'spring' if d.month <= 6 else 'autumn'} {d.year}")


def rodiklis() -> Rodiklis:
    if os.environ.get("ATNAUJINTI") == "1":
        try:
            _atnaujink()
        except Exception as e:
            print(f"  ⚠ Eurobarometras neatnaujintas ({e}); naudojamas esamas failas")
    lt, es = _serijos("vyriausybe")
    palyg = _ta_pati_puse(lt)
    pask = lt.iloc[-1]
    pries = palyg.iloc[-2]
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)
    d_pask = lt.index[-1]
    d_pries = lt[(lt.index.year == palyg.index[-2].year) & ((lt.index.month <= 6) == (d_pask.month <= 6))].index[-1]

    _dalys = []
    for rod in ("seimas", "teismai", "policija", "partijos", "demokratija"):
        s, _ = _serijos(rod)
        _dalys.append(dalis(t(*PAV[rod]), _ta_pati_puse(s), "didesne", SLENKSTIS))

    f1 = go.Figure()
    linijos(f1, [(t(*PAV[r]), _serijos(r)[0], SERIJOS[i]) for i, r in enumerate(["vyriausybe", "seimas", "teismai",
                                                                                  "policija"])],
            zenklas=False, zymekliai=True)
    stilius(f1, t("Pasitikėjimas institucijomis Lietuvoje", "Trust in institutions in Lithuania"),
            t("Gyventojai, kurie „linkę pasitikėti“, %", "Population who 'tend to trust', %"),
            t("Šaltinis: Standartinis Eurobarometras (Volume A), data.europa.eu",
              "Source: Standard Eurobarometer (Volume A), data.europa.eu"), nulio_linija=False, metiniai=True)
    f1.update_yaxes(range=[0, 100])

    f2 = go.Figure()
    lv, ev = _serijos("vyriausybe")
    ls, esm = _serijos("seimas")
    linijos(f2, [(t("Vyriausybė – Lietuva", "Government – Lithuania"), lv, SERIJOS[0]),
                 (t("Vyriausybė – ES-27", "Government – EU-27"), ev.dropna(), SERIJOS[1]),
                 (t("Seimas – Lietuva", "Parliament – Lithuania"), ls, SERIJOS[2]),
                 (t("Parlamentas – ES-27", "Parliament – EU-27"), esm.dropna(), SERIJOS[3])], zenklas=False, zymekliai=True)
    stilius(f2, t("Pasitikėjimas Vyriausybe ir parlamentu: Lietuva ir ES", "Trust in government and parliament: Lithuania and the EU"),
            t("Gyventojai, kurie „linkę pasitikėti“, %", "Population who 'tend to trust', %"),
            t("Šaltinis: Standartinis Eurobarometras", "Source: Standard Eurobarometer"), nulio_linija=False, metiniai=True)
    f2.update_yaxes(range=[0, 70])

    f3 = go.Figure()
    ld, ed = _serijos("demokratija")
    linijos(f3, [("Lietuva", ld, SERIJOS[0]), ("ES-27", ed.dropna(), SERIJOS[1])], zenklas=False, zymekliai=True)
    stilius(f3, t("Pasitenkinimas demokratijos veikimu šalyje", "Satisfaction with the way democracy works in the country"),
            t("Labai ir gana patenkinti, %", "Very and fairly satisfied, %"),
            t("Šaltinis: Standartinis Eurobarometras", "Source: Standard Eurobarometer"), nulio_linija=False, metiniai=True)
    f3.update_yaxes(range=[0, 100])

    lentele = pd.read_csv(FAILAS).pivot_table(index=["banga", "laikotarpis"], columns="rodiklis", values="LT").reset_index()
    kryptis = t("padidėjo", "rose by") if pokytis > 0 else t("sumažėjo", "fell by")
    return Rodiklis(
        dalys=_dalys,
        id="pasitikejimas-institucijomis",
        pavadinimas=t("Pasitikėjimas Vyriausybe", "Trust in the Government"),
        trumpas_aprasas=t("gyventojai, linkę pasitikėti Vyriausybe", "population who tend to trust the Government"),
        reiksme=pask, vienetai="%", laikotarpis=_banga(d_pask), busena=busena, dec=0,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Naujausia Eurobarometro banga lyginama su tos pačios metų pusės banga prieš metus. "
                             f"Gerėja, kai pasitikinčiųjų dalis padidėja daugiau nei {sk(SLENKSTIS, False, 0)} p. p. "
                             f"(apytikslė imties paklaida); prastėja, kai tiek pat sumažėja; kitu atveju – stabilu.",
                             f"The latest Eurobarometer wave is compared with the wave from the same half of the previous "
                             f"year. Improving when the share rises by more than {sk(SLENKSTIS, False, 0)} pp (roughly the "
                             f"sampling error); worsening when it falls by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{_banga(d_pask)}: Vyriausybe linkę pasitikėti {sk(pask, False, 0)} % gyventojų "
                                 f"({_banga(d_pries)} – {sk(pries, False, 0)} %; ES vidurkis – {sk(es.iloc[-1], False, 0)} %). "
                                 f"Dalis {kryptis} {sk(abs(pokytis), False, 0)} p. p.",
                                 f"{_banga(d_pask).capitalize()}: {sk(pask, False, 0)}% of the population tend to trust the "
                                 f"Government ({_banga(d_pries)}: {sk(pries, False, 0)}%; EU average {sk(es.iloc[-1], False, 0)}%). "
                                 f"The share {kryptis} {sk(abs(pokytis), False, 0)} pp."),
        sparkline=lt,
        grafikai=[f1, f2, f3],
        apibrezimas=t("Standartinio Eurobarometro klausimas: „Kiek pasitikite tam tikromis institucijomis? Ar esate linkęs joms "
                      "pasitikėti, ar nepasitikėti?“ Rodoma atsakiusiųjų „linkęs pasitikėti“ dalis. Pasitenkinimas demokratija – "
                      "„labai“ ir „gana“ patenkintų demokratijos veikimu šalyje dalis. Lietuvoje kiekvienoje bangoje apklausiama "
                      "apie 1000 gyventojų.",
                      "Standard Eurobarometer question: 'How much trust do you have in certain institutions? Do you tend to "
                      "trust or tend not to trust them?' The share answering 'tend to trust' is shown. Satisfaction with "
                      "democracy is the share 'very' or 'fairly' satisfied with the way democracy works in the country. "
                      "About 1,000 people are interviewed in Lithuania in each wave."),
        pastabos=[t("Imtis nedidelė, todėl pokyčiai iki ~3 p. p. gali būti atsitiktiniai. Vertinama tos pačios metų pusės "
                    "bangos lyginant, nes nuomonės priklauso ir nuo apklausos laiko (pvz., rinkimų ciklo).",
                    "The sample is small, so changes of up to ~3 pp may be random. Waves from the same half of the year are "
                    "compared, since opinions also depend on the timing of the survey (e.g. the electoral cycle).")],
        saltiniai=[(t("Standartinis Eurobarometras – data.europa.eu", "Standard Eurobarometer – data.europa.eu"),
                    "https://data.europa.eu/data/datasets?query=Standard%20Eurobarometer&locale=en"),
                   ("Eurobarometer", "https://europa.eu/eurobarometer/surveys/browse/all/series/4961")],
        lentele=lentele,
    )
