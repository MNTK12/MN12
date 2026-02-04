import customtkinter as ctk
from PIL import Image
import socket, threading, json, os, random, pygame

class LabyrintheApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x850")
        self.title("Labyrinthe Online - Sync Edition")
        
        self.mon_id = None
        self.avatar_choisi = "👤"
        self.client_socket = None
        self.current_map = []
        self.points_mouvement = 0
        self.is_moving = False
        self.is_muted = False
        
        pygame.mixer.init()
        self.load_resources()
        self.setup_background()
        self.bind("<Configure>", self.redimensionner_fond)
        self.choisir_avatar_screen()

    def load_resources(self):
        try:
            pygame.mixer.music.load("audio/games.mp3")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
            self.icon_on = ctk.CTkImage(Image.open("image/of.png"), size=(25, 25))
            self.icon_off = ctk.CTkImage(Image.open("image/on.png"), size=(25, 25))
        except: pass

    def setup_background(self):
        try:
            self.bg_raw = Image.open("image/femme.jpg")
            self.bg_img = ctk.CTkImage(self.bg_raw, size=(1000, 850))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_img, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()
        except: pass

    def redimensionner_fond(self, event):
        if event.widget == self:
            try: self.bg_img.configure(size=(event.width, event.height))
            except: pass

    def nettoyer(self):
        for w in self.winfo_children():
            if w != getattr(self, "bg_label", None): w.destroy()
        self.mute_btn = ctk.CTkButton(self, text="", image=self.icon_on if not self.is_muted else self.icon_off, 
                                      width=40, height=40, fg_color="transparent", command=self.toggle_mute)
        self.mute_btn.place(relx=0.96, rely=0.04, anchor="center")

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted: pygame.mixer.music.pause()
        else: pygame.mixer.music.unpause()
        self.mute_btn.configure(image=self.icon_on if not self.is_muted else self.icon_off)

    def connecter(self):
        if not self.client_socket:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(('127.0.0.1', 5555))
                self.mon_id = f"J_{self.client_socket.getsockname()[1]}"
                threading.Thread(target=self.ecouter, daemon=True).start()
                return True
            except: return False
        return True
    
    def ecouter(self):
            while True:
                try:
                    data = self.client_socket.recv(4096).decode('utf-8')
                    if not data: break
                    msg = json.loads(data)
                    
                    if msg["type"] == "update_attente":
                        self.after(0, lambda: self.label_attente.configure(text="SQUAD :\n" + "\n".join(msg["joueurs"])))
                    elif msg["type"] == "start_game":
                        self.after(0, lambda: self.interface_jeu(msg))
                    elif msg["type"] == "update_game":
                        self.after(0, lambda: self.dessiner_plateau(msg["etat"]))
                    elif msg["type"] == "liste_salles":
                        self.after(0, lambda: self.afficher_liste_salles(msg["salles"]))
                    elif msg["type"] == "end_game":
                        # On récupère la liste, si elle n'existe pas on met une liste vide
                        w = msg.get("winners", [])
                        self.after(0, lambda: self.afficher_fin(w))
                    elif msg["type"] == "winner_message":
                        self.after(0, lambda: self.afficher_winner(msg["message"]))
                except: break
    def afficher_fin(self, winners):
            self.nettoyer()
            
            # Titre stylé
            ctk.CTkLabel(self, text="🏆 PODIUM FINAL 🏆", font=("Impact", 60), text_color="#FFD700").pack(pady=30)

            # Affichage du classement
            frame_podium = ctk.CTkFrame(self, fg_color="transparent")
            frame_podium.pack(pady=20)

            for i, avatar in enumerate(winners):
                rang = "1er" if i == 0 else f"{i+1}ème"
                color = "#FFD700" if i == 0 else "#C0C0C0" if i == 1 else "#CD7F32" if i == 2 else "white"
                
                lbl = ctk.CTkLabel(frame_podium, 
                                text=f"{rang} : {avatar}", 
                                font=("Arial", 30, "bold"), 
                                text_color=color)
                lbl.pack(pady=5)

            # --- BOUTONS DE FIN ---
            btn_frame = ctk.CTkFrame(self, fg_color="transparent")
            btn_frame.pack(pady=40)

            # Bouton 1 : Recommencer (Retour au choix du terrain)
            ctk.CTkButton(btn_frame, 
                        text="CHANGER DE TERRAIN", 
                        command=self.choisir_terrain_screen, 
                        width=250, height=50, 
                        fg_color="#1f538d").grid(row=0, column=0, padx=20)

            # Bouton 2 : Menu Principal
            ctk.CTkButton(btn_frame, 
                        text="MENU PRINCIPAL", 
                        command=self.menu_principal, 
                        width=250, height=50, 
                        fg_color="gray").grid(row=0, column=1, padx=20)

    # --- ÉCRANS ---
    def choisir_avatar_screen(self):
        self.nettoyer()
        ctk.CTkLabel(self, text="SÉLECTIONNE TON AVATAR", font=("Impact", 45), text_color="#00E5FF").pack(pady=50)
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack()
        avatars = ["🥷", "🤖", "🧙‍♂️", "🧛‍♂️", "🦁", "👻", "🧟", "👽"]
        for i, e in enumerate(avatars):
            ctk.CTkButton(f, text=e, width=90, height=90, font=("Arial", 40), command=lambda a=e: self.valider_avatar(a)).grid(row=i//4, column=i%4, padx=10, pady=10)

    def valider_avatar(self, a):
        self.avatar_choisi = a
        self.menu_principal()

    def menu_principal(self):
        self.nettoyer()
        ctk.CTkLabel(self, text="L A B Y R I N T H E", font=("Impact", 80), text_color="#00E5FF").place(relx=0.5, rely=0.25, anchor="center")
        ctk.CTkButton(self, text="CRÉER UNE SALLE", command=self.choisir_terrain_screen, width=300, height=60, font=("Impact", 25)).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkButton(self, text="REJOINDRE UNE SALLE", command=self.demander_salles, width=300, height=60, font=("Impact", 25)).place(relx=0.5, rely=0.65, anchor="center")

    def choisir_terrain_screen(self):
        self.nettoyer()
        ctk.CTkLabel(self, text="CHOISIS TON TERRAIN", font=("Impact", 35)).pack(pady=30)
        terrains = [("Donjon de Glace", "glace.jpg"), ("Forêt Maudite", "foret.jpeg"), ("Labyrinthe de Feu", "feu.jpg")]
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack()
        for i, (nom, img_p) in enumerate(terrains):
            try: img = ctk.CTkImage(Image.open(f"image/{img_p}"), size=(250, 150))
            except: img = None
            ctk.CTkButton(f, text=nom, image=img, compound="top", command=lambda n=nom: self.creer_salle(n)).grid(row=0, column=i, padx=10)

    def demander_salles(self):
        if self.connecter():
            self.client_socket.send(json.dumps({"type": "get_salles"}).encode())

    def afficher_liste_salles(self, salles):
        self.nettoyer()
        ctk.CTkLabel(self, text="SALLES OUVERTES", font=("Impact", 35)).pack(pady=30)
        if not salles:
            ctk.CTkLabel(self, text="Aucune salle active...", font=("Arial", 20)).pack()
            ctk.CTkButton(self, text="Retour", command=self.menu_principal).pack(pady=20)
            return
        for s in salles:
            btn = ctk.CTkButton(self, text=f"Hôte: {s['nom']} | {s['terrain']}", width=400, height=50, command=lambda n=s['nom']: self.rejoindre(n))
            btn.pack(pady=10)

    def creer_salle(self, terrain):
        if self.connecter():
            self.client_socket.send(json.dumps({"type": "creer_salle", "avatar": self.avatar_choisi, "terrain": terrain}).encode())
            self.attente_ecran()

    def rejoindre(self, nom_salle):
        self.client_socket.send(json.dumps({"type": "rejoindre_salle", "salle": nom_salle, "avatar": self.avatar_choisi}).encode())
        self.attente_ecran()

    def attente_ecran(self):
        self.nettoyer()
        self.label_attente = ctk.CTkLabel(self, text="Attente des joueurs...", font=("Impact", 30))
        self.label_attente.pack(pady=100)
        ctk.CTkButton(self, text="LANCER LE JEU", command=lambda: self.client_socket.send(json.dumps({"type":"lancer_jeu"}).encode())).pack()
    def interface_jeu(self, data):
            self.nettoyer()
            self.current_map = data["map"]
            self.ma_salle = data["ma_salle"]
            
            # --- AJOUT ICI : Création du label pour les mouvements ---
            self.stat_lab = ctk.CTkLabel(self, text="MOUVEMENTS : 0", font=("Impact", 25), text_color="#00E5FF")
            self.stat_lab.pack(pady=10)

            self.bind("<Up>", lambda e: self.move("up"))
            self.bind("<Down>", lambda e: self.move("down"))
            self.bind("<Left>", lambda e: self.move("left"))
            self.bind("<Right>", lambda e: self.move("right"))

            self.can = ctk.CTkCanvas(self, width=800, height=500, bg="black", highlightthickness=2, highlightbackground="#00E5FF")
            self.can.pack(pady=20)
            
            ctrl = ctk.CTkFrame(self, fg_color="transparent")
            ctrl.pack()

    def move(self, d):
        self.client_socket.send(json.dumps({"type":"move", "dir":d, "salle":self.ma_salle}).encode())
        self.points_mouvement = random.randint(1,6)
        self.stat_lab.configure(text=f"MOUVEMENTS : {self.points_mouvement}")
    def afficher_winner(self, message):
            if hasattr(self, 'stat_lab'):
                self.stat_lab.configure(text=message, text_color="#FFD700")
    def dessiner_plateau(self, etat):
        self.can.delete("all")
        rows, cols = len(self.current_map), len(self.current_map[0])
        cs = min(1000 // cols, 1000 // rows)
        ma_pos = etat[self.mon_id]["pos"]
        
        for r in range(rows):
            for c in range(cols):
                dist = abs(ma_pos[0]-r) + abs(ma_pos[1]-c)
                if dist <= 2:
                    x, y = c*cs, r*cs
                    v = self.current_map[r][c]

                    # Choisir la couleur AVANT de dessiner
                    if v == 1:      # mur
                        color = "#222"
                    elif v == 0:    # sol libre
                        color = "#050505"
                    elif v == 2:    # drapeau
                        color = "grey"
                    elif v == 3:    # bombe
                        color = "red"   # 🔴 toute la case rouge
                    elif v == 4:    # lave
                        color = "orange"
                    elif v == 5:    # ronces
                        color = "darkgreen"
                    elif v == 6:    # ronces
                        color = "#140777"
                    elif v == 7:    # ronces
                        color = "#009407"
                    elif v == 8:    # ronces
                        color = "#340295"
                    else:
                        color = "#050505"

                    # Dessiner le rectangle avec la couleur choisie
                    self.can.create_rectangle(x, y, x+cs, y+cs, fill=color, outline="#111")

                    # Ajouter éventuellement un symbole par-dessus
                    if v == 2:
                        self.can.create_text(x+cs/2, y+cs/2, text="🏁")
                    elif v == 3:
                        self.can.create_text(x+cs/2, y+cs/2, text="💣")
                    elif v == 4:
                        self.can.create_text(x+cs/2, y+cs/2, text="🔥")
                    elif v == 5:
                        self.can.create_text(x+cs/2, y+cs/2, text="🌵")
                    elif v == 6:
                        self.can.create_text(x+cs/2, y+cs/2, text="🥶")
                    elif v == 7:
                        self.can.create_text(x+cs/2, y+cs/2, text="🌲")
                    elif v == 8:
                        self.can.create_text(x+cs/2, y+cs/2, text="🌀")
        # Dessiner les avatars des joueurs
        for info in etat.values():
            y, x = info["pos"]
            self.can.create_text(x*cs+cs/2, y*cs+cs/2, text=info["avatar"], font=("Arial", int(cs*0.4)))


if __name__ == "__main__":
    app = LabyrintheApp()
    app.mainloop()