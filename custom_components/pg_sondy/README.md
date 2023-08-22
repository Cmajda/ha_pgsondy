# PG sondy
získání dat z meteostanic https://pgsonda.cz/prehled/
zatím jen suchomasty start


## integrace senzoru
```yaml
senzor:
	- platform: pg_sondy
	  url: "https://www.pgsonda.cz/suchomasty/"
	  name: klonk
```
## příklad nastavení karty
```yaml
type: entities
entities:
  - entity: sensor.klonk_average_speed
  - entity: sensor.klonk_max_speed
  - entity: sensor.klonk_min_speed
  - entity: sensor.klonk_wind_rotation
```