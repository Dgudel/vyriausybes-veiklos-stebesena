# Vyriausybės veiklos stebėsenos švieslentė (prototipas)

Statinė svetainė: pagrindinis puslapis su 6 sritimis ir rodiklių kortelėmis, kiekvienam rodikliui –
atskiras puslapis su grafikais, vertinimu (gerėja / stabilu / prastėja), apibrėžimu, šaltiniais ir CSV.
Svetainę sugeneruoja Python, o GitHub Pages ją nemokamai paskelbia.

## Struktūra

```
generuoti.py              # surenka rodiklius ir sugeneruoja svetainę į _site/
rodikliai/
  bendra.py               # bendros priemonės: duomenų skaitymas, vertinimas, grafikų stilius
  saltiniai.py            # duomenų rinkiniai, naudojami kelių rodiklių
  realusis_du.py          # 1 rodiklis = 1 failas
  energijos_kainos.py
  busto_ispirkamumas.py
  eurostat_duomenys.py    # Eurostat lentelių skaitymas ir automatinis atnaujinimas
  sveikatos_eiles.py
  sveikatos_rezultatai.py
  svietimo_pasiekimai.py  # PUPP (NŠA) ir PISA (Eurostat)
  issilavinimas.py        # anksti mokslus palikę, aukštasis išsilavinimas (Eurostat)
  brandos_egzaminai.py    # VBE (NŠA)
  bvp.py, nedarbas.py, nasumas.py, infliacija.py, skola.py   # 3 sritis (Eurostat; infliacija – ir ECB)
irankiai/pupp_rezultatai.py  # NŠA PUPP PDF → duomenys/pupp_salies_eilutes.csv (paleisti kartą per metus)
irankiai/vbe_rezultatai.py   # NŠA VBE PDF + Excel → duomenys/vbe_salies_eilutes.csv, vbe_mokyklu_vidurkiai.csv
sablonai/                 # HTML šablonai (Jinja)
statika/stilius.css       # išvaizda
duomenys/                 # duomenų failai (xlsx / csv)
.github/workflows/        # automatinis generavimas ir paskelbimas
```

## Paleidimas savo kompiuteryje

```bash
pip install -r requirements.txt
python generuoti.py
python -m http.server -d _site 8000     # atidarykite http://localhost:8000
```

## Paskelbimas GitHub Pages (vieną kartą)

1. GitHub'e sukurkite **viešą** repozitoriją (geriausia – institucijos organizacijos paskyroje).
2. Įkelkite visus šio aplanko failus (išskyrus `_site/`).
3. Repozitorijoje: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. **Actions** skiltyje pamatysite „Švieslentės atnaujinimas“ – po 1–2 min. svetainė bus adresu
   `https://<paskyra>.github.io/<repozitorija>/`.

Svetainė perkuriama kiekvieną kartą įkėlus pakeitimus, kasdien ir rankiniu būdu (Actions → Run workflow).

## Kaip pridėti naują rodiklį

1. Įdėkite duomenų failą į `duomenys/`.
2. Nukopijuokite `rodikliai/realusis_du.py` nauju pavadinimu ir pakeiskite:
   duomenų skaitymą, reikšmę, **vertinimo taisyklę** (`ivertink(reiksme, "didesne"/"mazesne", slenkstis)`),
   grafikus, apibrėžimą, šaltinius.
3. `generuoti.py` sąraše `SRITYS` įrašykite modulį į reikiamą sritį.

Kiekvienas rodiklis – atskiras failas, todėl kolegos gali dirbti lygiagrečiai.

## Automatinis duomenų atnaujinimas

GitHub Actions svetainę perkuria **kasdien** (5:00 UTC) ir prieš tai atsisiunčia naujausius duomenis:

- **Lietuvos duomenų portalas** (`api.dataportal.gov.lt`): S10R027, S7R329, S7R334. Lentelių pavadinimai –
  `rodikliai/saltiniai.py`. Naujai lentelei pavadinimą rasite rinkinio puslapyje: Eksportuoti → API endpoint.
