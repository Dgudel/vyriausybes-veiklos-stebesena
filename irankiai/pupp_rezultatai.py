"""
PUPP (pagrindinio ugdymo pasiekimų patikrinimo) rezultatų surinkimas iš NŠA svetainės.

1. Nuskaito NŠA puslapį ir suranda visus PDF failus (metai, dalykas, savivaldybių/mokyklų lygis).
2. Atsisiunčia PDF į  <APLANKAS>/pdf/
3. Kiekvieną PDF paverčia Excel failu (visos lentelės, lapas – PDF puslapis) į  <APLANKAS>/excel/
4. Sukuria suvestinę  <APLANKAS>/PUPP_suvestine.xlsx :
     • lapas „Lietuva“      – šalies eilutė iš kiekvieno savivaldybių PDF: kandidatai, balų 1–10 pasiskirstymas,
                              vidurkis, neišlaikiusių (1–3 balai) ir aukštai įvertintų (9–10 balų) dalis
   ir  <APLANKAS>/pupp_salies_eilutes.csv – tas pats švieslentei (nukopijuokite į svieslente/duomenys/)
     • lapas „Failai“       – visų PDF sąrašas su nuorodomis ir apdorojimo būsena
     • lapas „Visos_eilutes“ – visos iš PDF ištrauktos lentelių eilutės (žali duomenys)

Paleidimas:  pip install requests beautifulsoup4 pdfplumber openpyxl pandas
             python3.10 pupp_rezultatai.py
Pakartotinai paleidus jau atsisiųsti PDF nesiunčiami iš naujo.
"""
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import pdfplumber
import requests
from bs4 import BeautifulSoup

# ---------------- NUSTATYMAI ----------------
APLANKAS = Path("/Users/user/Dropbox/Mac/Downloads/PUPP")
PUSLAPIS = ("https://www.nsa.smsm.lt/pasiekimu-departamentas/egzaminai-ir-pasiekimu-patikrinimai/"
            "pagrindinio-ugdymo-pasiekimu-patikrinimai/pupp-rezultatai/")
LYGIAI = {"savivaldybės", "mokyklos"}   # palikite tik {"savivaldybės"}, jei mokyklų failų nereikia
PAUZE_S = 0.5                           # pauzė tarp atsisiuntimų, kad neapkrautume serverio
NARSYKLE = {"User-Agent": "Mozilla/5.0 (PUPP duomenu surinkimas svieslentei)"}

PDF_DIR, XLS_DIR = APLANKAS / "pdf", APLANKAS / "excel"
SALIES_EILUTE = re.compile(r"^\s*(Visa Lietuva|Iš viso|Viso|Lietuva|Šalis|Šalies)\b", re.I)


# ---------------- 1. NUORODOS ----------------
def _metai_virs(el) -> str:
    """Artimiausi ankstesni metai (2013–2029) puslapio tekste virš nuorodos."""
    for t in el.find_all_previous(string=re.compile(r"\b20[12]\d\b")):
        if t.parent and t.parent.name in ("script", "style"):
            continue
        m = re.search(r"\b(20[12]\d)\b", t)
        if m:
            return m.group(1)
    return ""


def _lygis(a, href: str) -> str:
    vardas = Path(urlparse(href).path).name.lower()
    if re.search(r"mok", vardas):
        return "mokyklos"
    if re.search(r"sav", vardas):
        return "savivaldybės"
    td = a.find_parent(["td", "th"])
    table = a.find_parent("table")
    if td is not None and table is not None:              # pagal stulpelio antraštę
        idx = len(td.find_previous_siblings(["td", "th"]))
        antraste = table.find("tr")
        if antraste:
            celes = antraste.find_all(["td", "th"])
            if idx < len(celes) and "mokykl" in celes[idx].get_text().lower():
                return "mokyklos"
    return "savivaldybės"


def surask_pdf() -> pd.DataFrame:
    r = requests.get(PUSLAPIS, headers=NARSYKLE, timeout=60)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    irasai, matyti = [], set()
    for a in soup.find_all("a", href=True):
        href = urljoin(PUSLAPIS, a["href"])
        if not href.lower().split("?")[0].endswith(".pdf") or href in matyti:
            continue
        matyti.add(href)
        tr = a.find_parent("tr")
        dalykas = tr.find(["td", "th"]).get_text(" ", strip=True) if tr else a.get_text(" ", strip=True)
        irasai.append({"metai_puslapyje": _metai_virs(a), "dalykas": dalykas,
                       "lygis": _lygis(a, href), "url": href,
                       "failas": Path(urlparse(href).path).name})
    df = pd.DataFrame(irasai)
    print(f"Rasta PDF nuorodų: {len(df)}")
    return df[df["lygis"].isin(LYGIAI)].reset_index(drop=True)


