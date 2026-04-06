#!/usr/bin/env python3
"""
Scarica tutte le foto reali usate dal generatore PDF nella cartella images/.

Esegui UNA VOLTA con connessione internet prima di generare il PDF:

    python3 download_images.py
    python3 generate_tour_pdf.py

Le immagini vengono salvate in images/<nome_file>.jpg.
Se un file esiste già viene saltato (non riscaricato).
"""

import io
import os
import sys
import urllib.request

from PIL import Image as PILImage

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

# Mappa URL originale → nome file locale
PHOTOS = [
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5"
        "/Sevilla_desde_la_Giralda_-_2.jpg/1280px-Sevilla_desde_la_Giralda_-_2.jpg",
        "1280px-Sevilla_desde_la_Giralda_-_2.jpg",
        "Panorama di Siviglia dalla Giralda (copertina + panoramica)",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e"
        "/Seville_night.jpg/1280px-Seville_night.jpg",
        "1280px-Seville_night.jpg",
        "Siviglia di notte (header Giorno 0)",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53"
        "/Catedral_de_Sevilla_-_02.jpg/800px-Catedral_de_Sevilla_-_02.jpg",
        "800px-Catedral_de_Sevilla_-_02.jpg",
        "Cattedrale di Siviglia",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b"
        "/Real_Alcazar_Seville_2008.jpg/1280px-Real_Alcazar_Seville_2008.jpg",
        "1280px-Real_Alcazar_Seville_2008.jpg",
        "Real Alcázar di Siviglia (header Giorno 1)",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66"
        "/Real_Alcazar_of_Seville_-_Patio_de_las_Doncellas.jpg"
        "/800px-Real_Alcazar_of_Seville_-_Patio_de_las_Doncellas.jpg",
        "800px-Real_Alcazar_of_Seville_-_Patio_de_las_Doncellas.jpg",
        "Patio de las Doncellas – Real Alcázar",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6"
        "/Mezquita_de_C%C3%B3rdoba_-_panoramio_%281%29.jpg"
        "/1280px-Mezquita_de_C%C3%B3rdoba_-_panoramio_%281%29.jpg",
        "1280px-Mezquita_de_C%C3%B3rdoba_-_panoramio_%281%29.jpg",
        "Mezquita-Catedral di Córdoba esterno (header Giorno 2)",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e"
        "/Mosque-Cathedral_of_Cordoba_interior.jpg"
        "/800px-Mosque-Cathedral_of_Cordoba_interior.jpg",
        "800px-Mosque-Cathedral_of_Cordoba_interior.jpg",
        "Interno della Mezquita-Catedral",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97"
        "/Triana%2C_Seville.jpg/1280px-Triana%2C_Seville.jpg",
        "1280px-Triana%2C_Seville.jpg",
        "Quartiere Triana (header Giorno 3)",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85"
        "/Triana_Sevilla.jpg/800px-Triana_Sevilla.jpg",
        "800px-Triana_Sevilla.jpg",
        "Triana – ponti sul Guadalquivir",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4"
        "/Plaza_de_Espa%C3%B1a_%28Sevilla%29.jpg"
        "/800px-Plaza_de_Espa%C3%B1a_%28Sevilla%29.jpg",
        "800px-Plaza_de_Espa%C3%B1a_%28Sevilla%29.jpg",
        "Plaza de España",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1"
        "/Seville_golden_tower.jpg/800px-Seville_golden_tower.jpg",
        "800px-Seville_golden_tower.jpg",
        "Torre del Oro sul Guadalquivir",
    ),
]


def download(url: str, dest: str, description: str) -> bool:
    """Download *url* to *dest*. Returns True on success."""
    if os.path.isfile(dest):
        print(f"  ✓ già presente: {os.path.basename(dest)}")
        return True
    print(f"  ↓ {description} …", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        # Verify it's a valid image
        PILImage.open(io.BytesIO(data)).verify()
        with open(dest, "wb") as f:
            f.write(data)
        size_kb = len(data) // 1024
        print(f"OK ({size_kb} KB)")
        return True
    except Exception as exc:
        print(f"ERRORE: {exc}")
        return False


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"Cartella immagini: {IMAGES_DIR}\n")

    ok = 0
    fail = 0
    for url, filename, description in PHOTOS:
        dest = os.path.join(IMAGES_DIR, filename)
        if download(url, dest, description):
            ok += 1
        else:
            fail += 1

    print(f"\n{'='*50}")
    print(f"Completato: {ok} foto scaricate/presenti, {fail} errori.")
    if fail:
        print("Alcune foto non sono state scaricate. Controlla la connessione internet.")
        print("Il PDF userà immagini segnaposto per quelle mancanti.")
    else:
        print("Tutte le foto sono pronte. Esegui: python3 generate_tour_pdf.py")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
