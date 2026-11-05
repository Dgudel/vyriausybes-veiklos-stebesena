"""1.1 Realusis darbo užmokestis."""
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, ivertink, linijos, sk, stilius, zmoniu_laikotarpis
from .saltiniai import SEKTORIAI, du_serija, kainu_pokytis, laikotarpis_is_datos

SALTINIS = "Šaltinis: Valstybės duomenų agentūra, rodiklis S10R027"
SLENKSTIS = 0.5          # ±0,5 proc. punkto laikoma stabiliu


def rodiklis() -> Rodiklis:
    real = du_serija("Realusis")
    neto = du_serija("Neto")
    pask = real.iloc[-1]
    laik = laikotarpis_is_datos(real.index[-1])
    busena = ivertink(pask, "didesne", SLENKSTIS)

    # Sukauptas pokytis nuo seniausio turimo to paties mėnesio (grandinė per 12 mėn. žingsnius)
    datos = [d for d in real.index if d.month == real.index[-1].month]
    kaupt = 1.0
    for d in datos:
        kaupt *= 1 + real[d] / 100
    bazes_metai = datos[0].year - 1

    # 1 grafikas – pagal sektorių
    f1 = go.Figure()
    linijos(f1, [(v, du_serija("Realusis", v), SERIJOS[i]) for i, v in enumerate(SEKTORIAI.values())])
    stilius(f1, "Realusis darbo užmokestis pagal sektorių",
            "Metinis pokytis, %: palyginti su praėjusių metų tuo pačiu mėnesiu", SALTINIS)

    # 2 grafikas – neto DU ir kainos
    kainos = kainu_pokytis("Iš viso, išskyrus tabaką")
    kainos = kainos[(kainos.index >= neto.index.min()) & (kainos.index <= neto.index.max())]
    f2 = go.Figure()
    f2.add_trace(go.Scatter(x=kainos.index, y=kainos.values, mode="lines", line=dict(width=0),
                            hoverinfo="skip", showlegend=False))
    f2.add_trace(go.Scatter(x=neto.index, y=neto.values, mode="lines", line=dict(width=0),
                            fill="tonexty", fillcolor="rgba(42,120,214,0.10)", hoverinfo="skip",
                            name="Perkamosios galios pokytis"))
    linijos(f2, [("Neto darbo užmokestis", neto, SERIJOS[0]),
                 ("Vartojimo kainos (iš viso, išskyrus tabaką)", kainos, SERIJOS[1])])
    stilius(f2, "Atlyginimai ir kainos",
            "Abu rodikliai – metinis pokytis, %: palyginti su praėjusių metų tuo pačiu mėnesiu",
            "Šaltinis: Valstybės duomenų agentūra, rodikliai S10R027 ir S7R329")

    lentele = (real.rename("realusis_du_metinis_pokytis_proc").to_frame()
               .join(neto.rename("neto_du_metinis_pokytis_proc")).reset_index())
    lentele["laikotarpis"] = lentele["data"].map(laikotarpis_is_datos)

    return Rodiklis(
        id="realusis-darbo-uzmokestis",
        pavadinimas="Realusis darbo užmokestis",
        trumpas_aprasas="per metus, šalies ūkyje",
        reiksme=pask, laikotarpis=laik, busena=busena,
        vertinimo_taisykle=(f"Gerėja, kai realusis darbo užmokestis per metus padidėja daugiau nei "
                            f"{sk(SLENKSTIS, False)} %; prastėja, kai sumažėja daugiau nei {sk(SLENKSTIS, False)} %; "
                            f"kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{zmoniu_laikotarpis(laik, kada=True)} realusis darbo užmokestis buvo {sk(pask, zenklas=False)} % "
                                f"didesnis nei prieš metus: neto atlyginimas augo {sk(neto.iloc[-1], zenklas=False)} %, "
                                f"t. y. greičiau už kainas, todėl perkamoji galia didėjo."
                                if pask > 0 else
                                f"{zmoniu_laikotarpis(laik, kada=True)} realusis darbo užmokestis buvo {sk(abs(pask), zenklas=False)} % "
                                f"mažesnis nei prieš metus: kainos augo greičiau už atlyginimus."),
        sparkline=real,
        grafikai=[f1, f2],
        apibrezimas=("Realusis darbo užmokestis – neto (atskaičius mokesčius) vidutinis darbo užmokestis, "
                     "įvertinus vartojimo kainų pokytį. Rodo, kaip keičiasi atlyginimo perkamoji galia. "
                     "Šalies ūkis – be individualiųjų įmonių."),
        pastabos=[
            "Duomenys pateikiami kaip indeksas (praėjusių metų tas pats mėnuo = 100); švieslentėje rodomas pokytis = indeksas − 100.",
            "Paskutinių mėnesių duomenys gali būti patikslinti (pažymėti „patikslinti ir perskaičiuoti duomenys“).",
            "Grafike „Atlyginimai ir kainos“ naudojama kainų grupė „Iš viso, išskyrus tabaką“, nes pateiktoje lentelėje nėra bendro VKI; "
            "todėl tarpas tarp linijų gali šiek tiek skirtis nuo realiojo DU pokyčio.",
        ],
        saltiniai=[("Oficialiosios statistikos portalas – darbo užmokestis", "https://osp.stat.gov.lt/"),
                   ("Lietuvos atvirų duomenų portalas", "https://data.gov.lt/")],
        papildomai=[(f"{sk((kaupt - 1) * 100)} %",
                     f"realusis DU {zmoniu_laikotarpis(laik, kada=True)}, palyginti su {bazes_metai} m. tuo pačiu mėnesiu")],
        lentele=lentele[["laikotarpis", "realusis_du_metinis_pokytis_proc", "neto_du_metinis_pokytis_proc"]],
    )
