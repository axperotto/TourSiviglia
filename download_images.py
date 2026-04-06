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
import time
import urllib.error
import urllib.request

from PIL import Image as PILImage

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

# Mappa URL originale → nome file locale
PHOTOS = [
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef"
        "/Panorama_Seville_from_Giralda_Tower.jpg"
        "/1280px-Panorama_Seville_from_Giralda_Tower.jpg",
        "1280px-Panorama_Seville_from_Giralda_Tower.jpg",
        "Panorama di Siviglia dalla Giralda (copertina + panoramica)",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8"
        "/Seville_at_night_1.jpg/1280px-Seville_at_night_1.jpg",
        "1280px-Seville_at_night_1.jpg",
        "Siviglia di notte (header Giorno 0)",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15"
        "/Catedral_de_Sevilla._Exterior._01.JPG"
        "/960px-Catedral_de_Sevilla._Exterior._01.JPG",
        "960px-Catedral_de_Sevilla._Exterior._01.JPG",
        "Cattedrale di Siviglia",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b"
        "/Alc%C3%A1zar_Seville_April_2019-11.jpg"
        "/1280px-Alc%C3%A1zar_Seville_April_2019-11.jpg",
        "1280px-Alc%C3%A1zar_Seville_April_2019-11.jpg",
        "Real Alcázar di Siviglia (header Giorno 1)",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f"
        "/Patio_de_las_doncellas_edited.jpg"
        "/960px-Patio_de_las_doncellas_edited.jpg",
        "960px-Patio_de_las_doncellas_edited.jpg",
        "Patio de las Doncellas – Real Alcázar",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9"
        "/Exterior_of_Mezquita%2C_Cordoba_%282369161889%29.jpg"
        "/1280px-Exterior_of_Mezquita%2C_Cordoba_%282369161889%29.jpg",
        "1280px-Exterior_of_Mezquita%2C_Cordoba_%282369161889%29.jpg",
        "Mezquita-Catedral di Córdoba esterno (header Giorno 2)",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e"
        "/Mezquita-Catedral_de_C%C3%B3rdoba_-_Blending_of_Christian_and_Moorish_architecture.jpg"
        "/960px-Mezquita-Catedral_de_C%C3%B3rdoba_-_Blending_of_Christian_and_Moorish_architecture.jpg",
        "960px-Mezquita-Catedral_de_C%C3%B3rdoba_-_Blending_of_Christian_and_Moorish_architecture.jpg",
        "Interno della Mezquita-Catedral",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e"
        "/Triana_embankment_Seville_Spain.jpg"
        "/1280px-Triana_embankment_Seville_Spain.jpg",
        "1280px-Triana_embankment_Seville_Spain.jpg",
        "Quartiere Triana (header Giorno 3)",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c"
        "/Puente_de_Triana%2C_Sevilla%2C_Espa%C3%B1a%2C_2015-12-06%2C_DD_67.JPG"
        "/960px-Puente_de_Triana%2C_Sevilla%2C_Espa%C3%B1a%2C_2015-12-06%2C_DD_67.JPG",
        "960px-Puente_de_Triana%2C_Sevilla%2C_Espa%C3%B1a%2C_2015-12-06%2C_DD_67.JPG",
        "Triana – ponti sul Guadalquivir",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6"
        "/Plaza_de_Espa%C3%B1a_%28Sevilla%29_-_01.jpg"
        "/960px-Plaza_de_Espa%C3%B1a_%28Sevilla%29_-_01.jpg",
        "960px-Plaza_de_Espa%C3%B1a_%28Sevilla%29_-_01.jpg",
        "Plaza de España",
    ),
    (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81"
        "/Torre_del_Oro_Guadalquivir_Seville_Spain.jpg"
        "/960px-Torre_del_Oro_Guadalquivir_Seville_Spain.jpg",
        "960px-Torre_del_Oro_Guadalquivir_Seville_Spain.jpg",
        "Torre del Oro sul Guadalquivir",
    ),
]


USER_AGENT = (
    "TourSivigliaBot/1.0 (travel PDF generator; personal use) "
    "Python-urllib/" + sys.version.split()[0]
)

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def download(url: str, dest: str, description: str) -> bool:
    """Download *url* to *dest*. Returns True on success."""
    if os.path.isfile(dest):
        print(f"  ✓ già presente: {os.path.basename(dest)}")
        return True
    print(f"  ↓ {description} …", end=" ", flush=True)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            # Verify it's a valid image
            PILImage.open(io.BytesIO(data)).verify()
            with open(dest, "wb") as f:
                f.write(data)
            size_kb = len(data) // 1024
            print(f"OK ({size_kb} KB)")
            return True
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < MAX_RETRIES:
                wait = RETRY_DELAY * attempt
                print(f"rate-limited, retry in {wait}s …", end=" ", flush=True)
                time.sleep(wait)
                continue
            print(f"ERRORE: {exc}")
            return False
        except Exception as exc:
            print(f"ERRORE: {exc}")
            return False
    return False


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"Cartella immagini: {IMAGES_DIR}\n")

    ok = 0
    fail = 0
    for i, (url, filename, description) in enumerate(PHOTOS):
        dest = os.path.join(IMAGES_DIR, filename)
        if download(url, dest, description):
            ok += 1
        else:
            fail += 1
        # Delay between downloads to avoid Wikimedia rate limiting
        if i < len(PHOTOS) - 1:
            time.sleep(3)

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
