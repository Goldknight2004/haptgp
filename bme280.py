# bme_module.py

import time
from adafruit_bme280 import basic as adafruit_bme280
import board # Nécessaire pour les constantes de suréchantillonnage

# --- Initialisation de l'Objet ---
def init_bme280(i2c_bus):
    """Initialise l'objet BME280 et configure l'oversampling interne."""
    try:
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c_bus, 0x76)
        
        # Configuration de l'oversampling interne (Moyennage fait par la puce)
        bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X16
        bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X16
        bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
        
        bme280.sea_level_pressure = 1013.25
        return bme280
    except ValueError:
        print("ERREUR: BME280 non trouvé. Vérifiez le câblage.")
        return None

# --- Lecture Instantanée Stable ---
def get_bme_readings(bme_sensor):
    """Retourne la lecture unique (déjà moyennée par le capteur)."""
    if bme_sensor is None:
        return 0.0, 0.0, 0.0
    
    # Lecture instantanée des valeurs stables
    stable_temp = bme_sensor.temperature
    stable_humi = bme_sensor.relative_humidity
    stable_press = bme_sensor.pressure

    return stable_temp, stable_humi, stable_press