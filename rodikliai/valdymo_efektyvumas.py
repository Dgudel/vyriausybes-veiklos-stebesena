"""7. Valstybės valdymo kokybė: Pasaulio banko valdymo rodikliai (WGI) – valdymo efektyvumas ir teisės viršenybė.

Duomenys – duomenys/wgi_lt.csv (stulpeliai: rodiklis, metai, reiksme). GitHub Actions (ATNAUJINTI=1) atsisiunčia juos
iš Pasaulio banko API; jei nepavyksta ir failo nėra – rodiklis praleidžiamas."""
import os

import pandas as pd
import plotly.graph_objects as go

from .bendra import DUOMENYS, SERIJOS, Rodiklis, dalis, ivertink, linijos, sk, stilius, t

FAILAS = DUOMENYS / "wgi_lt.csv"
RODIKLIAI = {"GE.EST": "valdymo_efektyvumas", "RL.EST": "teises_virsenybe"}
SLENKSTIS = 0.1     # WGI įverčio vienetai (skalė maždaug nuo −2,5 iki 2,5)


def _atsisiusk():
    import requests
    eil = []
    for kodas in RODIKLIAI:
        for param in ({"source": "3"}, {}):
            r = requests.get(f"https://api.worldbank.org/v2/country/LTU/indicator/{kodas}",
                             params={"format": "json", "per_page": "200", **param}, timeout=120)
            r.raise_for_status()
            j = r.json()
            if len(j) > 1 and j[1]:
                eil += [{"rodiklis": kodas, "metai": int(x["date"]), "reiksme": x["value"]} for x in j[1]
                        if x.get("value") is not None]
                break
    if not eil:
        raise ValueError("WGI: tuščias atsakymas")
    pd.DataFrame(eil).sort_values(["rodiklis", "metai"]).to_csv(FAILAS, index=False)
    print(f"  ↓ WGI: {len(eil)} eilučių")


def _serija(kodas: str) -> pd.Series:
    d = pd.read_csv(FAILAS)
    d = d[d.rodiklis == kodas].sort_values("metai")
    return pd.Series(d.reiksme.values, index=[pd.Timestamp(int(m), 1, 1) for m in d.metai]).dropna()


def rodiklis() -> Rodiklis:
    if os.environ.get("ATNAUJINTI") == "1":
        try:
            _atsisiusk()
        except Exception as e:
            print(f"  ⚠ WGI neatsisiųsta ({e}); naudojamas esamas failas")
    ge, rl = _serija("GE.EST"), _serija("RL.EST")
    pask, pries = ge.iloc[-1], ge.iloc[-2]
    metai, ankst = ge.index[-1].year, ge.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    f1 = go.Figure()
    linijos(f1, [(t("Valdymo efektyvumas", "Government effectiveness"), ge, SERIJOS[0]),
                 (t("Teisės viršenybė", "Rule of law"), rl, SERIJOS[1])], vnt="", zenklas=True, dec=2, zymekliai=True)
    stilius(f1, t("Pasaulio banko valdymo rodikliai (WGI)", "Worldwide Governance Indicators (WGI)"),
            t("Įvertis: nuo maždaug −2,5 (silpnas) iki 2,5 (stiprus)", "Estimate: from about −2.5 (weak) to 2.5 (strong)"),
            t("Šaltinis: Pasaulio bankas, WGI", "Source: World Bank, WGI"), vnt="", nulio_linija=True, metiniai=True)

    lentele = ge.rename("valdymo_efektyvumas").to_frame().join(rl.rename("teises_virsenybe"), how="outer").round(3)
    lentele.insert(0, "metai", lentele.index.year)
    kryptis = t("padidėjo", "rose by") if pokytis > 0 else t("sumažėjo", "fell by")
    return Rodiklis(
        dalys=[dalis(t("Teisės viršenybė (WGI)", "Rule of law (WGI)"), rl, "didesne", SLENKSTIS, vienetai="", dec=2,
                     zenklas=True)],
        id="valdymo-efektyvumas",
        pavadinimas=t("Valdymo efektyvumas (WGI)", "Government effectiveness (WGI)"),
        trumpas_aprasas=t("Pasaulio banko įvertis (−2,5…2,5)", "World Bank estimate (−2.5…2.5)"),
        reiksme=pask, vienetai="", laikotarpis=str(metai), busena=busena, dec=2,
        zenklas=True, spark_nuo_nulio=False,
        vertinimo_taisykle=t(f"Gerėja, kai įvertis per metus padidėja daugiau nei {sk(SLENKSTIS, False)}; prastėja, kai "
                             f"tiek pat sumažėja; kitu atveju – stabilu.",
                             f"Improving when the estimate rises by more than {sk(SLENKSTIS, False)} in a year; worsening "
                             f"when it falls by as much; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{metai} m. Lietuvos valdymo efektyvumo įvertis – {sk(pask, True, 2)} "
                                 f"({ankst} m. – {sk(pries, True, 2)}); jis {kryptis} {sk(abs(pokytis), False, 2)}. "
                                 f"Teisės viršenybės įvertis – {sk(rl.iloc[-1], True, 2)}.",
                                 f"In {metai}, Lithuania's government effectiveness estimate was {sk(pask, True, 2)} "
                                 f"({ankst}: {sk(pries, True, 2)}); it {kryptis} {sk(abs(pokytis), False, 2)}. "
                                 f"The rule of law estimate was {sk(rl.iloc[-1], True, 2)}."),
        sparkline=ge,
        grafikai=[f1],
        apibrezimas=t("Valdymo efektyvumas apibendrina viešųjų paslaugų ir valstybės tarnybos kokybės, politikos "
                      "formavimo ir įgyvendinimo bei Vyriausybės įsipareigojimų patikimumo vertinimus. Teisės viršenybė – "
                      "pasitikėjimą taisyklėmis ir jų laikymąsi, sutarčių vykdymą, nuosavybės teises, policiją ir teismus.",
                      "Government effectiveness captures perceptions of the quality of public services and the civil "
                      "service, policy formulation and implementation, and the credibility of the government's "
                      "commitments. Rule of law captures confidence in and abidance by the rules of society, contract "
                      "enforcement, property rights, the police and the courts."),
        pastabos=[t("WGI įverčiai turi paklaidos ribas, todėl nedideli metiniai pokyčiai gali būti statistiškai nereikšmingi.",
                    "WGI estimates have margins of error, so small year-on-year changes may not be statistically significant.")],
        saltiniai=[(t("Pasaulio bankas – Worldwide Governance Indicators", "World Bank – Worldwide Governance Indicators"),
                    "https://www.worldbank.org/en/publication/worldwide-governance-indicators")],
        lentele=lentele,
    )
