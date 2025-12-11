import time
import board
import busio
import buzzer
import sys
# Importation de la nouvelle librairie cst816
import cst816 

# --- CONSTANTES DE GESTE NUMÉRIQUES ---
GESTURE_NONE = 0
SWIPE_UP = 1
SWIPE_DOWN = 2
SWIPE_LEFT = 3
SWIPE_RIGHT = 4

# --- VARIABLES GLOBALES ---
touch = None 
current_screen = "HOME"
# Variables d'état pour la machine à états et le cooldown
_touch_is_active = False # True si le doigt est en contact
last_update_time = time.monotonic() # Pour le cooldown
COOLDOWN_TIME = 0.4 # Temps minimum entre deux événements tactiles

# Définition des états possibles de l'écran (Navigation en Croix)
MENU_SCREENS = {
    "HOME": "Heure Actuelle",
    "UP": "Temperature",
    "DOWN": "Pression Atmospherique",
    "LEFT": "Humidite",
    "RIGHT": "Luminosite"
}

# --- CONFIGURATION DU MATÉRIEL CST816 ---
try:
    # Initialisation I2C standard
    i2c = board.I2C() 
    
    # Initialisation du contrôleur CST816
    touch = cst816.CST816(i2c)
    
    # Vérification de l'initialisation
    if touch.who_am_i():
        print("Capteur CST816 detecte et initialise avec succès.")
    else:
        print("CST816 initialise, mais 'who_am_i' ne correspond pas (adresse I2C?).")
        
except Exception as e:
    print(f"Erreur lors de l'initialisation du CST816: {e}. Le tactile sera desactive.")
    touch = None


def handle_gesture(gesture_id):
    """
    Met à jour l'état de l'écran (current_screen) selon la logique de navigation en croix.
    """
    global current_screen
    
    new_screen = current_screen
    
    # 1. GESTION DES TRANSITIONS DEPUIS L'ÉCRAN HOME (Centre de la croix)
    if current_screen == "HOME":
        if gesture_id == SWIPE_UP:
            new_screen = "UP"
        elif gesture_id == SWIPE_DOWN:
            new_screen = "DOWN"
        elif gesture_id == SWIPE_LEFT: 
            new_screen = "LEFT"
        elif gesture_id == SWIPE_RIGHT:
            new_screen = "RIGHT"
    
    # 2. GESTION DES RETOURS À HOME (Depuis les branches de la croix)
    elif current_screen in ["UP", "DOWN", "LEFT", "RIGHT"]:
        # N'importe quel SWIPE retourne à HOME
        if gesture_id != GESTURE_NONE: 
            new_screen = "HOME"
            
    # 3. MISE À JOUR FINALE
    if new_screen != current_screen:
        current_screen = new_screen
        try:
            buzzer.play_switch() 
        except NameError:
            pass
        
        print(f"Changement d'écran vers: {current_screen}")


def check_and_update_menu():
    """ 
    Gère le capteur en utilisant la méthode stable du "Touch Up" et le cooldown.
    Ceci remplace la fonction handle_touch_and_update_state précédente.
    """
    global touch, _touch_is_active, last_update_time
    
    if touch is None:
        return     
    
    temps_actuel = time.monotonic()
    
    # 1. Lecture des Registres CST816
    # NOTE: Cette ligne est cruciale et doit être lue à chaque itération du main loop.
    gesture_id = touch.get_gesture() 
    is_pressed = touch.get_touch() # True tant que le doigt est là

    if is_pressed:
        # Le doigt est sur l'écran (Touch Down ou Touch Move)
        # On active le flag d'état
        _touch_is_active = True
        
    elif not is_pressed and _touch_is_active:
        # --- 2. GESTION DU TOUCH UP (Le doigt vient d'être retiré) ---
        
        # Le doigt a été retiré, on réinitialise l'état
        _touch_is_active = False 
        print(f"DEBUG: Touch UP détecté. Geste lu (ID): {gesture_id}")
        # C'est la ligne la plus importante pour briser la boucle:
        # On ne traite le geste que si le COOLDOWN est écoulé.
        if (temps_actuel - last_update_time) > COOLDOWN_TIME:
            
            # On vérifie si un SWIPE a été enregistré au moment du Touch Up
            if gesture_id != GESTURE_NONE:
                
                # Geste valide détecté. On le traite.
                handle_gesture(gesture_id)
                
                # Réinitialiser le temps pour le cooldown (empêche la prochaine lecture immédiate)
                last_update_time = temps_actuel
        
    # Si le doigt n'est pas pressé ET que _touch_is_active est False: on ne fait rien.