import socket
import threading
import json
import random

class LabyServeur:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('0.0.0.0', 5555))
        self.server.listen()
        self.salles = {} 

        # --- CONFIGURATION DES TERRAINS (0: chemin, 1: mur, 2: sortie, 3: piège/bombe) ---
        self.TERRAINS_DATA = {
            "Donjon de Glace": {
                "grid": [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1],
                    [1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1],
                    [1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,3,0,1,0,0,0,1],
                    [1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,0,1,0,1,1,1],
                    [1,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0,1],
                    [1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1,1,1,1,0,1],
                    [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,1],
                    [1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1],
                    [1,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,1],
                    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1],
                    [1,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,3,1,0,1,0,0,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1],
                    [1,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,1],
                    [1,0,1,1,1,1,1,1,1,0,1,0,1,0,1,1,1,0,1,1,1,1,1,0,1],
                    [1,0,1,0,0,0,0,0,1,0,1,0,0,0,1,0,1,0,0,0,0,0,1,0,1],
                    [1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1],
                    [1,0,1,0,1,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,1],
                    [1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1,0,1],
                    [1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,1],
                    [1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1],
                    [1,0,0,0,0,0,1,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,1],
                    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ],
                "image_fond": "glace.jpg"
            },
            "Forêt Maudite": {
                "grid": [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
                    [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
                    [1,0,1,0,0,0,1,2,1,0,0,0,1,0,1],
                    [1,0,1,1,1,0,1,0,1,0,1,1,1,0,1],
                    [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ],
                "image_fond": "foret.jpeg"
            },
            "Labyrinthe de Feu": {
                "grid": [
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,1,0,0,0,0,0,1,0,0,0,0,0,1],
                    [1,0,1,0,1,1,1,0,1,0,1,1,1,0,1],
                    [1,0,0,0,1,3,1,0,0,0,1,2,1,0,1],
                    [1,1,1,0,1,0,1,1,1,0,1,0,1,0,1],
                    [1,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                ],
                "image_fond": "feu.jpg"
            }
        }

    def broadcast_salle(self, nom_salle, message):
        if nom_salle in self.salles:
            msg_encoded = json.dumps(message).encode('utf-8')
            for conn in self.salles[nom_salle]["joueurs"]:
                try: conn.send(msg_encoded)
                except: pass

    def verifier_mouvement(self, salle_info, j_id, direction):
        """Logique serveur pour valider le déplacement et les conséquences"""
        pos = salle_info["etat_joueurs"][j_id]["pos"]
        grille = salle_info["data"]["grid"]
        
        y, x = pos[0], pos[1]
        if direction == "up": y -= 1
        elif direction == "down": y += 1
        elif direction == "left": x -= 1
        elif direction == "right": x += 1
        
        # 1. Vérifier les limites et les murs
        if 0 <= y < len(grille) and 0 <= x < len(grille[0]):
            if grille[y][x] != 1: # Si ce n'est pas un mur
                salle_info["etat_joueurs"][j_id]["pos"] = [y, x]
                
                # 2. Vérifier si c'est une bombe (3)
                if grille[y][x] == 3:
                    salle_info["etat_joueurs"][j_id]["vies"] -= 1
                    if salle_info["etat_joueurs"][j_id]["vies"] <= 0:
                        # Reset si mort
                        salle_info["etat_joueurs"][j_id]["pos"] = [1, 1]
                        salle_info["etat_joueurs"][j_id]["vies"] = 3
                        return "mort"
                    return "bombe"
                
                # 3. Vérifier si c'est la sortie (2)
                if grille[y][x] == 2:
                    return "victoire"
                
                return "ok"
        return "mur"

    def handle_client(self, conn, addr):
        j_id = f"J_{addr[1]}" # ID unique basé sur le port
        nom_salle_actuelle = None

        while True:
            try:
                data = conn.recv(32768).decode('utf-8')
                if not data: break
                msg = json.loads(data)

                if msg["type"] == "creer_salle":
                    terrain_type = msg["terrain"]
                    nom_salle_actuelle = j_id
                    self.salles[nom_salle_actuelle] = {
                        "terrain": terrain_type, 
                        "joueurs": [conn],
                        "data": self.TERRAINS_DATA.get(terrain_type),
                        "etat_joueurs": {j_id: {"pos": [1, 1], "vies": 3, "nom": "Hôte"}},
                        "tour_actuel": j_id
                    }
                    conn.send(json.dumps({"type": "update_attente", "joueurs": ["Hôte"]}).encode('utf-8'))

                elif msg["type"] == "rejoindre_salle":
                    nom_salle_actuelle = msg["salle"]
                    if nom_salle_actuelle in self.salles:
                        self.salles[nom_salle_actuelle]["joueurs"].append(conn)
                        self.salles[nom_salle_actuelle]["etat_joueurs"][j_id] = {"pos": [1, 1], "vies": 3, "nom": f"Joueur {len(self.salles[nom_salle_actuelle]['joueurs'])}"}
                        noms = [v["nom"] for v in self.salles[nom_salle_actuelle]["etat_joueurs"].values()]
                        self.broadcast_salle(nom_salle_actuelle, {"type": "update_attente", "joueurs": noms})

                elif msg["type"] == "lancer_de":
                    if nom_salle_actuelle in self.salles:
                        score = random.randint(1, 6)
                        self.broadcast_salle(nom_salle_actuelle, {"type": "resultat_de", "valeur": score, "joueur": j_id})

                elif msg["type"] == "move":
                    if nom_salle_actuelle in self.salles:
                        res = self.verifier_mouvement(self.salles[nom_salle_actuelle], j_id, msg["dir"])
                        # On renvoie l'état complet à tout le monde pour synchroniser
                        self.broadcast_salle(nom_salle_actuelle, {
                            "type": "update_game",
                            "etat": self.salles[nom_salle_actuelle]["etat_joueurs"],
                            "dernier_evenement": res,
                            "id_action": j_id
                        })

                elif msg["type"] == "lancer_jeu":
                    if nom_salle_actuelle in self.salles:
                        salle_info = self.salles[nom_salle_actuelle]
                        self.broadcast_salle(nom_salle_actuelle, {
                            "type": "start_game",
                            "map": salle_info["data"]["grid"],
                            "image": salle_info["data"]["image_fond"],
                            "etat_initial": salle_info["etat_joueurs"],
                            "ma_salle": nom_salle_actuelle
                        })

            except: break
        
        # Nettoyage si déconnexion
        if nom_salle_actuelle in self.salles:
             if conn in self.salles[nom_salle_actuelle]["joueurs"]:
                 self.salles[nom_salle_actuelle]["joueurs"].remove(conn)
        conn.close()

    def start(self):
        print("SERVEUR LABYRINTHE PRO ACTIF...")
        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    LabyServeur().start()