# ---------------- 2. ATSISIUNTIMAS ----------------
def atsisiusk(df: pd.DataFrame) -> pd.DataFrame:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    keliai = []
    for i, e in df.iterrows():
        # unikalus vardas: metai_lygis_originalus-pavadinimas (kai kurie pavadinimai kartojasi skirtingais metais)
        vardas = f"{e.metai_puslapyje or 'xxxx'}_{e.lygis[:3]}_{e.failas}"
        kelias = PDF_DIR / vardas
        if not kelias.exists():
            try:
                r = requests.get(e.url, headers=NARSYKLE, timeout=120)
                r.raise_for_status()
                kelias.write_bytes(r.content)
                print(f"  ↓ {vardas}")
                time.sleep(PAUZE_S)
            except Exception as ex:
                print(f"  ✗ {vardas}: {ex}")
                kelias = None
        keliai.append(kelias)
    df = df.copy()
    df["pdf"] = keliai
    return df


# ---------------- 3. PDF → EXCEL ----------------
def pdf_i_excel(pdf: Path) -> tuple[list[pd.DataFrame], str]:
    """Ištraukia visas lenteles; grąžina (lentelės, viso PDF tekstas)."""
    lenteles, tekstas = [], []
    with pdfplumber.open(pdf) as doc:
        for nr, psl in enumerate(doc.pages, 1):
            tekstas.append(psl.extract_text() or "")
            for t in psl.extract_tables():
                if t and len(t) > 1:
                    d = pd.DataFrame(t)
                    d.insert(0, "psl", nr)
                    lenteles.append(d)
    XLS_DIR.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(XLS_DIR / (pdf.stem + ".xlsx")) as w:
        if lenteles:
            for i, d in enumerate(lenteles, 1):
                d.to_excel(w, sheet_name=f"lentele_{i}"[:31], index=False, header=False)
        else:   # lentelių neatpažino – išsaugome bent tekstą
            pd.DataFrame({"tekstas": "\n".join(tekstas).splitlines()}).to_excel(w, sheet_name="tekstas", index=False)
    return lenteles, "\n".join(tekstas)


# ---------------- 4. ŠALIES EILUTĖ ----------------
SK = re.compile(r"\d+(?:[.,]\d+)?%?")


def salies_eilute(tekstas: str) -> dict:
    """Randa šalies eilutę („Viso“, „Visa Lietuva“…) ir iš po jos einančių skaičių atrenka:
    kandidatų skaičių, 10 balų skaičių (jų suma turi lygti kandidatų skaičiui) ir vidurkį.
    Procentai ignoruojami – dalis perskaičiuojama iš skaičių, todėl formatų skirtumai netrukdo."""
    eil = tekstas.splitlines()
    for i, e in enumerate(eil):
        if not SALIES_EILUTE.match(e):
            continue
        tokenai = SK.findall(" ".join(eil[i:i + 8]))
        sveiki = [int(t) for t in tokenai if t.isdigit()]
        desim = [float(t.replace(",", ".")) for t in tokenai if not t.endswith("%") and re.search(r"[.,]", t)]
        if len(sveiki) < 11:
            continue
        kand, balai = sveiki[0], sveiki[1:11]
        patikra = sum(balai) == kand
        vidurkis = next((x for x in desim if 1 <= x <= 10), None)
        return {"kandidatai": kand, **{f"balas_{b}": balai[b - 1] for b in range(1, 11)},
                "vidurkis": vidurkis,
                "neislaike_1_3_proc": round(100 * sum(balai[:3]) / kand, 2) if patikra else None,
                "aukstas_9_10_proc": round(100 * sum(balai[8:]) / kand, 2) if patikra else None,
                "patikra_suma_sutampa": patikra}
    return {}


SALIES_CELE = re.compile(r"^\s*(Visa Lietuva|Iš viso|Viso|Lietuva)\s*$", re.I)


