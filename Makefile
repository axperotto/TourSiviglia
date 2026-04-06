.PHONY: pdf images clean

## Genera il PDF completo (scarica le immagini se mancanti, poi genera il PDF)
pdf:
	python3 generate_tour_pdf.py

## Scarica le foto da Wikimedia nella cartella images/
images:
	python3 download_images.py

## Rimuove il PDF generato
clean:
	rm -f tour_siviglia.pdf
