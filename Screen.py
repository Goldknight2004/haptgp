import board
import displayio
import terminalio
import menu
from adafruit_display_text.bitmap_label import Label
from fourwire import FourWire
from adafruit_gc9a01a import GC9A01A

# Constantes de l'écran (240x240 pixels)
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 240
HORIZONTAL_PADDING = 10
# Variables globales pour l'affichage
main_group = None
temp_label = None
hum_label = None
pres_label = None
lux_label = None
time_label = None
display = None

# Variables d'etat pour l'optimisation (stockent la derniere valeur affichee)
last_temp = float('inf')
last_humi = float('inf')
last_pres = float('inf')
last_lux = float('inf')
last_time = "Initialisation en cours..." 

# Liste des labels dynamiques
DYNAMIC_LABELS = []

# --- FONCTIONS D'UTILITAIRES D'AFFICHAGE ---

def _hide_all_labels():
    """Rend tous les labels temporairement invisibles."""
    # S'assurer que DYNAMIC_LABELS est initialisé avant l'appel
    if DYNAMIC_LABELS:
        for label in DYNAMIC_LABELS:
            label.hidden = True

def _center_label_verticale(label):
    """Calcule la position pour centrer le label."""
    # Recalcule X et Y en fonction de la taille actuelle du texte (bounding_box)
    # Assurez-vous que l'étiquette est centrée verticalement
    label.y = (SCREEN_HEIGHT // 2) - (label.bounding_box[3] // 2)
    
# --- FONCTION D'INITIALISATION ---
def init_screen():
    """Initialise le bus SPI et l'écran TFT, puis dessine les éléments statiques."""
    global display,main_group, temp_label, hum_label, lux_label, pres_label, time_label,last_time
    global DYNAMIC_LABELS # Ajout de la variable globale ici

    # Configuration des pins SPI et TFT
    spi = board.SPI()
    tft_cs = board.D8
    tft_dc = board.D25
    tft_reset = board.D27

    displayio.release_displays()

    # Initialisation du bus d'affichage
    display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
    display = GC9A01A(display_bus, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

    # Groupe Racine (Root Group)
    main_group = displayio.Group()
    display.root_group = main_group

    # Arrière-plan (Noir)
    bg_bitmap = displayio.Bitmap(SCREEN_WIDTH, SCREEN_HEIGHT, 1)
    color_palette = displayio.Palette(2)
    color_palette[0] = 0x000000# Noir
    
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=color_palette, x=0, y=0)
    main_group.append(bg_sprite)

    # --- Éléments de Texte Dynamiques ---
    
    # Texte 1: Heure (HOME)
    time_label = Label(terminalio.FONT, text="00:00:00", line_spacing=0.8, color=0xFFFFFF, scale=2) # Blanc, tres grande taille
    main_group.append(time_label)
    
    # Texte 2: Température (UP)
    temp_label = Label(terminalio.FONT, text="Temp: -- C", color=0x00FFFF, scale=2) # Cyan, grande taille
    main_group.append(temp_label)

    # Texte 3: Humidité (LEFT)
    # Note: L'ancien hum_label contenait Hum et Pres, maintenant il ne contient que Hum
    hum_label = Label(terminalio.FONT, text="Humidite:\n-- %", color=0xFFFF00, line_spacing=1.5, scale=2) # Jaune
    main_group.append(hum_label)

    # Texte 4: Pression (DOWN)
    pres_label = Label(terminalio.FONT, text= "Pression:\n-- kPa", color=0x00FF00, line_spacing=1.5, scale=2) # Vert
    main_group.append(pres_label)

    # Texte 5: Luminosité (RIGHT)
    lux_label = Label(terminalio.FONT, text="Lux: --", color=0xFF00FF, scale=2) # Magenta
    main_group.append(lux_label)

    
    # Remplir la liste des labels pour la gestion de la visibilite
    DYNAMIC_LABELS = [time_label, temp_label, hum_label, lux_label, pres_label]
    
    # S'assurer que seul le label de l'heure est visible au demarrage
    _hide_all_labels()
    time_label.hidden = False
    time_label.x = HORIZONTAL_PADDING
# --- FONCTION DE MISE À JOUR DES DONNÉES ---
def update_display(temp, hum, press, lux, current_time_str):
    """Met à jour les labels de l'écran SEULEMENT si la valeur a change et force le rafraîchissement."""
    global display, last_temp, last_humi, last_pres, last_lux,last_time
    
    if display is None:
        return

    # Indicateur pour savoir si nous devons appeler display.refresh()
    should_refresh = False
    
    # *** 1. Cacher tous les labels avant la sélection ***
    _hide_all_labels() 

    # 0. Écran HOME (Heure)
    if menu.current_screen == "HOME":
        print ("HOME")
        if current_time_str != last_time:
            time_label.text = current_time_str
            time_label.x = HORIZONTAL_PADDING # IMPORTANT: Recentre après changement de texte
            _center_label_verticale(time_label)
            last_time = current_time_str
            should_refresh = True
        time_label.hidden = False
        
    # 1. Température (UP)
    elif menu.current_screen == "UP":
        print ("up")
        formatted_temp = f"{temp:.1f}"
        formatted_last_temp = f"{last_temp:.1f}"
        
        if formatted_temp != formatted_last_temp:
            temp_label.text = f"Temp: {formatted_temp} C"
            _center_label_verticale(temp_label)
            temp_label.x = (SCREEN_WIDTH // 2) - (temp_label.bounding_box[2] // 2)
            last_temp = temp
            should_refresh = True
        temp_label.hidden = False

    # 2. Humidité (LEFT)
    elif menu.current_screen == "LEFT":
        print ("left")
        formatted_hum = f"Humidite:\n{hum:.1f} %"
        formatted_last_hum = f"Humidite:\n{last_humi:.1f} %"
        
        if formatted_hum != formatted_last_hum:
            hum_label.text = formatted_hum
            _center_label_verticale(hum_label) # IMPORTANT: Recentre après changement de texte
            hum_label.x = (SCREEN_WIDTH // 2) - (hum_label.bounding_box[2] // 2)
            last_humi = hum
            should_refresh = True
        hum_label.hidden = False
        
    # 3. Pression (DOWN)    
    elif menu.current_screen == "DOWN": 
        print ("down")
        # Pression est divisée par 10 pour hPa -> kPa
        formatted_press = f"{press / 10:.1f}"
        formatted_last_pres = f"{last_pres / 10:.1f}"
          
        if formatted_press != formatted_last_pres: 
             text_to_display = f"Pression:\n{formatted_press} kPa"
             pres_label.text = text_to_display
             pres_label.x = (SCREEN_WIDTH // 2) - (pres_label.bounding_box[2] // 2)
             _center_label_verticale(pres_label) # IMPORTANT: Recentre après changement de texte
             last_pres = press
             should_refresh = True
        pres_label.hidden = False
    
    # 4. Luminosite (RIGHT)
    elif menu.current_screen == "RIGHT":
        print ("right")
        formatted_lux = f"{lux:.2f}"
        formatted_last_lux = f"{last_lux:.2f}"
        
        if formatted_lux != formatted_last_lux:
            lux_label.text = f"Lux: {formatted_lux}"
            lux_label.x = (SCREEN_WIDTH // 2) - (lux_label.bounding_box[2] // 2)
            _center_label_verticale(lux_label) # IMPORTANT: Recentre après changement de texte
            last_lux = lux
            should_refresh = True
            
        lux_label.hidden = False

    # *** Rafraîchissement Conditionnel ***
    # On n'appelle display.refresh() que si au moins un label a ete mis a jour
    if should_refresh and not display.auto_refresh:
        display.refresh()