def _sk(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    t = str(x).split("\n")[0].strip().replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def salies_is_lenteliu(lenteles: list[pd.DataFrame]) -> dict:
    """Patikimesnis būdas: šalies eilutė iš ištrauktų lentelių (kiekviename langelyje „skaičius\nprocentas“)."""
    for d in lenteles:
        for _, r in d.drop(columns="psl").iterrows():
            celes = [c for c in r.tolist() if c is not None and not (isinstance(c, float) and pd.isna(c)) and str(c).strip()]
            if not celes or not SALIES_CELE.match(str(celes[0])):
                continue
            sk = [v for v in (_sk(c) for c in celes[1:]) if v is not None]
            if len(sk) < 12:
                continue
            kand, balai, vid = sk[0], sk[1:11], sk[-1]
            if abs(sum(balai) - kand) > max(2, 0.005 * kand) or not (1 <= vid <= 10):
                continue
            balai = [int(b) for b in balai]
            return {"kandidatai": int(kand), **{f"balas_{b}": balai[b - 1] for b in range(1, 11)},
                    "vidurkis": vid,
                    "neislaike_1_3_proc": round(100 * sum(balai[:3]) / kand, 2),
                    "aukstas_9_10_proc": round(100 * sum(balai[8:]) / kand, 2),
                    "patikra_suma_sutampa": True}
    return {}


def metai_pdf(tekstas: str) -> str:
    m = re.search(r"\b(20[12]\d)\s*m\.", tekstas[:1500])
    return m.group(1) if m else ""


# ---------------- PAGRINDINĖ ----------------
def main():
    APLANKAS.mkdir(parents=True, exist_ok=True)
    failai = atsisiusk(surask_pdf())

    salis, visos, busenos = [], [], []
    for _, e in failai.iterrows():
        if e.pdf is None:
            busenos.append("neatsisiųsta")
            continue
        try:
            lenteles, tekstas = pdf_i_excel(e.pdf)
        except Exception as ex:
            busenos.append(f"klaida: {ex}")
            continue
        metai = metai_pdf(tekstas) or e.metai_puslapyje
        bendra = {"metai": metai, "metai_puslapyje": e.metai_puslapyje, "dalykas": e.dalykas,
                  "lygis": e.lygis, "failas": e.pdf.name}
        for d in lenteles:
            d = d.copy()
            for k, v in reversed(bendra.items()):
                d.insert(0, k, v)
            visos.append(d)
        busena = f"lentelių: {len(lenteles)}" if lenteles else "lentelių neatpažinta (išsaugotas tekstas)"
        if e.lygis == "savivaldybės":
            s = salies_is_lenteliu(lenteles) or salies_eilute(tekstas)
            if s:
                salis.append({**bendra, **s})
                busena += "; šalies eilutė " + ("✓" if s["patikra_suma_sutampa"] else "⚠ suma nesutampa")
            else:
                busena += "; šalies eilutė nerasta"
        busenos.append(busena)
        print(f"  ✓ {e.pdf.name}: {busena}")

    failai["busena"] = busenos
    failai["pdf"] = failai["pdf"].astype(str)
    salis_df = pd.DataFrame(salis)
    if not salis_df.empty:
        salis_df = salis_df.sort_values(["dalykas", "metai"])
    with pd.ExcelWriter(APLANKAS / "PUPP_suvestine.xlsx") as w:
        salis_df.to_excel(w, sheet_name="Lietuva", index=False)
        failai.to_excel(w, sheet_name="Failai", index=False)
        if visos:
            pd.concat(visos, ignore_index=True).to_excel(w, sheet_name="Visos_eilutes", index=False)

    # Švieslentei: tik patikrintos šalies eilutės, stulpeliai b1..b10
    if not salis_df.empty:
        sv = salis_df[salis_df["patikra_suma_sutampa"]].rename(columns={f"balas_{i}": f"b{i}" for i in range(1, 11)})
        sv[["failas", "metai", "dalykas", "kandidatai"] + [f"b{i}" for i in range(1, 11)] + ["vidurkis"]] \
            .to_csv(APLANKAS / "pupp_salies_eilutes.csv", index=False)

    print(f"\n✅ Suvestinė: {APLANKAS / 'PUPP_suvestine.xlsx'}")
    print(f"   Šalies eilučių: {len(salis_df)}; iš jų patikrintų (suma sutampa): "
          f"{int(salis_df['patikra_suma_sutampa'].sum()) if not salis_df.empty else 0}")
    print("   PDF be šalies eilutės ar su klaidomis – žr. lapą „Failai“, stulpelį „busena“.")


if __name__ == "__main__":
    main()
