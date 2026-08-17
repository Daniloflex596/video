#!/usr/bin/env python3
"""Scarica video luxury verticali (9:16) in alta risoluzione, senza watermark.

Fonti: Pexels e Pixabay — video gratuiti, senza watermark, con licenza che
permette l'uso commerciale (es. pagine motivazionali su TikTok/Reels/Shorts).

Uso:
    python3 scarica_video.py --pexels-key LA_TUA_CHIAVE [--pixabay-key CHIAVE]
                             [--totale 300] [--min-altezza 2160]

Le chiavi API sono gratuite:
  - Pexels:  https://www.pexels.com/api/
  - Pixabay: https://pixabay.com/api/docs/
"""

import argparse
import csv
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Manca il modulo 'requests'. Installa con: pip install requests")

CARTELLA_SCRIPT = Path(__file__).resolve().parent
CARTELLA_VIDEO = CARTELLA_SCRIPT / "video"
FILE_TEMI = CARTELLA_SCRIPT / "temi.txt"
FILE_MANIFEST = CARTELLA_SCRIPT / "manifest.csv"

PEXELS_URL = "https://api.pexels.com/videos/search"
PIXABAY_URL = "https://pixabay.com/api/videos/"


def leggi_temi() -> list[str]:
    if not FILE_TEMI.exists():
        sys.exit(f"File dei temi non trovato: {FILE_TEMI}")
    temi = []
    for riga in FILE_TEMI.read_text(encoding="utf-8").splitlines():
        riga = riga.strip()
        if riga and not riga.startswith("#"):
            temi.append(riga)
    return temi


def e_verticale_916(larghezza: int, altezza: int) -> bool:
    """Accetta solo video verticali con proporzioni vicine a 9:16."""
    if larghezza <= 0 or altezza <= 0 or altezza <= larghezza:
        return False
    rapporto = larghezza / altezza
    return abs(rapporto - 9 / 16) < 0.03


def cerca_pexels(sessione: requests.Session, chiave: str, tema: str,
                 min_altezza: int, per_pagina: int = 80, max_pagine: int = 5):
    """Genera candidati (id, url_download, larghezza, altezza, autore, pagina)."""
    for pagina in range(1, max_pagine + 1):
        try:
            risposta = sessione.get(
                PEXELS_URL,
                headers={"Authorization": chiave},
                params={
                    "query": tema,
                    "orientation": "portrait",
                    "size": "large",
                    "per_page": per_pagina,
                    "page": pagina,
                },
                timeout=30,
            )
        except requests.RequestException as errore:
            print(f"  [Pexels] errore di rete su '{tema}': {errore}")
            return
        if risposta.status_code == 401:
            sys.exit("Chiave API Pexels non valida (errore 401).")
        if risposta.status_code == 429:
            print("  [Pexels] limite di richieste raggiunto, attendo 30s...")
            time.sleep(30)
            continue
        if risposta.status_code != 200:
            print(f"  [Pexels] risposta {risposta.status_code} su '{tema}'")
            return
        dati = risposta.json()
        for video in dati.get("videos", []):
            migliore = None
            for file_video in video.get("video_files", []):
                l = file_video.get("width") or 0
                a = file_video.get("height") or 0
                if not e_verticale_916(l, a) or a < min_altezza:
                    continue
                if migliore is None or a > (migliore.get("height") or 0):
                    migliore = file_video
            if migliore:
                yield {
                    "fonte": "pexels",
                    "id": f"pexels-{video['id']}",
                    "url": migliore["link"],
                    "larghezza": migliore["width"],
                    "altezza": migliore["height"],
                    "autore": (video.get("user") or {}).get("name", ""),
                    "pagina_web": video.get("url", ""),
                    "tema": tema,
                }
        if not dati.get("next_page"):
            return


def cerca_pixabay(sessione: requests.Session, chiave: str, tema: str,
                  min_altezza: int, per_pagina: int = 100, max_pagine: int = 3):
    for pagina in range(1, max_pagine + 1):
        try:
            risposta = sessione.get(
                PIXABAY_URL,
                params={
                    "key": chiave,
                    "q": tema,
                    "per_page": per_pagina,
                    "page": pagina,
                    "safesearch": "true",
                },
                timeout=30,
            )
        except requests.RequestException as errore:
            print(f"  [Pixabay] errore di rete su '{tema}': {errore}")
            return
        if risposta.status_code == 429:
            print("  [Pixabay] limite di richieste raggiunto, attendo 30s...")
            time.sleep(30)
            continue
        if risposta.status_code != 200:
            print(f"  [Pixabay] risposta {risposta.status_code} su '{tema}'")
            return
        dati = risposta.json()
        trovati = dati.get("hits", [])
        for video in trovati:
            varianti = video.get("videos", {})
            migliore = None
            for variante in varianti.values():
                l = variante.get("width") or 0
                a = variante.get("height") or 0
                if not e_verticale_916(l, a) or a < min_altezza:
                    continue
                if migliore is None or a > (migliore.get("height") or 0):
                    migliore = variante
            if migliore:
                yield {
                    "fonte": "pixabay",
                    "id": f"pixabay-{video['id']}",
                    "url": migliore["url"],
                    "larghezza": migliore["width"],
                    "altezza": migliore["height"],
                    "autore": video.get("user", ""),
                    "pagina_web": video.get("pageURL", ""),
                    "tema": tema,
                }
        if not trovati:
            return