- **Eurostat** (paketas `eurostat`): `hlth_silc_08`, `hlth_cd_apr`, `demo_mlexpec`, `hlth_silc_01`,
  `sdg_04_10`, `sdg_04_20`, `sdg_04_40`, `namq_10_gdp`, `nama_10_pc`, `une_rt_m`, `lfsi_emp_q`,
  `nama_10_lp_ulc`, `prc_hicp_manr`, `gov_10q_ggdebt`.
- **ECB duomenų portalas** (`data-api.ecb.europa.eu`): SVKI metinis pokytis (Lietuva ir euro zona) – nuo 2026 m.,
  nes Eurostat lentelė `prc_hicp_manr` pasibaigė 2025 m. gruodžio duomenimis.
- **NŠA PUPP rezultatai** skelbiami tik PDF, todėl atnaujinami rankiniu būdu kartą per metus (rugpjūtį–rugsėjį):
  paleiskite `python irankiai/pupp_rezultatai.py` ir nukopijuokite sukurtą `pupp_salies_eilutes.csv` į `duomenys/`.
- **NŠA VBE rezultatai**: 2013–2024 m. – PDF (`irankiai/vbe_rezultatai.py`), nuo 2025 m. – NŠA Excel „VBE vidurkiai
  pagal mokyklas“. Naujus Excel failus padėkite į VBE aplanką, paleiskite skriptą ir nukopijuokite
  `vbe_mokyklu_vidurkiai.csv` į `duomenys/`.

Jei šaltinis nepasiekiamas, naudojami failai iš `duomenys/`. Savo kompiuteryje su naujausiais duomenimis:

```bash
ATNAUJINTI=1 python generuoti.py
```

## Vertinimo taisyklės

| Rodiklis | Gerėja | Prastėja | Stabilu |
|---|---|---|---|
| Realusis DU | metinis pokytis > +0,5 % | < −0,5 % | tarp jų |
| Būsto įperkamumas | būstas brangsta > 1 p. p. lėčiau nei auga neto DU (ketvirčiais) | > 1 p. p. greičiau | tarp jų |
| Energijos kainos | energija brangsta > 1 p. p. lėčiau nei auga neto DU | > 1 p. p. greičiau | tarp jų |
| Negavo gydymo dėl laukimo eilių | dalis per metus sumažėja > 0,3 p. p. | padidėja > 0,3 p. p. | tarp jų |
| Išvengiamas mirtingumas dėl gydymo | rodiklis per metus sumažėja > 2 % | padidėja > 2 % | tarp jų |
| Matematikos pasiekimai (PUPP) | nepasiekusių patenkinamo lygio dalis sumažėja > 2 p. p. | padidėja > 2 p. p. | tarp jų |
| Matematikos VBE išlaikymas | išlaikiusiųjų dalis padidėja > 2 p. p. | sumažėja > 2 p. p. | tarp jų |
| Realus BVP augimas | metinis augimas ≥ 1 % | BVP mažėja | 0–1 % |
| Nedarbo lygis | per metus sumažėja > 0,3 p. p. | padidėja > 0,3 p. p. | tarp jų |
| Darbo našumas | realus pokytis > +0,5 % | < −0,5 % | tarp jų |
| Infliacija | priartėja prie 2 % tikslo > 0,5 p. p. (palyginti su prieš metus) | nutolsta > 0,5 p. p. | tarp jų |
| Valdžios skola | santykis su BVP per metus sumažėja > 1 p. p. | padidėja > 1 p. p. | tarp jų |
| Anksti mokslus palikę jaunuoliai | dalis sumažėja > 0,5 p. p. | padidėja > 0,5 p. p. | tarp jų |

Taisyklės rodomos ir kiekvieno rodiklio puslapyje. Jas verta suderinti su darbo grupe.
