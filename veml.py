import adafruit_veml7700
import time
import math

# --- Fonction de Calibration Polynomiale (Degré 2) ---
# NOTE TRES IMPORTANTE: Remplacez les coefficients a, b et c ci-dessous par les valeurs 
# les plus precises que vous pouvez extraire d'Excel (ex: 8 decimales pour A).
# Votre equation est: y = A*x^2 + B*x + C
def calibrate_lux(raw_lux):
    """
    Applique la fonction polynomiale de calibration de degre 2.
    
    Equation: y = A * x^2 + B * x + C
    Où x est la valeur lue par le VEML7700 et y est la valeur calibrée.
    """
    x = raw_lux
    
    # Coefficients tires de votre courbe de regression
    # VEUILLEZ UTILISER LES VALEURS PRECISES D'EXCEL ICI
    a = 0.00000924351234  # Coefficient du x^2 (remplacez '0.000009' par la valeur complete, ex: 0.0000092435)
    b = 0.29065123    # Coefficient du x
    c = 219.645123    # Ordonnee a l'origine (constante)
    
    # Calcul de la valeur calibrée (y)
    calibrated_lux = (a * x**2) + (b * x) + c
    
    # On s'assure que la valeur calibrée ne soit jamais négative
    return max(0.0, calibrated_lux)


# --- Initialisation de l'Objet ---
def init_veml7700(i2c_bus):
    """Initialise l'objet VEML7700."""
    try:
        veml7700 = adafruit_veml7700.VEML7700(i2c_bus)
        print("Capteur VEML7700 initialise.")
        return veml7700
    except ValueError:
        print("ERREUR: VEML7700 non trouvé. Vérifiez le câblage I2C.")
        return None

# --- Lecture Calibrée ---
def get_veml_reading(veml_sensor):
    """
    Retourne la lecture stable de la lumière (Lux) après calibration.
    """
    if veml_sensor is None:
        return 0.0
        
    try:
        # 1. Lecture de la valeur brute du capteur
        raw_light = veml_sensor.light
        
        # 2. Application de la calibration polynomiale
        calibrated_light = calibrate_lux(raw_light)
        
        return calibrated_light
        
    except Exception as e:
        print(f"Erreur lors de la lecture du VEML7700: {e}")
        return 0.0