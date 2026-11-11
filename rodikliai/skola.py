"""3.5 Valdžios sektoriaus skola (Eurostat gov_10q_ggdebt)."""
import pandas as pd

from .bendra import dalis, papildomas_grafikas, Rodiklis, ivertink, sk, zmoniu_laikotarpis, t
from .ekonomika_bendra import grafikas
from .eurostat_duomenys import laikotarpis, serija

SLENKSTIS = 1.0     # proc. punkto per metus
RIBA = 60.0         # Mastrichto kriterijus, % BVP


def rodiklis() -> Rodiklis:
    f = dict(na_item="GD", sector="S13", unit="PC_GDP")
    lt, es = serija("gov_10q_ggdebt", "LT", **f), serija("gov_10q_ggdebt", "EU27_2020", **f)
    mln = serija("gov_10q_ggdebt", "LT", na_item="GD", sector="S13", unit="MIO_EUR")

    pask, data = lt.iloc[-1], lt.index[-1]
    pries = lt.get(data - pd.DateOffset(years=1))
    pokytis = pask - pries
    busena = ivertink(pokytis, "mazesne", SLENKSTIS)
    laik = laikotarpis(data, "Q")

    g = grafikas([("Lietuva", lt), ("ES-27", es)], t("Valdžios sektoriaus skola", "General government debt"),
                 t("Konsoliduota bendroji skola, % BVP; punktyras – 60 % riba", "Consolidated gross debt, % of GDP; dotted line – 60% limit"), "Šaltinis: Eurostat, gov_10q_ggdebt",
                 nuo="2008-01-01", nulio_linija=False)
    g.add_hline(y=RIBA, line=dict(color="#52514e", width=1, dash="dot"))

    lentele = (lt.rename("LT_skola_proc_BVP").to_frame().join(es.rename("ES27_skola_proc_BVP"))
               .join(mln.rename("LT_skola_mln_EUR")))
    lentele = lentele[lentele.index >= "2008-01-01"]
    lentele.insert(0, "laikotarpis", [laikotarpis(d, "Q") for d in lentele.index])

    kryptis = t("padidėjo", "up") if pokytis > 0 else t("sumažėjo", "down")
    _dalys = []
    _def_q = serija("gov_10q_ggnfa", "LT", na_item="B9", sector="S13", unit="PC_GDP", s_adj="NSA")
    deficitas = _def_q.rolling(4).mean().dropna()          # paskutinių 4 ketvirčių vidurkis
    _dalys.append(dalis(t("Valdžios sektoriaus balansas (4 ketv. vidurkis), % BVP", "General government balance (4-quarter average), % of GDP"),
                        deficitas, "didesne", 0.3,
                        zenklas=True))
    _r = Rodiklis(
        dalys=_dalys,
        id="valdzios-skola", pavadinimas=t("Valdžios sektoriaus skola", "General government debt"),
        trumpas_aprasas=t("BVP", "of GDP"), reiksme=pask, vienetai="%", laikotarpis=laik, busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=t(f"Lyginama su tuo pačiu ketvirčiu prieš metus. Gerėja, kai skolos ir BVP santykis sumažėja "
                             f"daugiau nei {sk(SLENKSTIS, False)} proc. punkto; prastėja, kai padidėja daugiau nei "
                             f"{sk(SLENKSTIS, False)} proc. punkto; kitu atveju – stabilu.",
                             f"Compared with the same quarter a year earlier. Improving when the debt-to-GDP ratio falls "
                             f"by more than {sk(SLENKSTIS, False)} percentage point; worsening when it rises by more than "
                             f"{sk(SLENKSTIS, False)} percentage point; otherwise stable."),
        vertinimo_paaiskinimas=t(f"{zmoniu_laikotarpis(laik)} pabaigoje valdžios sektoriaus skola sudarė {sk(pask, False)} % BVP "
                                 f"(prieš metus – {sk(pries, False)} %; {kryptis} {sk(abs(pokytis), False)} proc. punkto). "
                                 f"Tai {sk(mln.iloc[-1] / 1000, False)} mlrd. Eur; ES vidurkis – {sk(es.iloc[-1], False)} % BVP.",
                                 f"At the end of {zmoniu_laikotarpis(laik)}, general government debt was {sk(pask, False)}% "
                                 f"of GDP (a year earlier: {sk(pries, False)}%; {kryptis} {sk(abs(pokytis), False)} "
                                 f"percentage points). This is EUR {sk(mln.iloc[-1] / 1000, False)} billion; the EU average "
                                 f"is {sk(es.iloc[-1], False)}% of GDP."),
        sparkline=lt[lt.index >= "2015-01-01"], grafikai=[g],
        apibrezimas=t("Valdžios sektoriaus (centrinės ir vietos valdžios bei socialinės apsaugos fondų) konsoliduota "
                      "bendroji skola (Mastrichto apibrėžtis), santykis su BVP. Centrinės valdžios skola nėra viso "
                      "valdžios sektoriaus skola.",
                      "Consolidated gross debt of the general government (central and local government and social "
                      "security funds; Maastricht definition) as a ratio to GDP. Central government debt is not the "
                      "debt of the whole general government."),
        pastabos=[t("Ketvirtinis santykis su BVP skaičiuojamas pagal paskutinių keturių ketvirčių BVP.",
                    "The quarterly ratio to GDP is based on GDP over the last four quarters."),
                  t("Skolos padidėjimas ne visada reiškia blogėjimą (pvz. finansuojant gynybą ar investicijas), todėl "
                    "vertinimą reikia skaityti kartu su BVP augimu.",
                    "Rising debt does not always mean deterioration (e.g. when financing defence or investment), so the "
                    "assessment should be read together with GDP growth.")],
        saltiniai=[("Eurostat – gov_10q_ggdebt", "https://ec.europa.eu/eurostat/databrowser/view/gov_10q_ggdebt/default/table?lang=en"),
                   (t("OSP – valdžios sektoriaus finansai", "Official Statistics Portal – government finance"), "https://osp.stat.gov.lt/")],
        papildomai=[(t(f"{sk(mln.iloc[-1] / 1000, False)} mlrd. Eur", f"EUR {sk(mln.iloc[-1] / 1000, False)} bn"),
                     t(f"skolos suma, {zmoniu_laikotarpis(laik)}", f"amount of debt, {zmoniu_laikotarpis(laik)}"))],
        lentele=lentele,
    )
    _r.grafikai.append(papildomas_grafikas(
        t("Valdžios sektoriaus balansas (deficitas / perteklius)", "General government balance (deficit / surplus)"),
        t("% BVP, paskutinių 4 ketvirčių vidurkis (Mastrichto riba – −3 %)", "% of GDP, average of the last 4 quarters (Maastricht limit – −3%)"), "Šaltinis: Eurostat, gov_10q_ggnfa",
        [("Lietuva", deficitas)], vnt=" %", nuo="2010-01-01", nuo_nulio=False, zenklas=True))
    return _r
