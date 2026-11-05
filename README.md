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

Svetainė perkuriama kiekvieną kartą įkėlus pakeitimus, kas mėnesį 25 d. ir rankiniu būdu (Actions → Run workflow).

## Kaip pridėti naują rodiklį

1. Įdėkite duomenų failą į `duomenys/`.
2. Nukopijuokite `rodikliai/realusis_du.py` nauju pavadinimu ir pakeiskite:
   duomenų skaitymą, reikšmę, **vertinimo taisyklę** (`ivertink(reiksme, "didesne"/"mazesne", slenkstis)`),
   grafikus, apibrėžimą, šaltinius.
3. `generuoti.py` sąraše `SRITYS` įrašykite modulį į reikiamą sritį.

Kiekvienas rodiklis – atskiras failas, todėl kolegos gali dirbti lygiagrečiai.

## Automatinis duomenų atnaujinimas

`rodikliai/saltiniai.py` įrašykite data.gov.lt modelio kelią (pvz. `DU_MODELIS = "datasets/gov/lsd/..."`).
Tada GitHub Actions prieš generuodamas atsisiųs naujausius duomenis iš `get.data.gov.lt`.
Kol kelias nenurodytas, naudojamas failas iš `duomenys/` – jį atnaujinkite rankiniu būdu.
Patikrinkite, kad data.gov.lt CSV stulpelių pavadinimai sutampa su dabartinio failo stulpeliais.

## Vertinimo taisyklės

| Rodiklis | Gerėja | Prastėja | Stabilu |
|---|---|---|---|
| Realusis DU | metinis pokytis > +0,5 % | < −0,5 % | tarp jų |
| Būsto įperkamumas | būstas brangsta > 1 p. p. lėčiau nei auga neto DU (ketvirčiais) | > 1 p. p. greičiau | tarp jų |
| Energijos kainos | energija brangsta > 1 p. p. lėčiau nei auga neto DU | > 1 p. p. greičiau | tarp jų |

Taisyklės rodomos ir kiekvieno rodiklio puslapyje. Jas verta suderinti su darbo grupe.