def scarica_file(sessione: requests.Session, candidato: dict) -> Path | None:
    nome_file = f"{candidato['id']}.mp4"
    destinazione = CARTELLA_VIDEO / nome_file
    if destinazione.exists() and destinazione.stat().st_size > 0:
        print(f"  già presente: {nome_file}")
        return destinazione
    temporaneo = destinazione.with_suffix(".parziale")
    try:
        with sessione.get(candidato["url"], stream=True, timeout=120) as risposta:
            if risposta.status_code != 200:
                print(f"  download fallito ({risposta.status_code}): {nome_file}")
                return None
            with open(temporaneo, "wb") as f:
                for blocco in risposta.iter_content(chunk_size=1024 * 1024):
                    f.write(blocco)
        temporaneo.rename(destinazione)
    except (requests.RequestException, OSError) as errore:
        print(f"  download fallito: {nome_file} ({errore})")
        temporaneo.unlink(missing_ok=True)
        return None
    dimensione_mb = destinazione.stat().st_size / (1024 * 1024)
    print(f"  scaricato: {nome_file} "
          f"({candidato['larghezza']}x{candidato['altezza']}, {dimensione_mb:.0f} MB)")
    return destinazione


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scarica video luxury 9:16 senza watermark da Pexels/Pixabay.")
    parser.add_argument("--pexels-key",
                        default=os.environ.get("PEXELS_API_KEY", ""),
                        help="Chiave API Pexels (o variabile PEXELS_API_KEY)")
    parser.add_argument("--pixabay-key",
                        default=os.environ.get("PIXABAY_API_KEY", ""),
                        help="Chiave API Pixabay, opzionale (o PIXABAY_API_KEY)")
    parser.add_argument("--totale", type=int, default=300,
                        help="Quanti video scaricare in totale (default: 300)")
    parser.add_argument("--min-altezza", type=int, default=2160,
                        help="Altezza minima in pixel. 2160 = 4K verticale "
                             "(default). Usa 1920 per accettare anche Full HD "
                             "e trovare molti più video.")
    parser.add_argument("--solo-lista", action="store_true",
                        help="Non scaricare: crea solo manifest.csv con i link")
    argomenti = parser.parse_args()

    if not argomenti.pexels_key and not argomenti.pixabay_key:
        sys.exit("Serve almeno una chiave API.\n"
                 "  Pexels (consigliata, gratuita): https://www.pexels.com/api/\n"
                 "  Pixabay (gratuita):             https://pixabay.com/api/docs/\n"
                 "Poi: python3 scarica_video.py --pexels-key LA_TUA_CHIAVE")

    CARTELLA_VIDEO.mkdir(exist_ok=True)
    temi = leggi_temi()
    sessione = requests.Session()

    print(f"Obiettivo: {argomenti.totale} video verticali 9:16 "
          f"(altezza minima {argomenti.min_altezza}px)")
    print(f"Temi di ricerca: {len(temi)}")

    visti: set[str] = set()
    scelti: list[dict] = []
    for tema in temi:
        if len(scelti) >= argomenti.totale:
            break
        print(f"\nCerco: {tema}")
        generatori = []
        if argomenti.pexels_key:
            generatori.append(cerca_pexels(
                sessione, argomenti.pexels_key, tema, argomenti.min_altezza))
        if argomenti.pixabay_key:
            generatori.append(cerca_pixabay(
                sessione, argomenti.pixabay_key, tema, argomenti.min_altezza))
        nuovi = 0
        for generatore in generatori:
            for candidato in generatore:
                if candidato["id"] in visti:
                    continue
                visti.add(candidato["id"])
                scelti.append(candidato)
                nuovi += 1
                if len(scelti) >= argomenti.totale:
                    break
            if len(scelti) >= argomenti.totale:
                break
        print(f"  trovati {nuovi} nuovi (totale: {len(scelti)})")

    if not scelti:
        sys.exit("\nNessun video trovato. Prova con --min-altezza 1920: "
                 "i veri 4K verticali sono rari, il Full HD verticale è "
                 "comunque perfetto per TikTok/Reels.")

    with open(FILE_MANIFEST, "w", newline="", encoding="utf-8") as f:
        campi = ["id", "fonte", "tema", "larghezza", "altezza",
                 "autore", "pagina_web", "url"]
        scrittore = csv.DictWriter(f, fieldnames=campi)
        scrittore.writeheader()
        scrittore.writerows(scelti)
    print(f"\nManifest salvato: {FILE_MANIFEST} ({len(scelti)} video)")

    if argomenti.solo_lista:
        print("Modalità --solo-lista: nessun download eseguito.")
        return

    print(f"\nScarico {len(scelti)} video in {CARTELLA_VIDEO}/ ...")
    riusciti = 0
    for indice, candidato in enumerate(scelti, 1):
        print(f"[{indice}/{len(scelti)}]")
        if scarica_file(sessione, candidato):
            riusciti += 1
    print(f"\nFatto: {riusciti}/{len(scelti)} video scaricati in {CARTELLA_VIDEO}/")


if __name__ == "__main__":
    main()
