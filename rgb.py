import board
import neopixel
import time 
import random

# --- Configuration et variables globales (COLLÉES à GAUCHE) ---
PIXEL_PIN = board.D21  # == GPIO18 (PWM-capable)
NUM_PIXELS = 12


current_color_index = 0
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.2, auto_write=True)

def cycle_couleurs():
    """
    Applique la couleur suivante du cycle (non-bloquant).
    """
    # Declaration necessaire pour modifier les variables globales
    global current_color_index
    global pixels
    
    try:
     # 1. Generation des trois composantes R, G, B entre 0 et 255
        # random.randint(a, b) inclut les deux bornes
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        
        new_color = (r, g, b)
        # 2. Applique la couleur 
        pixels.fill(new_color)
        
        # 3. Incremente l'index
        current_color_index = current_color_index + 1 
        

    
    except Exception as e:
        print(f"Erreur dans cycle_couleurs: {e}")


def eteindre_pixels():
    """ Fonction de securite pour eteindre les LEDs. """
    pixels.fill((0, 0, 0))

# Eteindre les LEDs au demarrage du module
eteindre_pixels()