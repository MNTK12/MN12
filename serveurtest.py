import socket, threading, json

class LabyServeur:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Évite l'erreur Address in Use
        self.server.bind(('0.0.0.0', 5555))
        self.server.listen()
        self.salles = {}
        # Carte de base (petit exemple, tu peux mettre ta grande map ici)
        self.MAP_BASE = [
            [1]*20, # Bordure haute
            [1, 0, 7, 0, 1, 8, 0, 0, 0, 1, 0, 0, 0, 7, 0, 0, 3, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 5, 1, 0, 1, 0, 0, 0, 0, 0, 0, 5, 0, 0, 1],
            [1, 0, 1, 1, 1, 3, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1],
            [1, 8, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 5, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 0, 0, 3, 0, 0, 0, 0, 8, 0, 0, 1, 1, 1, 1, 0, 1],
            [1, 7, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 3, 1, 0, 1],
            [1, 0, 0, 0, 3, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1],
            [1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 5, 0, 1, 0, 0, 0, 1],
            [1, 8, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 7, 0, 0, 1, 3, 0, 2, 1],
            [1]*20  # Bordure basse
        ]

        self.MAP_FORET = [
            [1]*20,
            [1,0,0,0,1,0,0,0,0,1, 1,0,0,0,1,0,0,0,0,1],
            [1,0,1,0,0,0,1,1,0,1, 1,0,1,0,0,0,1,1,0,1],
            [1,0,0,5,0,0,0,0,2,1, 1,0,0,3,0,0,0,0,3,1],
            [1]*20
        ]

        self.MAP_FEU = [
            [1]*20,
            [1,0,0,0,1,0,0,0,0,1, 1,0,0,0,1,0,0,0,0,1],
            [1,0,1,0,0,0,1,1,0,1, 1,0,1,0,0,0,1,1,0,1],
            [1,0,0,0,0,0,0,0,2,1, 1,0,0,4,0,0,0,0,4,1], # 4 = lave
            [1]*20
        ]


    def broadcast(self, nom_salle, message):
        """Envoie un message JSON à tous les joueurs d'une salle."""
        if nom_salle in self.salles:
            data = json.dumps(message).encode('utf-8')
            for conn in self.salles[nom_salle]["joueurs"]:
                try:
                    conn.send(data)
                except:
                    pass

    def handle_client(self, conn, addr):
        j_id = f"J_{addr[1]}"
        ma_salle = None
        print(f"[LOG] {j_id} connecté.")

        while True:
            try:
                data = conn.recv(2048).decode('utf-8')
                if not data:
                    break
                msg = json.loads(data)

                # --- ROUTE : LISTER LES SALLES ---
                if msg["type"] == "get_salles":
                    liste = [{"nom": k, "terrain": v["terrain"]} for k, v in self.salles.items()]
                    conn.send(json.dumps({"type": "liste_salles", "salles": liste}).encode())

                # --- ROUTE : CRÉER SALLE ---
                elif msg["type"] == "creer_salle":
                    ma_salle = j_id

                    # Choisir la bonne carte selon le terrain
                    terrain = msg.get("terrain", "Inconnu")
                    if terrain == "Forêt Maudite":
                        map_choice = self.MAP_FORET
                    elif terrain == "Labyrinthe de Feu":
                        map_choice = self.MAP_FEU
                    else:
                        map_choice = self.MAP_BASE

                    self.salles[ma_salle] = {
                        "terrain": terrain,
                        "joueurs": [conn],
                        "etat": {j_id: {"pos": [1, 1], "vies": 3, "avatar": msg["avatar"]}},
                        "map": map_choice,
                        "winners": []  # liste des gagnants
                    }
                    self.broadcast(ma_salle, {"type": "update_attente", "joueurs": [msg["avatar"]]})


                # --- ROUTE : REJOINDRE SALLE ---
                elif msg["type"] == "rejoindre_salle":
                    ma_salle = msg["salle"]
                    if ma_salle in self.salles:
                        self.salles[ma_salle]["joueurs"].append(conn)
                        self.salles[ma_salle]["etat"][j_id] = {"pos": [1, 1], "vies": 3, "avatar": msg["avatar"]}
                        avatars = [p["avatar"] for p in self.salles[ma_salle]["etat"].values()]
                        self.broadcast(ma_salle, {"type": "update_attente", "joueurs": avatars})

                # --- ROUTE : MOUVEMENT ---
                elif msg["type"] == "move":
                    target_salle = msg["salle"]
                    if target_salle in self.salles:
                        salle = self.salles[target_salle]
                        y, x = salle["etat"][j_id]["pos"]

                        if msg["dir"] == "up": y -= 1
                        elif msg["dir"] == "down": y += 1
                        elif msg["dir"] == "left": x -= 1
                        elif msg["dir"] == "right": x += 1

                        if salle["map"][y][x] != 1:  # pas un mur
                            salle["etat"][j_id]["pos"] = [y, x]

                            # Bombe
                            if salle["map"][y][x] == 3:
                                salle["etat"][j_id]["vies"] -= 1
                                salle["etat"][j_id]["pos"] = [1, 1]

                            # Drapeau
# --- BLOC VICTOIRE CORRIGÉ ---
                            elif salle["map"][y][x] == 2:
                                if j_id not in salle["winners"]:
                                    salle["winners"].append(j_id)

                                # Bloquer le joueur sur la case
                                salle["etat"][j_id]["pos"] = [y, x]

                                # 1. Calcul du classement (Proximité)
                                drapeau_pos = [y, x]
                                autres = [pid for pid in salle["etat"] if pid not in salle["winners"]]
                                
                                classement_restant = sorted(
                                    autres,
                                    key=lambda pid: abs(salle["etat"][pid]["pos"][0] - drapeau_pos[0]) +
                                                    abs(salle["etat"][pid]["pos"][1] - drapeau_pos[1])
                                )

                                # 2. Convertir les IDs en AVATARS pour le client
                                final_ids = salle["winners"] + classement_restant
                                final_avatars = [salle["etat"][pid]["avatar"] for pid in final_ids]

                                # 3. Envoyer le signal de fin avec les avatars
                                self.broadcast(target_salle, {
                                    "type": "end_game",
                                    "winners": final_avatars
                                })





                        # Mise à jour générale
                        self.broadcast(target_salle, {"type": "update_game", "etat": salle["etat"]})


                # --- ROUTE : LANCER ---
                elif msg["type"] == "lancer_jeu":
                    if ma_salle in self.salles:
                        self.broadcast(ma_salle, {
                            "type": "start_game",
                            "map": self.salles[ma_salle]["map"],
                            "etat_initial": self.salles[ma_salle]["etat"],
                            "ma_salle": ma_salle
                        })
            except:
                break

        # Nettoyage si déco
        if ma_salle in self.salles and conn in self.salles[ma_salle]["joueurs"]:
            self.salles[ma_salle]["joueurs"].remove(conn)
            if not self.salles[ma_salle]["joueurs"]:
                del self.salles[ma_salle]
        conn.close()

    def start(self):
        print("--- SERVEUR LABYRINTHE ACTIF (PORT 5555) ---")
        while True:
            c, a = self.server.accept()
            threading.Thread(target=self.handle_client, args=(c, a), daemon=True).start()


if __name__ == "__main__":
    LabyServeur().start()
