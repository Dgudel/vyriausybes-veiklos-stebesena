"""Sugeneruoja švieslentės svetainę į aplanką _site/.

    python generuoti.py              # iš duomenys/ aplanko failų
    ATNAUJINTI=1 python generuoti.py # prieš tai atsisiunčia naujausius duomenis iš data.gov.lt

Peržiūra kompiuteryje:  python -m http.server -d _site 8000  ->  http://localhost:8000
"""
import os

import pandas as pd
import shutil
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from rodikliai import (pasitenkinimas, savizudybes, regionai, atsinaujinanti_energija, oro_tarsa, skurdas, nelygybe, imigracija, migracijos_valdymas, senejimas, grizimas, nusikalstamumas, gynybos_islaidos, atlieku_perdirbimas, gyventojai, sesd_emisijos, zuvusieji_keliuose, bvp, infliacija, nasumas, nedarbas, skola, brandos_egzaminai, busto_ispirkamumas, energijos_kainos, issilavinimas, realusis_du,
                       sveikatos_eiles, sveikatos_rezultatai, svietimo_pasiekimai)
from rodikliai.bendra import slugas, papildomas_grafikas, sk, sparkline_svg, zmoniu_laikotarpis, palyginimo_tekstas

SAKNIS = Path(__file__).resolve().parent
ISVESTIS = SAKNIS / "_site"

# Sritys ir jų rodikliai. Kol srities rodikliai neparuošti, rodikliai = [].
# Sudedamosios dalys, rodomos tarp pagrindinių kortelių (tėvinio rodiklio id, dalies pavadinimo pradžia)
# (tėvinio rodiklio id, dalies pavadinimo pradžia, kortelės pavadinimas, trumpas aprašas)
ISKELTI = {
    4: [("atsinaujinanti-energija", "Energetinė priklausomybė", "Energetinė priklausomybė",
         "importuojama energijos poreikių dalis")],
    5: [("nusikalstamumas", "Sukčiavimas", "Sukčiavimas", "registruotų atvejų pokytis per metus"),
        ("nusikalstamumas", "Tyčiniai nužudymai", "Tyčiniai nužudymai", "100 tūkst. gyventojų"),
        ("migracijos-valdymas", "Prieglobsčio prašymai", "Prieglobsčio prašymai", "pirmų prašymų per mėnesį")],
    6: [("gyventoju-kaita", "Suminis gimstamumo", "Gimstamumas", "vaikų vienai moteriai"),
        ("emigracija-grizimas", "Išvyko", "Emigracija", "išvykusių Lietuvos piliečių per metus")],
}

SRITYS = [
    {"nr": 1, "trumpai": "Gyvenimo lygis", "pavadinimas": "Gyvenimo lygis ir sąlygos",
     "klausimas": "Ar žmonių materialinė gerovė gerėja?",
     "rodikliai": [realusis_du, busto_ispirkamumas, energijos_kainos, skurdas, nelygybe, pasitenkinimas]},
    {"nr": 2, "trumpai": "Paslaugos", "pavadinimas": "Viešosios paslaugos",
     "klausimas": "Ar piliečiai gauna geresnes viešąsias paslaugas?",
     "rodikliai": [sveikatos_eiles, sveikatos_rezultatai, svietimo_pasiekimai, brandos_egzaminai, issilavinimas, savizudybes]},
    {"nr": 3, "trumpai": "Ekonomika", "pavadinimas": "Ekonomika ir užimtumas",
     "klausimas": "Ar ekonomika kuria gerovę ir darbo vietas?",
     "rodikliai": [bvp, nedarbas, nasumas, infliacija, skola, regionai]},
    {"nr": 4, "trumpai": "Infrastruktūra", "pavadinimas": "Infrastruktūra ir aplinka",
     "klausimas": "Ar šalis gerina savo fizinę ir aplinkos infrastruktūrą?",
     "rodikliai": [zuvusieji_keliuose, sesd_emisijos, atlieku_perdirbimas, atsinaujinanti_energija, oro_tarsa]},
    {"nr": 5, "trumpai": "Saugumas", "pavadinimas": "Saugumas ir visuomenės valdymas",
     "klausimas": "Ar valstybė užtikrina saugumą ir veiksmingai valdo svarbiausius visuomenės iššūkius?",
     "rodikliai": [nusikalstamumas, migracijos_valdymas, gynybos_islaidos]},
    {"nr": 6, "trumpai": "Demografija", "pavadinimas": "Demografija ir migracija",
     "klausimas": "Ar šalies demografinė raida išlieka tvari ir ar valstybė geba valdyti gyventojų senėjimo bei migracijos iššūkius?",
     "rodikliai": [gyventojai, senejimas, grizimas, imigracija]},
]

