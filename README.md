notre projet porte sur un labirainthe ou les utilisateur peuvent se connecter:
sous le meme reseau l'un qui decide de cree la salle et les autres parte dans attendre puis une liste de salle cree leurs seras presenter
quite a eux de choisir avec qui jouer 

pour le lancement de l'application nous travaillons sur ubuntu donc la commande pour lancer l'environnement virtuelle qui regroupes toutes nos 
bibliotheque est : source mon_env/bin/active 
dans windows vous allez devoir supprimer cette environnement et relancer le telechargement de toute les biblitheque a savoir :

customtkinter : pour le designe de la platfomr c'est une version ameliorer de tkinter que nous avons utilisez dans le premier projet 
PIL : pour la gestion des images il nous a permis de mettre en arriere plan nos images pour mieux gerer le style de la platfomrs

pour la suite apres avoir intaller ces bibliotheque avec le pip install vous allez maintenant activer l'environnement virtuelle avec la commande : ./active (tacher a etre dans le dossier ./mon_env/Scrip/active) le dossier mon_env est cree avec python3 -m venv mon_env 

de par la suite nous avons ajouter 2 version le clienttest et le serveurtest qui est la version beta du projet ici c'est purement la connexion distant : le serveur utilise le protocole udp pour envoyer sont addresse de facon sequentielle et des que le client recois sont addresse il fait maitenant une connexion three hand shake TCP 
maintenant nous avons une version possible de lancer dans en local avec app.py et serveur.py qui est la version possible de lancer en local et verifier notre travaille
