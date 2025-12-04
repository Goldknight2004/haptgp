import adafruit_ds3231
import time
import sys
# On garde board pour la compatibilite, mais l'objet i2c est passe en argument
# import board 

# --- CONFIGURATION ET DÉPENDANCES ---
JOURS = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"]
MOIS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jui", 
        "Jui", "Aoû", "Sep", "Oct", "Nov", "Déc"]

# --- INITIALISATION ---
def init_horloge(i2c_bus):
    """
    Initialise l'objet RTC DS3231 sur le bus I2C fourni.
    
    Args:
        i2c_bus: L'objet I2C initialise depuis main.py.

    Returns:
        L'objet adafruit_ds3231.DS3231 ou None en cas d'erreur.
    """
    rtc = None
    try:
        # L'objet i2c est maintenant passe en argument, et non recree localement
        rtc = adafruit_ds3231.DS3231(i2c_bus)
        print("Horloge RTC DS3231 detectee et initialisee.")
        
        # Synchronisation initiale du Pi vers le RTC
        current_system_time = time.localtime(time.time())
        if current_system_time.tm_year >= 2024:
            print(f"Synchronisation initiale RTC : {time.strftime('%Y-%m-%d %H:%M:%S', current_system_time)}")
            rtc.datetime = current_system_time
        else:
            print("ATTENTION : L'heure systeme est invalide. RTC non synchronise au demarrage.")
            
    except Exception as e:
        print(f"Erreur d'initialisation RTC (non critique, utilisation du temps systeme): {e}")
        rtc = None
        
    return rtc # IMPORTANT: On retourne l'objet RTC

# --- LECTURE DE L'HORLOGE (Renomme pour clarte) ---
def get_formatted_time(rtc_obj):
    """
    Lit l'heure depuis l'objet RTC et la retourne au format heure\ndate.
    
    Args:
        rtc_obj: L'objet DS3231 initialisé (ou None).
        
    Returns:
        Une chaîne de caractères formatée (ex: "15:30:00\nMercredi, 27 Novembre 2024").
    """
    if rtc_obj:
        try:
            # t est l'heure lue du DS3231
            t = rtc_obj.datetime 
            
            # Formater l'heure (H:M:S Jour, Mois, Année)
            heure_formatee = "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)
            
            # tm_wday : 0=Lundi, 6=Dimanche. On ajuste pour la liste JOURS (0=Dimanche, 6=Samedi)
            jour_semaine = JOURS[(t.tm_wday + 1) % 7] 
            nom_mois = MOIS[t.tm_mon - 1] 
            date_formatee = f"{jour_semaine}, {t.tm_mday} {nom_mois} {t.tm_year}"
            
            current_time_str = f"{heure_formatee}\n{date_formatee}"
            
            # Affichage dynamique sur la console (pour debug)
            sys.stdout.write(f"RTC: {heure_formatee} {date_formatee}\r")
            sys.stdout.flush()
            
            return current_time_str # IMPORTANT: On retourne la chaîne de caractères
        
        except Exception as e:
            # print(f"Erreur de lecture du RTC: {e}") # Peut causer du bruit, on le garde en commentaire
            pass # Fallback
            
    # Fallback : Si RTC n'est pas initialisé ou s'il y a une erreur de lecture
    # Utilisez l'heure système Python
    return time.strftime("%H:%M:%S\n%a, %d %b %Y")