"""1.2 Būsto įperkamumas / būsto statyba – duomenys dar neprijungti.

Kai turėsite duomenis: įdėkite failą į duomenys/, apskaičiuokite reikšmę ir būseną
taip pat kaip realusis_du.py, ir užpildykite reiksme, laikotarpis, busena, grafikai.
"""
from .bendra import Rodiklis


def rodiklis() -> Rodiklis:
    return Rodiklis(
        id="busto-ispirkamumas",
        pavadinimas="Būsto įperkamumas",
        trumpas_aprasas="duomenys rengiami",
        busena="nera",
        vertinimo_taisykle="Bus nustatyta, kai bus pasirinktas rodiklis.",
        apibrezimas=("Siūlomi variantai: disponuojamųjų pajamų dalis, skirta būstui išlaikyti (OSP); "
                     "pernelyg didelių būsto išlaidų našta (Eurostat ilc_lvho07a); baigti statyti gyvenamieji pastatai (OSP)."),
        pastabos=["Būsto išlaidų našta parodo gyvenimo būste finansinę naštą, o ne būsto pirkimo įperkamumą. "
                  "Pirkimo įperkamumui reikia atskirai apibrėžti kainų, pajamų ir paskolos įmokos santykį."],
        saltiniai=[("Eurostat – ilc_lvho07a", "https://ec.europa.eu/eurostat/databrowser/view/ilc_lvho07a/default/table"),
                   ("Oficialiosios statistikos portalas", "https://osp.stat.gov.lt/")],
    )
