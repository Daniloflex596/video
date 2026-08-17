# Video Luxury 4K verticali (9:16) — senza watermark

Strumento per scaricare **centinaia di video luxury in formato verticale 9:16**
(TikTok, Reels, Shorts) per una pagina motivazionale.

I video vengono da **Pexels** e **Pixabay**: sono **senza watermark** e con
**licenza gratuita che permette l'uso commerciale**, quindi puoi usarli nei
tuoi montaggi senza problemi legali. Niente siti pirata, niente watermark da
rimuovere.

## Come si usa (5 minuti)

1. **Prendi una chiave API gratuita di Pexels** (bastano 2 minuti):
   vai su <https://www.pexels.com/api/>, registrati e copia la chiave.
   Facoltativo: anche una chiave Pixabay da <https://pixabay.com/api/docs/>
   per trovare ancora più video.

2. **Installa Python** (se non lo hai già): <https://www.python.org/downloads/>
   Poi installa l'unica dipendenza:

   ```bash
   pip install requests
   ```

3. **Lancia lo script** dalla cartella `luxury-4k-9x16`:

   ```bash
   python3 scarica_video.py --pexels-key LA_TUA_CHIAVE --totale 300
   ```

   I video finiscono nella sottocartella `video/`, già pronti in 9:16.

## Consiglio importante sul 4K

I veri video **4K verticali** (2160×3840) esistono ma non sono tantissimi.
Se lo script ne trova pochi, rilancia accettando anche il Full HD verticale
(1080×1920), che su TikTok/Reels è indistinguibile dal 4K dopo la
compressione dell'app:

```bash
python3 scarica_video.py --pexels-key LA_TUA_CHIAVE --totale 300 --min-altezza 1920
```

## Salvarli direttamente su Google Drive

Se vuoi che i video finiscano su Google Drive, installa
[Google Drive per Desktop](https://www.google.com/drive/download/) e punta lo
script alla cartella sincronizzata: i video verranno caricati su Drive
automaticamente man mano che vengono scaricati.

Esempio su Windows:

```bash
python scarica_video.py --pexels-key LA_TUA_CHIAVE --cartella "G:\Il mio Drive\video-luxury"
```

Esempio su Mac:

```bash
python3 scarica_video.py --pexels-key LA_TUA_CHIAVE --cartella "$HOME/Google Drive/Il mio Drive/video-luxury"
```

## Altre opzioni

| Opzione | Effetto |
|---|---|
| `--totale 500` | quanti video scaricare (default 300) |
| `--min-altezza 1920` | accetta anche Full HD verticale (default 2160 = 4K) |
| `--pixabay-key CHIAVE` | aggiunge Pixabay come seconda fonte |
| `--cartella PERCORSO` | dove salvare i video (default: `./video`) |
| `--solo-lista` | non scarica: crea solo `manifest.csv` con tutti i link |

- **`temi.txt`** — la lista dei temi di ricerca (auto, yacht, jet privati,
  orologi, ville, soldi, palestra, skyline…). Modificala come vuoi.
- **`manifest.csv`** — creato a ogni esecuzione: elenco dei video con
  risoluzione, autore, link alla pagina originale e link di download.
- Se interrompi lo script, puoi rilanciarlo: i video già scaricati vengono
  saltati automaticamente.

## Spazio su disco

Centinaia di video in alta risoluzione occupano **decine di GB**: assicurati
di avere spazio libero. Per questo i video restano sul tuo computer e non
vengono caricati su GitHub (la cartella `video/` è esclusa dal repository).

## Nota sulla licenza

Le licenze Pexels e Pixabay permettono uso commerciale senza attribuzione
obbligatoria, ma non permettono di rivendere i video così come sono.
Per i dettagli: <https://www.pexels.com/license/> e
<https://pixabay.com/service/license-summary/>.
