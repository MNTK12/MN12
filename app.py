import customtkinter as ctk
from PIL import Image
import pygame
import os
import socket
import threading

class LabyrintheApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Labyrinthe Multijoueur")
        self.geometry("900x700")

        # --- RÉSEAU ---
        self.client_socket = None
        self.terrain_choisi = ""

        # --- AUDIO ---
        pygame.mixer.init()
        self.is_muted = False
        self.load_audio()
        
        # --- INITIALISATION VISUELLE ---
        self.setup_background()
        
        self.btn_style = {
            "width": 320, "height": 60, "font": ("Segoe UI", 20, "bold"), 
            "corner_radius": 15, "border_width": 2, "border_color": "#00E5FF", 
            "fg_color": "#1A1A1A", "hover_color": "#00B8D4"
        }
        self.btn2_style = {
            "width": 320, "height": 260, "font": ("Segoe UI", 20, "bold"), 
            "corner_radius": 15, "border_width": 2, "border_color": "#00E5FF", 
            "fg_color": "#1A1A1A", "hover_color": "#00B8D4",
            "compound": "top"
        }

        self.setup_menu()
        self.bind("<Configure>", self.redimensionner_image)
        
        # Lancement automatique de la musique
        self.play_music()

    def load_audio(self):
        """Charge les fichiers audio et les icônes du haut-parleur"""
        try:
            # Musique de fond
            pygame.mixer.music.load(os.path.join("audio", "games.mp3"))
            pygame.mixer.music.set_volume(0.5)
            # Effet sonore
            self.click_sound = pygame.mixer.Sound(os.path.join("audio", "effet.wav"))
            
            # Icônes pour le bouton Muet
            img_on = Image.open(os.path.join("image", "of.png"))
            img_off = Image.open(os.path.join("image", "on.png"))
            self.icon_on = ctk.CTkImage(img_on,size=(20, 20))
            self.icon_off = ctk.CTkImage(img_off,size=(20, 20))
        except:
            print("Erreur : Fichiers audio ou icônes manquants.")
            self.icon_on = self.icon_off = True

    def toggle_mute(self):
        """Bascule entre mode muet et actif"""
        self.is_muted = not self.is_muted
        if self.is_muted:
            pygame.mixer.music.pause()
            self.mute_btn.configure(image=self.icon_off)
        else:
            pygame.mixer.music.unpause()
            self.mute_btn.configure(image=self.icon_on)

    def play_music(self):
        if not self.is_muted:
            pygame.mixer.music.play(-1)

    def play_click(self):
        if not self.is_muted and hasattr(self, 'click_sound'):
            self.click_sound.play()

    def setup_background(self):
        try:
            path = os.path.join("image", "femme.jpg")
            self.pil_img = Image.open(path).convert("RGB")
            self.bg_image = ctk.CTkImage(light_image=self.pil_img, dark_image=self.pil_img, size=(900, 700))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()
        except: pass

    def redimensionner_image(self, event):
        if event.widget == self:
            self.bg_image.configure(size=(event.width, event.height))

    def nettoyer_ecran(self):
        for widget in self.winfo_children():
            if widget != getattr(self, "bg_label", None) and widget != getattr(self, "mute_btn", None):
                widget.destroy()
        
        # Recréation/Repositionnement du bouton muet pour qu'il reste au premier plan
        self.mute_btn = ctk.CTkButton(self, text="", image=self.icon_on if not self.is_muted else self.icon_off, 
                                      width=40, height=40, fg_color="transparent", hover_color="#333",
                                      command=self.toggle_mute)
        self.mute_btn.place(relx=0.95, rely=0.05, anchor="center")
        self.after(10, self.bg_label.lower)

    def setup_menu(self):
        self.nettoyer_ecran()
        ctk.CTkLabel(self, text="L A B Y R I N T H E", font=("Impact", 80), text_color="#00E5FF", fg_color="transparent").place(relx=0.5, rely=0.2, anchor="center")
        
        ctk.CTkButton(self, text="CRÉER UNE SALLE", command=lambda: [self.play_click(), self.show_terrain_choice()], **self.btn_style).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkButton(self, text="SE CONNECTER", command=self.play_click, **self.btn_style).place(relx=0.5, rely=0.65, anchor="center")

    def show_terrain_choice(self):
        self.nettoyer_ecran()
        ctk.CTkLabel(self, text="CHOISISSEZ VOTRE TERRAIN", font=("Impact", 35, "bold"), text_color="white").place(relx=0.5, rely=0.15, anchor="center")
        
        # Chargement images terrains
        try:
            img1 = ctk.CTkImage(Image.open("image/glace.jpg"), size=(300, 200))
            img2 = ctk.CTkImage(Image.open("image/foret.jpeg"), size=(300, 200))
            img3 = ctk.CTkImage(Image.open("image/feu.jpg"), size=(300, 200))
        except: img1 = img2 = img3 = None

        terrains = [("Donjon de Glace", img1), ("Forêt Maudite", img2), ("Labyrinthe de Feu", img3)]
        
        for i, (t, img) in enumerate(terrains):
            ctk.CTkButton(self, text=t, image=img, command=lambda name=t: [self.play_click(), self.connect_to_server(name)], **self.btn2_style).place(rely=0.45, relx=0.15 + (i*0.35), anchor="center")
        
        ctk.CTkButton(self, text="← Retour", font=("arial", 15, "bold"), command=lambda: [self.play_click(), self.setup_menu()], width=100, fg_color="transparent").place(relx=0.05, rely=0.05)

    def connect_to_server(self, terrain_name):
        self.terrain_choisi = terrain_name
        # Logique réseau...
        self.show_waiting_room()

    def show_waiting_room(self):
        self.nettoyer_ecran()
        ctk.CTkLabel(self, text=f"TERRAIN : {self.terrain_choisi}", font=("Segoe UI", 35, "bold"), text_color="#00E5FF").place(relx=0.5, rely=0.1, anchor="center")
        
        self.list_frame = ctk.CTkFrame(self, fg_color="#1A1A1A", border_width=2, border_color="#00E5FF", width=450, height=350)
        self.list_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.list_frame.pack_propagate(False)
        
        ctk.CTkLabel(self.list_frame, text="JOUEURS DANS LA SALLE", font=("Segoe UI", 20, "bold"), text_color="#00E5FF").pack(pady=15)
        self.players_label = ctk.CTkLabel(self.list_frame, text="Attente...", font=("Consolas", 18), text_color="white")
        self.players_label.pack(pady=10)

        ctk.CTkButton(self, text="LANCER LA PARTIE", fg_color="#27ae60", hover_color="#2ecc71", width=250, height=50, font=("Segoe UI", 20, "bold"), command=self.play_click).place(relx=0.5, rely=0.85, anchor="center")

if __name__ == "__main__":
    app = LabyrintheApp()
    app.mainloop()