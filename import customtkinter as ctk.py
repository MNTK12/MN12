import customtkinter as ctk
from PIL import Image
import pygame
import os

class LabyrintheApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- CONFIGURATION INITIALE ---
        self.title("Labyrinthe")
        self.geometry("800x600")
        
        # On force la couleur de fond de la fenêtre à être identique au fond de l'image
        # pour éviter les flashs gris lors des changements de page
        self.configure(fg_color="black")

        # --- AUDIO ---
        pygame.mixer.init()
        self.play_background_music("audio/games.mp3")

        # --- CHARGEMENT DE L'IMAGE (MÉTHODE ULTRA-ROBUSTE) ---
        self.setup_background()

        # --- CONTENEUR DE NAVIGATION ---
        # On place ce container AVANT tout le reste pour qu'il soit sur la couche supérieure
        self.main_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Affichage du menu
        self.show_main_menu()
        
        # Lier le redimensionnement
        self.bind("<Configure>", self.resize_bg)

    def setup_background(self):
        """Force l'affichage de l'image en utilisant des références multiples."""
        try:
            # On utilise le chemin relatif direct
            img_path = "image/femme.jpg"
            
            # Ouverture avec conversion RGB pour garantir la compatibilité
            pil_img = Image.open(img_path).convert("RGB")
            
            # Création de l'image CTk
            self.bg_image = ctk.CTkImage(
                light_image=pil_img, 
                dark_image=pil_img, 
                size=(self.winfo_width(), self.winfo_height())
            )
            
            # Création du label. IMPORTANT : master=self (la fenêtre root)
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Force l'image à être derrière tous les futurs boutons
            self.bg_label.lower()
            
        except Exception as e:
            print(f"Erreur visuelle : {e}")

    def clear_container(self):
        """Nettoie l'écran sans toucher au fond."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_container()
        
        # Utilisation de titres transparents
        ctk.CTkLabel(
            self.main_container, text="BIENVENUE", 
            font=("Arial", 60, "bold"), text_color="white", fg_color="transparent"
        ).place(relx=0.5, rely=0.25, anchor="center")

        # Boutons avec fg_color opaque pour être bien visibles sur l'image
        btn_style = {
            "font": ("Arial", 30, "bold"),
            "width": 400, "height": 70,
            "fg_color": "#1f1f1f", # Couleur sombre solide
            "hover_color": "#333333",
            "border_width": 2,
            "border_color": "white"
        }

        ctk.CTkButton(self.main_container, text="Créer une Salle", command=self.show_create, **btn_style).place(relx=0.5, rely=0.55, anchor="center")
        ctk.CTkButton(self.main_container, text="Se connecter", command=self.show_connect, **btn_style).place(relx=0.5, rely=0.72, anchor="center")

    def show_create(self):
        self.clear_container()
        ctk.CTkLabel(self.main_container, text="MODE CRÉATION", font=("Arial", 40, "bold"), text_color="white").place(relx=0.5, rely=0.2, anchor="center")
        ctk.CTkButton(self.main_container, text="Retour", command=self.show_main_menu).place(relx=0.1, rely=0.9)

    def show_connect(self):
        self.clear_container()
        ctk.CTkLabel(self.main_container, text="REJOINDRE", font=("Arial", 40, "bold"), text_color="white").place(relx=0.5, rely=0.2, anchor="center")
        ctk.CTkButton(self.main_container, text="Retour", command=self.show_main_menu).place(relx=0.1, rely=0.9)

    def resize_bg(self, event):
        """Recalcule la taille de l'image de fond en temps réel."""
        if event.widget == self:
            if hasattr(self, 'bg_image'):
                self.bg_image.configure(size=(event.width, event.height))

    def play_background_music(self, path):
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.3)
            except: pass

if __name__ == "__main__":
    app = LabyrintheApp()
    app.mainloop()