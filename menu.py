import time
import board
import busio
import buzzer
import sys
# Importation de la nouvelle librairie cst816
import cst816 

# --- CONSTANTES DE GESTE NUMÉRIQUES (Vérifiez si elles correspondent à cst816) ---
# Ces valeurs sont les plus courantes pour le CST816/820.
GESTURE_NONE = 0
SWIPE_UP = 1
SWIPE_DOWN = 2
SWIPE_LEFT = 3
SWIPE_RIGHT = 4

# --- VARIABLES GLOBALES ---
touch = None 
current_screen = "HOME"
# Variables d'état
_touch_is_active = False # True si le doigt est en contact


# Définition des états possibles de l'écran
MENU_SCREENS = {
    "HOME": "Heure Actuelle",
    "UP": "Temperature",
    "DOWN": "Pression Atmospherique",
    "LEFT": "Humidite",
    "RIGHT": "Luminosite"
}

# --- CONFIGURATION DU MATÉRIEL CST816 ---
try:
    # Initialisation I2C standard (utilise le bus I2C par défaut du Raspberry Pi)
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
    Met à jour l'état de l'écran avec les règles :
    1. L'écran suit le doigt
    2. Toutes les transitions doivent repasser par 'HOME'.
    """
    global current_screen
    
    new_screen = current_screen
    
    # 1. GESTION DES SWIPES VERTICAUX 
    if gesture_id == SWIPE_UP:
        if current_screen == "HOME":
            new_screen = "UP"
        elif current_screen == "DOWN":
            new_screen = "HOME"
            
    elif gesture_id == SWIPE_DOWN:
        if current_screen == "HOME":
            new_screen = "DOWN"
        elif current_screen == "UP":
            new_screen = "HOME"

    # 2. GESTION DES SWIPES HORIZONTAUX 
    elif gesture_id == SWIPE_LEFT: 
        if current_screen == "HOME":
            new_screen = "RIGHT"
        elif current_screen == "LEFT":
            new_screen = "HOME"
            
    elif gesture_id == SWIPE_RIGHT:
        if current_screen == "HOME":
            new_screen = "LEFT"
        elif current_screen == "RIGHT":
            new_screen = "HOME"
            
    # 3. MISE À JOUR FINALE
    if new_screen != current_screen:
        current_screen = new_screen
        buzzer.play_switch()
        print(f"Changement d'écran vers: {current_screen}")
        
def check_and_update_menu():
    """ 
    Gère le capteur en liant l'activité tactile (Touch Up) au geste.
    Implémente un Cooldown strict pour stopper la boucle infinie du gesture_id persistant.
    """
    global touch, _touch_is_active
    
    if touch is None:
        return     
    # --- 2. Lecture des Registres CST816 ---
    gesture_id = touch.get_gesture() 
    is_pressed = touch.get_touch() # True tant que le doigt est là
    
    
    if is_pressed:
        # Le doigt est sur l'écran (Touch Down ou Touch Move)
        _touch_is_active = True
    elif not is_pressed and _touch_is_active:
        # Le doigt vient d'être retiré (Touch Up)
        
        # ... (Gestion du cooldown)
        
        # On vérifie si un SWIPE a été enregistré au moment du Touch Up
        if gesture_id != GESTURE_NONE:
            
            # Geste valide détecté. On le traite.
            handle_gesture(gesture_id)
            
        else:
            # Pas de SWIPE (gesture_id=0), c'est un TAP.
            # 🛑 SUPPRIMEZ la ligne suivante :
            buzzer.play_click() 
            
        # Un événement (SWIPE ou TAP) a été traité. On active le cooldown.
        _touch_is_active = False 
