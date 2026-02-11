 ## Exemple de module lvl 

dans main

 ```python
 from src.infrastructure import setup_logging
 
 def main():
 setup_logging(
 module_levels={
 "app.http": 20,   # logging.INFO
 "app.etl": 10,    # logging.DEBUG
 }
 )
 ```

dans les fichier
```python
import logging

logger = logging.getLogger("app.http")

logger.debug("Détail HTTP")   # ❌ ignoré (niveau INFO)
logger.info("Appel API OK")   # ✅ affiché
```

## ajouter des champs pour le format json:
```python
logger.info(
    "Ingestion terminée",
    extra={
        "event": "ods_ingest",
        "station_id": station_id,
        "rows": rows
    }
)
```
