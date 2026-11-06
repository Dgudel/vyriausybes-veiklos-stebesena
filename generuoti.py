"""Sugeneruoja švieslentės svetainę į aplanką _site/.

    python generuoti.py              # iš duomenys/ aplanko failų
    ATNAUJINTI=1 python generuoti.py # prieš tai atsisiunčia naujausius duomenis iš data.gov.lt

Peržiūra kompiuteryje:  python -m http.server -d _site 8000  ->  http://localhost:8000
"""
import shutil
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from rodikliai import (busto_ispirkamumas, energijos_kainos, issilavinimas, realusis_du,
                       sveikatos_eiles, sveikatos_rezultatai, svietimo_pasiekimai)
from rodikliai.bendra import sk, sparkline_svg, zmoniu_laikotarpis

SAKNIS = Path(__file__).resolve().parent
ISVESTIS = SAKNIS / "_site"

# Sritys ir jų rodikliai. Kol srities rodikliai neparuošti, rodikliai = [].
SRITYS = [
    {"nr": 1, "pavadinimas": "Gyvenimo lygis ir sąlygos",
     "klausimas": "Ar žmonių materialinė gerovė gerėja?",
     "rodikliai": [realusis_du, busto_ispirkamumas, energijos_kainos]},
    {"nr": 2, "pavadinimas": "Viešosios paslaugos",
     "klausimas": "Ar piliečiai gauna geresnes viešąsias paslaugas?",
     "rodikliai": [sveikatos_eiles, sveikatos_rezultatai, svietimo_pasiekimai, issilavinimas]},
    {"nr": 3, "pavadinimas": "Ekonomika ir užimtumas",
     "klausimas": "Ar ekonomika kuria gerovę ir darbo vietas?", "rodikliai": []},
    {"nr": 4, "pavadinimas": "Infrastruktūra ir aplinka",
     "klausimas": "Ar šalis gerina savo fizinę ir aplinkos infrastruktūrą?", "rodikliai": []},
    {"nr": 5, "pavadinimas": "Saugumas ir visuomenės valdymas",
     "klausimas": "Ar valstybė užtikrina saugumą ir veiksmingai valdo svarbiausius visuomenės iššūkius?",
     "rodikliai": []},
    {"nr": 6, "pavadinimas": "Demografija ir migracija",
     "klausimas": "Ar šalies demografinė raida išlieka tvari?", "rodikliai": []},
]

BUSENOS = {
    "gereja":   {"zodis": "Gerėja",   "ikona": "▲"},
    "stabilu":  {"zodis": "Stabilu",  "ikona": "■"},
    "prasteja": {"zodis": "Prastėja", "ikona": "▼"},
    "nera":     {"zodis": "Nėra duomenų", "ikona": "○"},
}


def main():
    if ISVESTIS.exists():
        shutil.rmtree(ISVESTIS)
    (ISVESTIS / "rodikliai").mkdir(parents=True)
    (ISVESTIS / "duomenys").mkdir()
    shutil.copytree(SAKNIS / "statika", ISVESTIS / "statika")

    env = Environment(loader=FileSystemLoader(SAKNIS / "sablonai"), autoescape=True)
    env.filters["sk"] = sk
    env.filters["laikotarpis"] = zmoniu_laikotarpis
    from plotly.offline import get_plotlyjs_version
    bendri = {"busenos": BUSENOS, "atnaujinta": date.today().strftime("%Y-%m-%d"),
              "plotlyjs_versija": get_plotlyjs_version()}

    sritys = []
    for sritis in SRITYS:
        rodikliai = []
        for modulis in sritis["rodikliai"]:
            print(f"• {modulis.__name__}")
            r = modulis.rodiklis()
            r.spark = sparkline_svg(r.sparkline, nuo_nulio=r.spark_nuo_nulio) if r.sparkline is not None else ""
            r.grafiku_html = [f.to_html(full_html=False, include_plotlyjs=False,
                                        config={"displaylogo": False, "responsive": True,
                                                "toImageButtonOptions": {"format": "png", "scale": 2}})
                              for f in r.grafikai]
            if r.lentele is not None:
                r.lentele.round(2).to_csv(ISVESTIS / "duomenys" / f"{r.id}.csv", index=False, encoding="utf-8-sig")
            rodikliai.append(r)
        suvestine = {k: sum(r.busena == k for r in rodikliai) for k in BUSENOS}
        sritys.append({**sritis, "rodikliai": rodikliai, "suvestine": suvestine})

    (ISVESTIS / "index.html").write_text(
        env.get_template("index.html").render(sritys=sritys, **bendri), encoding="utf-8")
    for sritis in sritys:
        for r in sritis["rodikliai"]:
            (ISVESTIS / "rodikliai" / f"{r.id}.html").write_text(
                env.get_template("rodiklis.html").render(r=r, sritis=sritis, **bendri), encoding="utf-8")
    (ISVESTIS / ".nojekyll").touch()   # GitHub Pages: neapdoroti per Jekyll
    print(f"✅ Svetainė sugeneruota: {ISVESTIS}")


if __name__ == "__main__":
    main()
