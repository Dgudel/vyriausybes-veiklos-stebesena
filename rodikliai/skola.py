"""3.5 Valdžios sektoriaus skola (Eurostat gov_10q_ggdebt)."""
import pandas as pd

from .bendra import Rodiklis, ivertink, sk, zmoniu_laikotarpis
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

    g = grafikas([("Lietuva", lt), ("ES-27", es)], "Valdžios sektoriaus skola",
                 "Konsoliduota bendroji skola, % BVP; punktyras – 60 % riba", "Šaltinis: Eurostat, gov_10q_ggdebt",
                 nuo="2008-01-01", nulio_linija=False)
    g.add_hline(y=RIBA, line=dict(color="#52514e", width=1, dash="dot"))

    lentele = (lt.rename("LT_skola_proc_BVP").to_frame().join(es.rename("ES27_skola_proc_BVP"))
               .join(mln.rename("LT_skola_mln_EUR")))
    lentele = lentele[lentele.index >= "2008-01-01"]
    lentele.insert(0, "laikotarpis", [laikotarpis(d, "Q") for d in lentele.index])

    kryptis = "padidėjo" if pokytis > 0 else "sumažėjo"
    return Rodiklis(
        id="valdzios-skola", pavadinimas="Valdžios sektoriaus skola",
        trumpas_aprasas="BVP", reiksme=pask, vienetai="%", laikotarpis=laik, busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Lyginama su tuo pačiu ketvirčiu prieš metus. Gerėja, kai skolos ir BVP santykis sumažėja "
                            f"daugiau nei {sk(SLENKSTIS, False)} proc. punkto; prastėja, kai padidėja daugiau nei "
                            f"{sk(SLENKSTIS, False)} proc. punkto; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{zmoniu_laikotarpis(laik)} pabaigoje valdžios sektoriaus skola sudarė {sk(pask, False)} % BVP "
                                f"(prieš metus – {sk(pries, False)} %; {kryptis} {sk(abs(pokytis), False)} proc. punkto). "
                                f"Tai {sk(mln.iloc[-1] / 1000, False)} mlrd. Eur; ES vidurkis – {sk(es.iloc[-1], False)} % BVP."),
        sparkline=lt[lt.index >= "2015-01-01"], grafikai=[g],
        apibrezimas=("Valdžios sektoriaus (centrinės ir vietos valdžios bei socialinės apsaugos fondų) konsoliduota "
                     "bendroji skola (Mastrichto apibrėžtis), santykis su BVP. Centrinės valdžios skola nėra viso "
                     "valdžios sektoriaus skola."),
        pastabos=["Ketvirtinis santykis su BVP skaičiuojamas pagal paskutinių keturių ketvirčių BVP.",
                  "Skolos padidėjimas ne visada reiškia blogėjimą (pvz. finansuojant gynybą ar investicijas), todėl "
                  "vertinimą reikia skaityti kartu su BVP augimu."],
        saltiniai=[("Eurostat – gov_10q_ggdebt", "https://ec.europa.eu/eurostat/databrowser/view/gov_10q_ggdebt/default/table?lang=en"),
                   ("OSP – valdžios sektoriaus finansai", "https://osp.stat.gov.lt/")],
        papildomai=[(f"{sk(mln.iloc[-1] / 1000, False)} mlrd. Eur", f"skolos suma, {zmoniu_laikotarpis(laik)}")],
        lentele=lentele,
    )
