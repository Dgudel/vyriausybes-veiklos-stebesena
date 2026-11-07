"""
VBE (valstybinių brandos egzaminų) rezultatų surinkimas iš NŠA svetainės (PDF, 2016–2024 m.).

1. Nuskaito NŠA puslapį ir suranda PDF failus: metai, dalykas, lentelės tipas
   (savivaldybės / mokyklų tipai / mokyklos / profesinės mokyklos).
2. Atsisiunčia PDF į  <APLANKAS>/pdf/   (metai > PASKUTINIAI_PDF_METAI praleidžiami –
   2025–2026 m. NŠA skelbia Excel, juos jau turite).
3. Kiekvieną PDF paverčia Excel failu į  <APLANKAS>/excel/  (lapas „eilutes“ – atpažintos eilutės,
   lapas „lenteles“ – visos pdfplumber lentelės).
4. Sukuria  <APLANKAS>/VBE_suvestine.xlsx :
     • „Lietuva“       – šalies rezultatai pagal metus ir dalyką, susumuoti iš savivaldybių eilučių:
                         laikė, išlaikė, balų intervalai 16–35 / 36–85 / 86–100, dalys %
     • „Savivaldybes“  – visų metų ir dalykų savivaldybių eilutės (viena lentelė)
     • „Failai“        – visi PDF ir jų apdorojimo būsena
     • „Vidurkiai_nuo_2025“ ir „Mokyklu_vidurkiai_nuo_2025“ – iš Excel failų VBE_vidurkiai_pagal_mokyklas*.xlsx,
                         jei juos padėsite į tą patį aplanką (nuo 2025 m. NŠA skelbia tik mokyklų vidurkius)
   ir CSV švieslentei:  vbe_salies_eilutes.csv,  vbe_mokyklu_vidurkiai.csv

Pastaba: NŠA lentelėse pateikiami tik mokyklų mokinių rezultatai (be eksternų ir buvusių mokinių),
o šalies sumos eilutės savivaldybių lentelėse nėra – ją apskaičiuojame susumavę savivaldybes.

Paleidimas:  pip install requests beautifulsoup4 pdfplumber openpyxl pandas
             python3.10 vbe_rezultatai.py
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
APLANKAS = Path("/Users/user/Dropbox/Mac/Downloads/VBE")
PUSLAPIS = ("https://www.nsa.smsm.lt/pasiekimu-departamentas/egzaminai-ir-pasiekimu-patikrinimai/"
            "valstybiniai-brandos-egzaminai/vbe-rezultatai/")
PASKUTINIAI_PDF_METAI = 2024        # vėlesni metai jau turimi Excel formatu
TIPAI = {"savivaldybės", "mokyklų tipai", "mokyklos", "profesinės mokyklos"}   # ką siųsti
PAUZE_S = 0.5
NARSYKLE = {"User-Agent": "Mozilla/5.0 (VBE duomenu surinkimas svieslentei)"}

PDF_DIR, XLS_DIR = APLANKAS / "pdf", APLANKAS / "excel"
STULPELIAI = ["savivaldybės", "mokyklų tipai", "mokyklos", "profesinės mokyklos"]   # NŠA lentelės stulpeliai A–D


# ---------------- 1. NUORODOS ----------------
def _metai_virs(el) -> str:
    for t in el.find_all_previous(string=re.compile(r"\b20[12]\d\b")):
        if t.parent and t.parent.name in ("script", "style"):
            continue
        m = re.search(r"\b(20[12]\d)\b", t)
        if m:
            return m.group(1)
    return ""


def _tipas(a, href: str) -> str:
    v = Path(urlparse(href).path).name.lower()
    if re.search(r"prof", v):
        return "profesinės mokyklos"
    if re.search(r"skirtingo_tipo|grupes|_stm|rstm", v):
        return "mokyklų tipai"
    if re.search(r"sav", v):
        return "savivaldybės"
    if re.search(r"mok", v):
        return "mokyklos"
    td, tr = a.find_parent(["td", "th"]), a.find_parent("tr")
    if td is not None and tr is not None:          # pagal stulpelio vietą eilutėje (be pirmo – dalyko)
        celes = tr.find_all(["td", "th"])
        idx = celes.index(td) - 1
        if 0 <= idx < len(STULPELIAI):
            return STULPELIAI[idx]
    return "savivaldybės"


def surask_pdf() -> pd.DataFrame:
    r = requests.get(PUSLAPIS, headers=NARSYKLE, timeout=60)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    irasai, matyti = [], set()
    for a in soup.find_all("a", href=True):
        href = urljoin(PUSLAPIS, a["href"])
        if not href.lower().split("?")[0].endswith(".pdf") or href in matyti:   # D stulpelis kartais = C
            continue
        matyti.add(href)
        tr = a.find_parent("tr")
        dalykas = tr.find(["td", "th"]).get_text(" ", strip=True) if tr else a.get_text(" ", strip=True)
        irasai.append({"metai_puslapyje": _metai_virs(a), "dalykas": dalykas, "tipas": _tipas(a, href),
                       "url": href, "failas": Path(urlparse(href).path).name})
    df = pd.DataFrame(irasai)
    print(f"Rasta PDF nuorodų: {len(df)}")
    metai = pd.to_numeric(df["metai_puslapyje"], errors="coerce")
    return df[(metai <= PASKUTINIAI_PDF_METAI) & df["tipas"].isin(TIPAI)].reset_index(drop=True)


# ---------------- 2. ATSISIUNTIMAS ----------------
def atsisiusk(df: pd.DataFrame) -> pd.DataFrame:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    keliai = []
    for _, e in df.iterrows():
        trump = {"savivaldybės": "sav", "mokyklų tipai": "tip", "mokyklos": "mok", "profesinės mokyklos": "prof"}[e.tipas]
        kelias = PDF_DIR / f"{e.metai_puslapyje}_{trump}_{e.failas}"
        if not kelias.exists():
            try:
                r = requests.get(e.url, headers=NARSYKLE, timeout=120)
                r.raise_for_status()
                kelias.write_bytes(r.content)
                print(f"  ↓ {kelias.name}")
                time.sleep(PAUZE_S)
            except Exception as ex:
                print(f"  ✗ {kelias.name}: {ex}")
                kelias = None
        keliai.append(kelias)
    df = df.copy()
    df["pdf"] = keliai
    return df


# ---------------- 3. EILUČIŲ ATPAŽINIMAS ----------------
SKAICIUS = re.compile(r"^\d+(?:[.,]\d+)?%?$")


def atkoduok(tekstas: str) -> str:
    """Kai kuriuose PDF šriftas užkoduotas poslinkiu (pvz. „$NPHQơVU“ = „Akmenės r“).
    Atkoduojame ASCII raides (+29); lietuviškos raidės lieka neatkoduotos ir pažymimos „?“."""
    if not re.search(r"[$%&'()*+]|[A-Z]{3,}", tekstas) or re.search(r"[a-z]{3,}", tekstas):
        return tekstas
    rez = []
    for ch in tekstas:
        k = ord(ch)
        if 33 <= k <= 93:
            rez.append(chr(k + 29))
        elif ch == " ":
            rez.append(" ")
        else:
            rez.append("?")
    return "".join(rez)


def eilute_is_teksto(e: str) -> dict | None:
    """Iš teksto eilutės „Pavadinimas  laikė  išlaikė % 16-35 % 36-85 % 86-100 %“ ištraukia skaičius.
    Jei „laikė“ stulpelio eilutėje nėra (pvz. 2021 m.), jis apskaičiuojamas iš išlaikiusiųjų procento."""
    tok = e.split()
    sk = []
    while tok and SKAICIUS.match(tok[-1]):
        sk.insert(0, tok.pop())
    if len(sk) < 8:
        return None
    poros = sk[-8:]                                   # (# , %) × 4: 16–100, 16–35, 36–85, 86–100
    try:
        kiek = [int(poros[i]) for i in (0, 2, 4, 6)]
        proc = [float(poros[i].rstrip("%").replace(",", ".")) for i in (1, 3, 5, 7)]
    except ValueError:
        return None
    islaike, b1, b2, b3 = kiek
    if abs(islaike - (b1 + b2 + b3)) > 1:
        return None
    laike = None
    if len(sk) >= 9 and sk[-9].isdigit() and int(sk[-9]) >= islaike:
        laike = int(sk[-9])
    elif proc[0] > 0:
        laike = round(islaike / (proc[0] / 100))
    if not laike:
        return None
    pav = " ".join(tok).strip()
    return {"pavadinimas_pdf": pav, "pavadinimas": atkoduok(pav), "laike": laike, "islaike": islaike,
            "b16_35": b1, "b36_85": b2, "b86_100": b3}


def pazymek_sumas(eil: list[dict]) -> list[dict]:
    """Pažymi tarpines / bendras sumų eilutes (pvz. savivaldybių grupių 2021 m.), kad nebūtų sumuojamos du kartus:
    eilutė laikoma suma, jei jos skaičiai lygūs gretimų (prieš arba po) eilučių sumai."""
    laukai = ["laike", "islaike", "b16_35", "b36_85", "b86_100"]
    for e in eil:
        e["suma"] = False
    for i, e in enumerate(eil):
        for kryptis in (-1, 1):
            acc = dict.fromkeys(laukai, 0)
            j, n = i + kryptis, 0
            while 0 <= j < len(eil):
                if eil[j]["suma"]:
                    break
                for k in laukai:
                    acc[k] += eil[j][k]
                n += 1
                if n >= 2 and all(acc[k] == e[k] for k in laukai):
                    e["suma"] = True
                    break
                if acc["laike"] > e["laike"]:
                    break
                j += kryptis
            if e["suma"]:
                break
    return eil


def apdorok_pdf(pdf: Path) -> tuple[list[dict], str]:
    tekstas, lenteles = [], []
    with pdfplumber.open(pdf) as doc:
        for nr, psl in enumerate(doc.pages, 1):
            tekstas.append(psl.extract_text() or "")
            for t in psl.extract_tables():
                if t and len(t) > 1:
                    d = pd.DataFrame(t)
                    d.insert(0, "psl", nr)
                    lenteles.append(d)
    visas = "\n".join(tekstas)
    eil = [r for r in (eilute_is_teksto(x) for x in visas.splitlines()) if r]
    eil = pazymek_sumas(eil)
    XLS_DIR.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(XLS_DIR / (pdf.stem + ".xlsx")) as w:
        pd.DataFrame(eil or [{"pastaba": "eilučių neatpažinta"}]).to_excel(w, sheet_name="eilutes", index=False)
        if lenteles:
            pd.concat(lenteles, ignore_index=True).to_excel(w, sheet_name="lenteles", index=False)
    return eil, visas


def metai_pdf(tekstas: str) -> str:
    m = re.search(r"\b(20[12]\d)\s*m\.", tekstas[:2000])
    return m.group(1) if m else ""


# ---------------- 2025+ m. EXCEL (mokyklų vidurkiai) ----------------
def skaityk_mokyklu_vidurkius(kelias: Path) -> pd.DataFrame:
    """NŠA Excel „VBE vidurkiai pagal mokyklas“ → ilgas formatas: metai, mokykla, dalykas, vidurkis."""
    d = pd.read_excel(kelias, header=None)
    mm = next(str(v) for v in d.iloc[:3].values.ravel() if re.search(r"\d{4}-\d{4} m\. m\.", str(v)))
    metai = int(re.search(r"\d{4}-(\d{4})", mm).group(1))
    k = d.iloc[4:].copy()
    k.columns = ["mokyklos_tipas", "mokykla"] + d.iloc[3, 2:].tolist()
    k["mokyklos_tipas"] = k["mokyklos_tipas"].ffill()
    ilg = k.melt(id_vars=["mokyklos_tipas", "mokykla"], var_name="dalykas", value_name="vidurkis").dropna(subset=["vidurkis"])
    ilg.insert(0, "mokslo_metai", mm)
    ilg.insert(0, "metai", metai)
    return ilg


# ---------------- PAGRINDINĖ ----------------
def main():
    APLANKAS.mkdir(parents=True, exist_ok=True)
    failai = atsisiusk(surask_pdf())

    savivaldybes, salis, busenos = [], [], []
    for _, e in failai.iterrows():
        if e.pdf is None:
            busenos.append("neatsisiųsta")
            continue
        try:
            eil, tekstas = apdorok_pdf(e.pdf)
        except Exception as ex:
            busenos.append(f"klaida: {ex}")
            continue
        metai = metai_pdf(tekstas) or e.metai_puslapyje
        busena = f"atpažinta eilučių: {len(eil)}"
        if e.tipas == "savivaldybės" and eil:
            sav = [r for r in eil if not r["suma"]]
            sumu = len(eil) - len(sav)
            for r in sav:
                savivaldybes.append({"metai": metai, "dalykas": e.dalykas, "failas": e.pdf.name, **r})
            t = {k: sum(r[k] for r in sav) for k in ["laike", "islaike", "b16_35", "b36_85", "b86_100"]}
            salis.append({"metai": metai, "metai_puslapyje": e.metai_puslapyje, "dalykas": e.dalykas,
                          "savivaldybiu": len(sav), **t,
                          "islaike_proc": round(100 * t["islaike"] / t["laike"], 2),
                          "neislaike_proc": round(100 - 100 * t["islaike"] / t["laike"], 2),
                          "b86_100_proc": round(100 * t["b86_100"] / t["laike"], 2),
                          "failas": e.pdf.name})
            busena += f"; savivaldybių: {len(sav)}" + (f"; sumų eilučių praleista: {sumu}" if sumu else "")
            if not 55 <= len(sav) <= 61:
                busena += " ⚠ netikėtas savivaldybių skaičius – patikrinkite"
        elif not eil:
            busena = "eilučių neatpažinta (žr. Excel lapą „lenteles“)"
        busenos.append(busena)
        print(f"  ✓ {e.pdf.name}: {busena}")

    failai["busena"] = busenos
    failai["pdf"] = failai["pdf"].astype(str)
    salis_df = pd.DataFrame(salis)
    if not salis_df.empty:
        # 2010–2012 m. PDF kitokio formato – paliekame tik metus, kur atpažinta beveik visos savivaldybės
        salis_df["metai"] = pd.to_numeric(salis_df["metai"], errors="coerce")
        salis_df = salis_df[(salis_df["savivaldybiu"] >= 55) & (salis_df["metai"] >= 2013)]
        salis_df = salis_df.sort_values(["dalykas", "metai"])

    # Excel failai „VBE_vidurkiai_pagal_mokyklas*.xlsx“, padėti į tą patį aplanką (2025 m. ir vėlesni)
    excel = sorted(APLANKAS.glob("VBE_vidurkiai_pagal_mokyklas*.xlsx"))
    mokyklos = pd.concat([skaityk_mokyklu_vidurkius(f) for f in excel], ignore_index=True) if excel else pd.DataFrame()
    if not mokyklos.empty:
        mokyklos["vidurkis"] = mokyklos["vidurkis"].astype(float)
        mokyklos.to_csv(APLANKAS / "vbe_mokyklu_vidurkiai.csv", index=False)
        print(f"   Excel failų su mokyklų vidurkiais: {len(excel)} (metai: {sorted(mokyklos['metai'].unique())})")
    with pd.ExcelWriter(APLANKAS / "VBE_suvestine.xlsx") as w:
        salis_df.to_excel(w, sheet_name="Lietuva", index=False)
        pd.DataFrame(savivaldybes).to_excel(w, sheet_name="Savivaldybes", index=False)
        failai.to_excel(w, sheet_name="Failai", index=False)
        if not mokyklos.empty:
            (mokyklos.groupby(["metai", "mokslo_metai", "dalykas"])["vidurkis"]
             .agg(mokyklu="count", mokyklu_vidurkiu_mediana="median", mokyklu_vidurkiu_vidurkis="mean")
             .round(2).reset_index().to_excel(w, sheet_name="Vidurkiai_nuo_2025", index=False))
            mokyklos.to_excel(w, sheet_name="Mokyklu_vidurkiai_nuo_2025", index=False)
    if not salis_df.empty:
        salis_df.to_csv(APLANKAS / "vbe_salies_eilutes.csv", index=False)

    print(f"\n✅ Suvestinė: {APLANKAS / 'VBE_suvestine.xlsx'}")
    print(f"   Šalies eilučių (metai × dalykas): {len(salis_df)}")
    print("   Patikrinkite lapo „Failai“ stulpelį „busena“: ⚠ žymi failus, kuriuose savivaldybių skaičius neįprastas.")


if __name__ == "__main__":
    main()
