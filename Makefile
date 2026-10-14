# Les cibles du cours. `make reproduce` doit donner deux fois les mêmes chiffres.
export PYTHONPATH := src
PY ?= python

reproduce: data split train metrics

data:            ## télécharge les données UCI et vérifie leur empreinte
	$(PY) -m credit.data --check data/sha256.txt

split:           ## la coupe figée par la graine de config.yaml
	$(PY) -m credit.split --config config.yaml

train:           ## le modèle naïf et la logistique calibrée, seuil par les coûts
	$(PY) -m credit.model --config config.yaml

metrics:         ## les métriques sur la validation : metrics.json
	$(PY) -m credit.evaluate --config config.yaml --out metrics.json

compare:         ## jalon 2 : les trois modèles sur le test, une seule fois : compare.json
	$(PY) -m credit.compare --config config.yaml --out compare.json

predict:         ## batch : scorer un CSV de clients (voir batch/predict.py)
	$(PY) batch/predict.py --in data/processed/validation.csv --out predictions.csv

test:            ## les cinq tests
	$(PY) -m pytest -q tests/

app:             ## l'interface minimale
	streamlit run app/app.py

clean:
	rm -rf data/processed models/*.pkl metrics.json compare.json predictions.csv

.PHONY: reproduce data split train metrics compare predict test app clean
