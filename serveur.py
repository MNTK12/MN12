import socket
import threading

class LabyrintheServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = {}  # {socket: pseudo}
        print(f"[*] Serveur lancé sur {host}:{port}")

    def broadcast(self, message):
        """Envoie la liste des joueurs à tout le monde"""
        for client in self.clients:
            try:
                client.send(message.encode('utf-8'))
            except:
                continue

    def handle_client(self, client):
        while True:
            try:
                msg = client.recv(1024).decode('utf-8')
                if msg.startswith("NAME:"):
                    pseudo = msg.split(":")[1]
                    self.clients[client] = pseudo
                    # Envoyer la liste mise à jour : LIST:pseudo1,pseudo2...
                    liste_pseudos = "LIST:" + ",".join(self.clients.values())
                    self.broadcast(liste_pseudos)
            except:
                if client in self.clients:
                    print(f"[-] {self.clients[client]} déconnecté.")
                    del self.clients[client]
                client.close()
                self.broadcast("LIST:" + ",".join(self.clients.values()))
                break

    def run(self):
        while True:
            client, addr = self.server.accept()
            print(f"[+] Connexion de {addr}")
            threading.Thread(target=self.handle_client, args=(client,)).start()

if __name__ == "__main__":
    LabyrintheServer().run()