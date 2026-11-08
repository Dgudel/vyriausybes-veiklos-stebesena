"""1.3 Energijos kainos ir pragyvenimo išlaidų spaudimas."""
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, palyginimo_tekstas, ivertink, linijos, sk, stilius, zmoniu_laikotarpis
from .saltiniai import du_serija, kainu_pokytis, laikotarpis_is_datos

SLENKSTIS = 1.0     # ±1 proc. punktas tarp energijos kainų ir atlyginimų augimo – stabilu


def rodiklis() -> Rodiklis:
    energija = kainu_pokytis("Energija")
    bendros = kainu_pokytis("Iš viso, išskyrus tabaką")
    neto = du_serija("Neto")

    pask = energija.iloc[-1]
    laik = laikotarpis_is_datos(energija.index[-1])

    # Vertinimas: ar energija brangsta greičiau nei auga atlyginimai (paskutinis bendras mėnuo)
    bendras = energija.index.intersection(neto.index).max()
    skirtumas = energija[bendras] - neto[bendras]          # >0 – spaudimas didėja
    busena = ivertink(skirtumas, "mazesne", SLENKSTIS)
    bl = zmoniu_laikotarpis(laikotarpis_is_datos(bendras), kada=True)

    f = go.Figure()
    nuo = neto.index.min()
    linijos(f, [("Energijos kainos", energija[energija.index >= nuo], SERIJOS[1]),
                ("Visos vartojimo kainos (išskyrus tabaką)", bendros[bendros.index >= nuo], SERIJOS[3]),
                ("Neto darbo užmokestis", neto, SERIJOS[0])])
    stilius(f, "Energijos kainos, visos kainos ir atlyginimai",
            "Metinis pokytis, %: palyginti su praėjusių metų tuo pačiu mėnesiu",
            "Šaltinis: Valstybės duomenų agentūra, rodikliai S7R329 ir S10R027")

    lentele = (energija.rename("energijos_kainu_metinis_pokytis_proc").to_frame()
               .join(bendros.rename("visu_kainu_metinis_pokytis_proc"))
               .join(neto.rename("neto_du_metinis_pokytis_proc")).reset_index())
    lentele["laikotarpis"] = lentele["data"].map(laikotarpis_is_datos)

    kryptis = "greičiau" if skirtumas > 0 else "lėčiau"
    return Rodiklis(
        id="energijos-kainos",
        pavadinimas="Energijos kainos",
        trumpas_aprasas="per metus",
        reiksme=pask, laikotarpis=laik, busena=busena,
        palyginimas=f"vertinta pagal {bl}, {palyginimo_tekstas(laikotarpis_is_datos(bendras))}",
        vertinimo_taisykle=("Vertinama, ar energija brangsta greičiau nei auga neto atlyginimai. "
                            f"Gerėja, kai energijos kainos auga daugiau nei {sk(SLENKSTIS, False)} proc. punkto lėčiau už atlyginimus; "
                            f"prastėja, kai daugiau nei {sk(SLENKSTIS, False)} proc. punkto greičiau; kitu atveju – stabilu."),
        vertinimo_paaiskinimas=(f"{bl} energijos kainos per metus pakito {sk(energija[bendras])} %, "
                                f"o neto atlyginimai – {sk(neto[bendras])} %. Energija brango {kryptis} "
                                f"nei augo atlyginimai (skirtumas {sk(skirtumas)} proc. punkto)."),
        sparkline=energija[energija.index >= nuo],
        grafikai=[f],
        apibrezimas=("Energijos kainų metinis pokytis pagal vartojimo kainų indeksą (specialioji grupė „Energija“: "
                     "elektra, dujos, šiluma, kitas kuras ir degalai). Lyginama su visų kainų ir neto atlyginimų augimu."),
        pastabos=[
            "Kainų duomenys pateikiami kaip lygio indeksas (2025 m. = 100); metinis pokytis apskaičiuotas lyginant su tuo pačiu mėnesiu prieš 12 mėn.",
            "Kainų duomenys skelbiami anksčiau nei darbo užmokesčio, todėl vertinimui naudojamas paskutinis mėnuo, už kurį yra abu.",
            "Dokumente siūloma papildyti apklausos rodikliu – gyventojų, negalinčių tinkamai šildyti būsto, dalimi (metinis).",
        ],
        saltiniai=[("Oficialiosios statistikos portalas – kainos", "https://osp.stat.gov.lt/"),
                   ("Lietuvos atvirų duomenų portalas", "https://data.gov.lt/")],
        papildomai=[(f"{sk(bendros.iloc[-1])} %", f"visų vartojimo kainų (išskyrus tabaką) metinis pokytis, "
                                                   f"{zmoniu_laikotarpis(laikotarpis_is_datos(bendros.index[-1]))}")],
        lentele=lentele[["laikotarpis", "energijos_kainu_metinis_pokytis_proc",
                         "visu_kainu_metinis_pokytis_proc", "neto_du_metinis_pokytis_proc"]],
    )
