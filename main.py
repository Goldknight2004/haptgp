# main.py

import board
import time
import sys
import bme280 
import veml
import Screen
import rgb
import menu
import horloge
import buzzer

# --- 1. INITIALISATION DES PÉRIPHÉRIQUES ---
i2c = board.I2C()

#L'initialisation se fait via les fonctions des modules
bme280_obj = bme280.init_bme280(i2c)
veml7700_obj = veml.init_veml7700(i2c)
# Cette fonction configure l'écran et les labels de texte.
Screen.init_screen()
rtc = horloge.init_horloge(i2c)
buzzer.init_buzzer()
# --- 2. PARAMÈTRES DE GESTION DU TEMPS ET DES DONNÉES ---
INTERVALLE_AFFICHAGE = 1
temps_dernier_update = time.monotonic()
# Initialiser les variables pour qu'elles existent avant le premier cycle
avg_temp, avg_humi, avg_press, avg_light = 0.0, 0.0, 0.0, 0.0
current_time_str = time.strftime("%H:%M:%S")
try: 
    print("Démarrage du système. Appuyez sur Ctrl+C pour arrêter.")
    print("---------------------------------")
    print(f"Demarrage du systeme. Intervalle cible: {INTERVALLE_AFFICHAGE:.1f}s")
    while True: 
        # DANS UNE BOUCLE NON-BLOQUANTE, TOUTES LES VÉRIFICATIONS SE FONT ICI
        temps_actuel = time.monotonic()
        menu.check_and_update_menu()
        # Vérifie si l'intervalle d'une seconde s'est écoulé
        if temps_actuel - temps_dernier_update >= INTERVALLE_AFFICHAGE:
            rgb.cycle_couleurs()
            # --- 1. LECTURE DES MODULES (Instantanée grâce à l'oversampling) ---
            start_time = time.monotonic() # Mesure le debut de la lecture
            # Récupérer les 3 valeurs du BME
            avg_temp, avg_humi, avg_press = bme280.get_bme_readings(bme280_obj)
            
            current_time_str = horloge.get_formatted_time(rtc)
            
            # Récupérer la valeur du VEML
            avg_light = veml.get_veml_reading(veml7700_obj)
            lecture_duration = time.monotonic() - start_time
            
            start_spi_time = time.monotonic()
                
            # --- 2. MISE À JOUR DE L'ÉCRAN TFT (SPI) ---
            start_spi_time = time.monotonic()
            # La mise a jour de l'ecran est maintenant optimiser dans Screen.py
            Screen.update_display(avg_temp, avg_humi, avg_press, avg_light,current_time_str)
            spi_duration = time.monotonic() - start_spi_time

            # Mettre à jour le temps de référence pour la prochaine vérification (1.0 seconde plus tard)
            temps_dernier_update = temps_actuel
            
        # C'est ici que le CPU vérifie les tâches non-bloquantes (ex: moteur haptique)
        pass 
    
except KeyboardInterrupt:
    print("\nArrêt du programme main.")
    sys.exit(0)