BUSENOS = {
    "gereja":   {"zodis": "Gerėja",   "ikona": "▲"},
    "stabilu":  {"zodis": "Stabilu",  "ikona": "■"},
    "prasteja": {"zodis": "Prastėja", "ikona": "▼"},
    "info":     {"zodis": "Stebimas", "ikona": "◆"},
    "nera":     {"zodis": "Nėra duomenų", "ikona": "○"},
}


def rodikliu(n: int) -> str:
    """Skaičius su taisyklinga daugiskaita: 1 rodiklis, 3 rodikliai, 10 rodiklių, 21 rodiklis."""
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} rodiklis"
    if 2 <= n % 10 <= 9 and not 11 <= n % 100 <= 19:
        return f"{n} rodikliai"
    return f"{n} rodiklių"


def saugiai(modulis):
    """Apskaičiuoja rodiklį. Jei nepavyksta su naujai atsisiųstais duomenimis – bando su saugyklos failais;
    jei ir tai nepavyksta – rodiklis praleidžiamas, bet svetainė vis tiek sugeneruojama."""
    try:
        return modulis.rodiklis()
    except Exception as e:
        print(f"  ⚠ {modulis.__name__}: {type(e).__name__}: {e}")
    if os.environ.get("ATNAUJINTI") == "1":
        import subprocess
        from rodikliai import eurostat_duomenys
        subprocess.run(["git", "checkout", "--", "duomenys/"], cwd=SAKNIS, capture_output=True)
        os.environ["ATNAUJINTI"] = "0"
        eurostat_duomenys.lentele.cache_clear()
        try:
            r = modulis.rodiklis()
            print(f"  ↺ {modulis.__name__}: naudoti saugyklos duomenys")
            return r
        except Exception as e:
            print(f"  ⚠ {modulis.__name__} vis tiek nepavyko: {e}")
        finally:
            os.environ["ATNAUJINTI"] = "1"
            eurostat_duomenys.lentele.cache_clear()
    print(f"  ✗ {modulis.__name__} praleistas")
    return None


