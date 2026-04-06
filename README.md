# 🌟 Tour Siviglia & Córdoba

Guida di viaggio personalizzata in PDF per un viaggio in Andalusia.
**Periodo:** 29 Aprile – 3 Maggio | **Destinazioni:** Siviglia + Córdoba (day trip)

## 📄 Contenuto del PDF

Il PDF generato (`tour_siviglia.pdf`) include:

- **Copertina** con immagine hero di Siviglia
- **Indice** del tour
- **Mappa generale** dell'Andalusia con tabella distanze
- **Itinerario giorno per giorno:**
  - 📍 29 Aprile – Arrivo a Siviglia (sera)
  - 🕌 30 Aprile – Siviglia Iconica (Real Alcázar, Cattedrale, Santa Cruz, Casa de Pilatos)
  - 🕌 1 Maggio – Day Trip a Córdoba (Mezquita, Judería, Ponte Romano)
  - 🌊 2 Maggio – Siviglia Autentica (Triana, Plaza de España, Metropol Parasol)
  - ✈️ 3 Maggio – Partenza
- **Consigli pratici** (biglietti, trasporti, ristoranti, meteo)
- **QR Code** per prenotazioni dirette
- **Quarta di copertina**

## 🚀 Come generare il PDF

### Requisiti

```bash
pip install reportlab Pillow requests qrcode
```

### Comando unico (consigliato)

```bash
make pdf
```

Questo comando:
1. Controlla se le immagini sono presenti in `images/`
2. Le scarica automaticamente da Wikimedia se mancanti (richiede internet)
3. Genera il PDF `tour_siviglia.pdf`
4. Verifica quante foto reali sono state incluse

### Esecuzione manuale (con foto reali)

Per ottenere un PDF con **foto vere** (fotografie dei luoghi), scarica prima le immagini:

```bash
# 1. Scarica le foto da Wikimedia (una volta sola, richiede internet)
python3 download_images.py
# oppure: make images

# 2. Genera il PDF con le foto reali
python3 generate_tour_pdf.py
```

Le foto vengono salvate nella cartella `images/` e riutilizzate nelle generazioni successive.

### Esecuzione (senza internet)

Se non hai connessione internet, il PDF viene generato comunque con immagini illustrative al posto delle foto:

```bash
python3 generate_tour_pdf.py
```

### Output

Il file `tour_siviglia.pdf` viene creato nella directory corrente.

## 🗂 File nel repository

| File | Descrizione |
|------|-------------|
| `generate_tour_pdf.py` | Script Python per generare il PDF |
| `download_images.py` | Script per scaricare le foto reali in `images/` |
| `Makefile` | Pipeline `make pdf` (download + genera + verifica) |
| `images/` | Cartella per le foto scaricate (non incluse nel repo) |
| `tour_siviglia.pdf` | PDF generato (pronto da stampare o condividere) |

## 📋 Struttura del Tour

```
29 Apr (sera)   → Arrivo + passeggiata centro
30 Apr          → Real Alcázar + Cattedrale + Santa Cruz + Casa de Pilatos
 1 Mag          → Day trip Córdoba (AVE 40 min) – Mezquita + Judería
 2 Mag          → Triana + Plaza de España + Metropol Parasol (tramonto)
 3 Mag (mattina)→ Partenza dall'aeroporto SVQ
```

## 🔑 Prenotazioni Consigliate

- **Real Alcázar:** [alcazarsevilla.es](https://www.alcazarsevilla.es/entradas/) *(prenotare con 2+ settimane di anticipo)*
- **Cattedrale di Siviglia:** [catedraldesevilla.es](https://www.catedraldesevilla.es/)
- **Mezquita Córdoba:** [mezquita-catedraldecordoba.es](https://mezquita-catedraldecordoba.es/)
- **Treno AVE:** [renfe.com](https://www.renfe.com/)
- **Flamenco (Casa de la Memoria):** [casadelamemoria.es](https://www.casadelamemoria.es/)