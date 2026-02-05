notre projet porte sur un labirainthe ou les utilisateur peuvent se connecter en mode TCP:
sous le meme reseau l'un qui decide de cree la salle et les autres parte dans la salle d'attente puis une liste de salle creee leurs seras presenter
le joueur a clique sur rejoindre une salle auras donc a choisir avec qui jouer 

pour le lancement de l'application nous travaillons sur ubuntu donc la commande pour lancer l'environnement virtuelle qui regroupes toutes nos 
bibliotheque est : source mon_env/bin/active 
dans windows vous allez devoir supprimer cette environnement et relancer le telechargement de toute les biblitheque a savoir :

customtkinter : pour le designe de la platfomr c'est une version ameliorer de tkinter que nous avons utilisez dans le premier projet 
PIL : pour la gestion des images il nous a permis de mettre en arriere plan nos images pour mieux gerer le style de la platfomrs

pour la suite apres avoir intaller ces bibliotheque avec le pip install. Vous allez maintenant activer l'environnement virtuelle avec la commande : ./active (tachez a etre dans le dossier ./mon_env/Scrip/active) le dossier mon_env est cree avec python3 -m venv mon_env 

de par la suite nous avons ajouter 2 version le clienttest et le serveurtest qui est la version en développement qui a eu a nous bloquer lors de la présentation 😥 du projet. Ici on utilise le protocole TCP et UDP: le serveur utilise le protocole udp pour envoyer sont addresse de facon sequentielle en broadcaste et des que le client recois sont addresse il fait maitenant une connexion three hand shake TCP.
Maintenant nous avons une version complète en TCP. Ici lors de la sélection de son avatar utilisateurs doit encore renseignés address du serveur avant maintenant de commencer le jeux 
