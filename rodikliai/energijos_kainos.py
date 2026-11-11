"""1.3 Energijos kainos ir pragyvenimo išlaidų spaudimas."""
import plotly.graph_objects as go

from .bendra import SERIJOS, Rodiklis, palyginimo_tekstas, ivertink, linijos, sk, stilius, zmoniu_laikotarpis, t
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
    linijos(f, [(t("Energijos kainos", "Energy prices"), energija[energija.index >= nuo], SERIJOS[1]),
                (t("Visos vartojimo kainos (išskyrus tabaką)", "All consumer prices (excl. tobacco)"),
                 bendros[bendros.index >= nuo], SERIJOS[3]),
                (t("Neto darbo užmokestis", "Net wages"), neto, SERIJOS[0])])
    stilius(f, t("Energijos kainos, visos kainos ir atlyginimai", "Energy prices, all prices and wages"),
            t("Metinis pokytis, %: palyginti su praėjusių metų tuo pačiu mėnesiu",
              "Annual change, %: compared with the same month of the previous year"),
            t("Šaltinis: Valstybės duomenų agentūra, rodikliai S7R329 ir S10R027",
              "Source: State Data Agency of Lithuania, indicators S7R329 and S10R027"))

    lentele = (energija.rename("energijos_kainu_metinis_pokytis_proc").to_frame()
               .join(bendros.rename("visu_kainu_metinis_pokytis_proc"))
               .join(neto.rename("neto_du_metinis_pokytis_proc")).reset_index())
    lentele["laikotarpis"] = lentele["data"].map(laikotarpis_is_datos)

    kryptis = t("greičiau", "faster") if skirtumas > 0 else t("lėčiau", "more slowly")
    return Rodiklis(
        id="energijos-kainos",
        pavadinimas=t("Energijos kainos", "Energy prices"),
        trumpas_aprasas=t("per metus", "year on year"),
        reiksme=pask, laikotarpis=laik, busena=busena,
        palyginimas=t(f"vertinta pagal {bl}, {palyginimo_tekstas(laikotarpis_is_datos(bendras))}",
                      f"assessed for {bl}, {palyginimo_tekstas(laikotarpis_is_datos(bendras))}"),
        vertinimo_taisykle=t("Vertinama, ar energija brangsta greičiau nei auga neto atlyginimai. "
                             f"Gerėja, kai energijos kainos auga daugiau nei {sk(SLENKSTIS, False)} proc. punkto lėčiau už atlyginimus; "
                             f"prastėja, kai daugiau nei {sk(SLENKSTIS, False)} proc. punkto greičiau; kitu atveju – stabilu.",
                             "Assesses whether energy is becoming more expensive faster than net wages are rising. "
                             f"Improving when energy prices grow more than {sk(SLENKSTIS, False)} percentage point slower "
                             f"than wages; worsening when more than {sk(SLENKSTIS, False)} percentage point faster; "
                             f"otherwise stable."),
        vertinimo_paaiskinimas=t(f"{bl} energijos kainos per metus pakito {sk(energija[bendras])} %, "
                                 f"o neto atlyginimai – {sk(neto[bendras])} %. Energija brango {kryptis} "
                                 f"nei augo atlyginimai (skirtumas {sk(skirtumas)} proc. punkto).",
                                 f"In {bl}, energy prices changed by {sk(energija[bendras])}% year on year and net "
                                 f"wages by {sk(neto[bendras])}%. Energy became more expensive {kryptis} than wages "
                                 f"grew (gap of {sk(skirtumas)} percentage points)."),
        sparkline=energija[energija.index >= nuo],
        grafikai=[f],
        apibrezimas=t("Energijos kainų metinis pokytis pagal vartojimo kainų indeksą (specialioji grupė „Energija“: "
                      "elektra, dujos, šiluma, kitas kuras ir degalai). Lyginama su visų kainų ir neto atlyginimų augimu.",
                      "Annual change in energy prices according to the consumer price index (special group “Energy”: "
                      "electricity, gas, heat, other fuels and motor fuels). Compared with growth in all prices and "
                      "net wages."),
        pastabos=[
            t("Kainų duomenys pateikiami kaip lygio indeksas (2025 m. = 100); metinis pokytis apskaičiuotas lyginant su tuo pačiu mėnesiu prieš 12 mėn.",
              "Price data are a level index (2025 = 100); the annual change is calculated against the same month 12 months earlier."),
            t("Kainų duomenys skelbiami anksčiau nei darbo užmokesčio, todėl vertinimui naudojamas paskutinis mėnuo, už kurį yra abu.",
              "Price data are published earlier than wage data, so the assessment uses the latest month for which both are available."),
            t("Dokumente siūloma papildyti apklausos rodikliu – gyventojų, negalinčių tinkamai šildyti būsto, dalimi (metinis).",
              "It is proposed to add a survey indicator – the share of people unable to keep their home adequately warm (annual)."),
        ],
        saltiniai=[(t("Oficialiosios statistikos portalas – kainos", "Official Statistics Portal – prices"), "https://osp.stat.gov.lt/"),
                   (t("Lietuvos atvirų duomenų portalas", "Lithuanian Open Data Portal"), "https://data.gov.lt/")],
        papildomai=[(f"{sk(bendros.iloc[-1])} %", t(f"visų vartojimo kainų (išskyrus tabaką) metinis pokytis, "
                                                    f"{zmoniu_laikotarpis(laikotarpis_is_datos(bendros.index[-1]))}",
                                                    f"annual change in all consumer prices (excl. tobacco), "
                                                    f"{zmoniu_laikotarpis(laikotarpis_is_datos(bendros.index[-1]))}"))],
        lentele=lentele[["laikotarpis", "energijos_kainu_metinis_pokytis_proc",
                         "visu_kainu_metinis_pokytis_proc", "neto_du_metinis_pokytis_proc"]],
    )