def main():
    if ISVESTIS.exists():
        shutil.rmtree(ISVESTIS)
    (ISVESTIS / "rodikliai").mkdir(parents=True)
    (ISVESTIS / "duomenys").mkdir()
    shutil.copytree(SAKNIS / "statika", ISVESTIS / "statika")

    env = Environment(loader=FileSystemLoader(SAKNIS / "sablonai"), autoescape=True)
    env.filters["sk"] = sk
    env.filters["laikotarpis"] = zmoniu_laikotarpis
    env.filters["rodikliu"] = rodikliu
    from plotly.offline import get_plotlyjs_version
    import hashlib
    css_versija = hashlib.md5((SAKNIS / "statika" / "stilius.css").read_bytes()).hexdigest()[:8]
    bendri = {"busenos": BUSENOS, "atnaujinta": date.today().strftime("%Y-%m-%d"), "css_versija": css_versija,
              "plotlyjs_versija": get_plotlyjs_version()}

    sritys = []
    for sritis in SRITYS:
        rodikliai = []
        for modulis in sritis["rodikliai"]:
            print(f"• {modulis.__name__}")
            r = saugiai(modulis)
            if r is None:
                continue
            if r.palyginimas is None:
                r.palyginimas = palyginimo_tekstas(r.laikotarpis)
            r.spark = sparkline_svg(r.sparkline, nuo_nulio=r.spark_nuo_nulio) if r.sparkline is not None else ""
            for x in r.dalys:
                x.id = f"{r.id}--{slugas(x.pavadinimas)}"
                x.tevas = r
                x.spark = sparkline_svg(x.serija, nuo_nulio=False) if x.serija is not None and len(x.serija) > 1 else ""
            r.grafiku_html = [f.to_html(full_html=False, include_plotlyjs=False,
                                        config={"displaylogo": False, "responsive": True,
                                                "toImageButtonOptions": {"format": "png", "scale": 2}})
                              for f in r.grafikai]
            if r.lentele is not None:
                r.lentele.round(2).to_csv(ISVESTIS / "duomenys" / f"{r.id}.csv", index=False, encoding="utf-8-sig")
            rodikliai.append(r)
        for r in rodikliai:
            r.visos_busenos = [r.busena] + [x.busena for x in r.dalys]
            r.nesutampa = [x for x in r.dalys if x.busena in ("gereja", "stabilu", "prasteja") and x.busena != r.busena]
        suvestine = {k: sum(b == k for r in rodikliai for b in r.visos_busenos) for k in BUSENOS}
        sritys.append({**sritis, "rodikliai": rodikliai, "suvestine": suvestine})

    bendri["meniu_sritys"] = sritys
    visi = [(s, r) for s in sritys for r in s["rodikliai"]]
    bendra = {k: sum(b == k for _, r in visi for b in r.visos_busenos) for k in BUSENOS}
    pagrindiniai = {k: sum(r.busena == k for _, r in visi) for k in BUSENOS}
    daliu_sk = sum(len([x for x in r.dalys if x.busena in ("gereja", "stabilu", "prasteja")]) for _, r in visi)
    vertinti = sum(bendra[k] for k in ("gereja", "stabilu", "prasteja"))

    for sritis in sritys:
        visos_dalys = [x for r in sritis["rodikliai"] for x in r.dalys if x.busena != "nera"]
        iskeltos = []
        for tevas, pradzia, pavadinimas, aprasas in ISKELTI.get(sritis["nr"], []):
            x = next((d for d in visos_dalys if d.tevas.id == tevas and d.pavadinimas.startswith(pradzia)), None)
            if x is None:
                print(f"  ⚠ iškelti nepavyko: {tevas} / {pradzia}")
                continue
            x.pavadinimas, x.trumpas_aprasas = pavadinimas, aprasas
            x.nesutampa = []
            iskeltos.append(x)
        for r in sritis["rodikliai"]:          # iškeltos dalys turi savo kortelę – tėvo kortelėje jų nekartojame
            r.nesutampa = [d for d in r.nesutampa if d not in iskeltos]
        sritis["pagrindines"] = list(sritis["rodikliai"]) + iskeltos
        sritis["kitos"] = [x for x in visos_dalys if x not in iskeltos]
        for x in sritis["kitos"]:
            s = x.serija.dropna() if x.serija is not None else None
            if s is not None and len(s) > 1:
                if len(s) > 40 and (s.index[-1] - s.index[0]).days > 365 * 15:
                    s = s[s.index >= s.index[-1] - pd.DateOffset(years=15)]
                vnt = " %" if x.vienetai.strip() == "%" else x.vienetai
                f = papildomas_grafikas(x.pavadinimas, f"Lietuva · rodiklio „{x.tevas.pavadinimas}“ sudedamoji dalis",
                                        "Šaltiniai – žr. pagrindinį rodiklį", [("Lietuva", s)], vnt=vnt, dec=x.dec,
                                        nuo_nulio=False, zenklas=x.zenklas)
                x.grafiko_html = f.to_html(full_html=False, include_plotlyjs=False, config={"displaylogo": False,
                                           "responsive": True, "locale": "lt"})
                x.lentele_eil = [(d, v) for d, v in zip(s.index, s.values)][::-1][:12]
            else:
                x.grafiko_html, x.lentele_eil = "", []
            (ISVESTIS / "rodikliai" / f"{x.id}.html").write_text(
                env.get_template("dalis.html").render(x=x, r=x.tevas, sritis=sritis, **bendri), encoding="utf-8")
    (ISVESTIS / "index.html").write_text(
        env.get_template("index.html").render(sritys=sritys, bendra=bendra, vertinti=vertinti,
                                              pagrindiniai=pagrindiniai, daliu_sk=daliu_sk,
                                              is_viso=len(visi),
                                              pagr_sk=sum(len(s["pagrindines"]) for s in sritys),
                                              kitu_sk=sum(len(s["kitos"]) for s in sritys), **bendri), encoding="utf-8")
    (ISVESTIS / "metodika.html").write_text(
        env.get_template("metodika.html").render(sritys=sritys, **bendri), encoding="utf-8")
    for i, (sritis, r) in enumerate(visi):
        ankstesnis = visi[i - 1][1] if i > 0 else None
        kitas = visi[i + 1][1] if i + 1 < len(visi) else None
        (ISVESTIS / "rodikliai" / f"{r.id}.html").write_text(
            env.get_template("rodiklis.html").render(r=r, sritis=sritis, ankstesnis=ankstesnis, kitas=kitas,
                                                     **bendri), encoding="utf-8")
    (ISVESTIS / ".nojekyll").touch()   # GitHub Pages: neapdoroti per Jekyll
    print(f"✅ Svetainė sugeneruota: {ISVESTIS}")


if __name__ == "__main__":
    main()
