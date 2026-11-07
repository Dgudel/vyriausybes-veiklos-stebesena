"""4. Žiedinė ekonomika: perdirbamų komunalinių atliekų dalis."""
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, ivertink, linijos, sk, stilius
from .eurostat_duomenys import serija

SLENKSTIS = 1.0     # proc. punkto


def rodiklis() -> Rodiklis:
    lt, es = serija("sdg_11_60", "LT", unit="PC"), serija("sdg_11_60", "EU27_2020", unit="PC")
    pask, pries = lt.iloc[-1], lt.iloc[-2]
    metai, ankst = lt.index[-1].year, lt.index[-2].year
    pokytis = pask - pries
    busena = ivertink(pokytis, "didesne", SLENKSTIS)

    nuo = "2005-01-01"
    f1 = go.Figure()
    linijos(f1, [("Lietuva", lt[lt.index >= nuo], SERIJOS[0]), ("ES-27", es[es.index >= nuo], SERIJOS[1])],
            zenklas=False, zymekliai=True)
    f1.add_hline(y=55, line=dict(color=SERIJOS[2], width=1, dash="dash"),
                 annotation_text="ES tikslas 2025 m. – 55 %", annotation_position="top left")
    stilius(f1, "Perdirbamų komunalinių atliekų dalis", "Perdirbta ir kompostuota, % visų komunalinių atliekų",
            "Šaltinis: Eurostat, sdg_11_60", nulio_linija=False, metiniai=True)
    f1.update_yaxes(rangemode="tozero")

    lentele = lt.rename("LT_proc").to_frame().join(es.rename("ES27_proc"))
    lentele = lentele[lentele.index >= nuo]
    lentele.insert(0, "metai", lentele.index.year)

    kryptis = "padidėjo" if pokytis > 0 else "sumažėjo"
    return Rodiklis(
        id="atlieku-perdirbimas",
        pavadinimas="Komunalinių atliekų perdirbimas",
        trumpas_aprasas="perdirbama atliekų dalis",
        reiksme=pask, vienetai="%", laikotarpis=str(metai), busena=busena,
        zenklas=False, spark_nuo_nulio=True,
        vertinimo_taisykle=(f"Gerėja, kai dalis per metus padidėja daugiau nei {sk(SLENKSTIS, False, 0)} proc. punktu; "
                            f"prastėja, kai sumažėja daugiau nei {sk(SLENKSTIS, False, 0)} proc. punktu; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{metai} m. perdirbta {sk(pask, False)} % komunalinių atliekų ({ankst} m. – "
                                f"{sk(pries, False)} %). Dalis {kryptis} {sk(abs(pokytis), False)} proc. punkto; "
                                f"ES vidurkis – {sk(es.iloc[-1], False)} %."),
        sparkline=lt[lt.index >= nuo],
        grafikai=[f1],
        apibrezimas=("Perdirbtų (įskaitant kompostavimą ir anaerobinį apdorojimą) komunalinių atliekų dalis nuo "
                     "visų susidariusių komunalinių atliekų. ES Atliekų pagrindų direktyva nustato tikslus: "
                     "55 % iki 2025 m., 60 % iki 2030 m., 65 % iki 2035 m."),
        pastabos=["Nuo 2020 m. ES taiko griežtesnę perdirbimo skaičiavimo metodiką, todėl ankstesni metai nėra "
                  "visiškai palyginami."],
        saltiniai=[("Eurostat – sdg_11_60", "https://ec.europa.eu/eurostat/databrowser/view/sdg_11_60/default/table?lang=en")],
        papildomai=[(f"{sk(55 - pask, False)} p. p.", "iki ES 2025 m. tikslo (55 %)")] if pask < 55 else [],
        lentele=lentele,
    )
