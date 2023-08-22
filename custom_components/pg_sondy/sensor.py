import requests
from lxml import html
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from datetime import timedelta
import logging

# Nastavení loggeru pro tuto integraci
_LOGGER = logging.getLogger(__name__)

# Doménové jméno integrace
DOMAIN = "pg_sondy"

# Schéma pro platformu senzorů
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("url"): cv.string,  # URL adresa pro získání dat
    vol.Required("name"): cv.string,  # Název pro senzory
})

# Funkce pro nastavení platformy
def setup_platform(hass, config, add_entities, discovery_info=None):
    url = config["url"]
    base_name = config["name"]
    
    # Seznam senzorů
    sensors = [
        SondaSensor(f"{base_name} Max Speed", url, "max_speed", f"{base_name}_max_speed"),
        SondaSensor(f"{base_name} Average Speed", url, "avg_speed", f"{base_name}_average_speed"),
        SondaSensor(f"{base_name} Min Speed", url, "min_speed", f"{base_name}_min_speed"),
        RotationSensor(f"{base_name} Wind Rotation", url, "wind_rotation", f"{base_name}_wind_rotation")
    ]
    
    # Přidání senzorů
    add_entities(sensors, True)

# Třída pro senzory rychlosti větru
class SondaSensor(Entity):
    def __init__(self, name, url, attribute, unique_id):
        self._url = url
        self._name = name
        self._attribute = attribute
        self._value = None
        self._unique_id = unique_id

    # Název senzoru
    @property
    def name(self):
        return self._name

    # Hodnota senzoru
    @property
    def state(self):
        if self._value is not None:
            return round(float(self._value), 1)
        return None

    # Hodnota senzoru
    @property
    def native_value(self):
        return self._value
    
    @property
    def unit_of_measurement(self):
        return "m/s"

    # Unikátní identifikátor senzoru
    @property
    def unique_id(self):
        return self._unique_id

    # Informace o zařízení
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
        }

    # Přátelský název senzoru
    @property
    def friendly_name(self):
        return f"{self._name} {self._attribute.replace('_', ' ').title()}"
    
    # Ikona senzoru
    @property
    def icon(self):
        if self._value is not None:
            if self._attribute == "wind_rotation":
                return "mdi:compass"
            wind_speed = float(self._value)
            if wind_speed <= 2:
                return "mdi:weather-windy"
            elif wind_speed <= 5:
                return "mdi:weather-windy-variant"
            else:
                return "mdi:weather-windy-variant"
        return "mdi:alert-circle-outline"

    # Aktualizace dat senzoru
    @Throttle(timedelta(minutes=1))
    def update(self):
        page = requests.get(self._url)
        if page.status_code == 200:
            tree = html.fromstring(page.content)
            if self._attribute == "max_speed":
                self._value = tree.xpath('/html/body/windgraf[1]/svg/text[11]')[0].text
            elif self._attribute == "avg_speed":
                self._value = tree.xpath('/html/body/windgraf[1]/svg/text[9]')[0].text
            elif self._attribute == "min_speed":
                self._value = tree.xpath('/html/body/windgraf[1]/svg/text[7]')[0].text
        else:
            _LOGGER.error("Failed to fetch data from %s", self._url)

# Třída pro senzor směru větru
class RotationSensor(Entity):
    def __init__(self, name, url, attribute, unique_id):
        self._url = url
        self._name = name
        self._attribute = attribute
        self._value = None
        self._unique_id = unique_id

    # Název senzoru
    @property
    def name(self):
        return self._name

    # Hodnota senzoru
    @property
    def state(self):
        return self._value

    # Jednotka měření senzoru
    @property
    def unit_of_measurement(self):
        return "°"

    # Unikátní identifikátor senzoru
    @property
    def unique_id(self):
        return self._unique_id

    # Informace o zařízení
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
        }

    # Přátelský název senzoru
    @property
    def friendly_name(self):
        return f"{self._name} {self._attribute.replace('_', ' ').title()}"
    
    # Ikona senzoru
    @property
    def icon(self):
        return "mdi:compass"

    # Aktualizace dat senzoru
    @Throttle(timedelta(minutes=1))
    def update(self):
        page = requests.get(self._url)
        if page.status_code == 200:
            tree = html.fromstring(page.content)
            if self._attribute == "wind_rotation":
                rotation_text = tree.xpath('/html/body/windgraf[1]/svg/text[5]')[0].text
                rotation_value = int(rotation_text.replace("°", ""))
                self._value = rotation_value
        else:
            _LOGGER.error("Failed to fetch data from %s", self._url)
