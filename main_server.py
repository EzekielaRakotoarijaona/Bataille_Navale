#!/usr/bin/python3

from game import *
import  random
import time
import socket
import select
import pickle






""" generate a random valid configuration """
def randomConfiguration():
    boats = [];
    while not isValidConfiguration(boats):
        boats=[]
        for i in range(5):
            x = random.randint(1,10)
            y = random.randint(1,10)
            isHorizontal = random.randint(0,1) == 0
            boats = boats + [Boat(x,y,LENGTHS_REQUIRED[i],isHorizontal)]
    return boats

    

def displayConfiguration(boats, shots=[], showBoats=True):
    Matrix = [[" " for x in range(WIDTH+1)] for y in range(WIDTH+1)]
    for i  in range(1,WIDTH+1):
        Matrix[i][0] = chr(ord("A")+i-1)
        Matrix[0][i] = i

    if showBoats:
        for i in range(NB_BOATS):
            b = boats[i]
            (w,h) = boat2rec(b)
            for dx in range(w):
                for dy in range(h):
                    Matrix[b.x+dx][b.y+dy] = str(i)

    for (x,y,stike) in shots:
        if stike:
            Matrix[x][y] = "X"
        else:
            Matrix[x][y] = "O"


    for y in range(0, WIDTH+1):
        if y == 0:
            l = "  "
        else:
            l = str(y)
            if y < 10:
                l = l + " "
        for x in range(1,WIDTH+1):
            l = l + str(Matrix[x][y]) + " "
        print(l)

""" display the game viewer by the player"""
def displayGame(game, player):
    otherPlayer = (player+1)%2
    displayConfiguration(game.boats[player], game.shots[otherPlayer], showBoats=True)
    displayConfiguration([], game.shots[player], showBoats=False)



""" Play a new random shot """
def randomNewShot(shots):
    (x,y) = (random.randint(1,10), random.randint(1,10))
    while not isANewShot(x,y,shots):
        (x,y) = (random.randint(1,10), random.randint(1,10))
    return (x,y)

def main():
    
    boats1 = randomConfiguration()
    boats2 = randomConfiguration()
    game = Game(boats1, boats2)
    
    #création de socket TCP
    server = socket.socket(family = socket.AF_INET6, type = socket.SOCK_STREAM, proto = 0, fileno = None)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #Bind la socket au port 7777
    print("Lancement du serveur sur le port 7777")
    server.bind(('',7777))
    # "Ecoute" pour les demandes de connections entrantes
    server.listen(5)

 
    #Attente de connexion
    clients_connectes = []
    
    while True:
        # Attente d'une connexion
        print("Attente de joueurs ..")
        
        #On récupère les sockets disponibles en lecture
        connexions_demandees, wlist, xlist = select.select([server],[], [])
    
        for connexion in connexions_demandees:
            connexion_avec_client, infos_connexion = connexion.accept()
            # On ajoute la socket connecté à la liste des clients
            clients_connectes.append(connexion_avec_client)

        #Les premiers clients connectés sont les joueurs on leur renvoit les infos sur la table de jeux et leur numero de joueurs
        if len(clients_connectes) == 2:
            print(" %s joueur(s) connecté(s)" % len(clients_connectes))
            clients_connectes[0].send(str(0).encode('utf-8'))
            clients_connectes[1].send(str(1).encode('utf-8'))
            clients_connectes[0].send(str(game).encode('utf-8'))
            clients_connectes[1].send(str(game).encode('utf-8'))
            
            #Pour commencer on defini le joueur du serveur à 0 
            currentPlayer = 0
            
            
            while gameOver(game) == -1:        
                if (currentPlayer == J0):
                    #Si c'est le tour du joueur 0 on attend les coordonées qu il a joue et on les envoie au joueur 1
                    x = clients_connectes[0].recv(1)
                    y = clients_connectes[0].recv(1)
                    addShot(game, int(x), int(y), currentPlayer)
                    clients_connectes[1].send(x)
                    clients_connectes[1].send(y)
                    currentPlayer = (currentPlayer+1)%2
                else:
                    #Si c'est le tour du joueur 1 on attend les coordonées qu il a joue et on les envoie au joueur 0
                    x = clients_connectes[1].recv(1)
                    y = clients_connectes[1].recv(1)
                    addShot(game, int(x), int(y), currentPlayer)
                    clients_connectes[0].send(x)
                    clients_connectes[0].send(y)
                    currentPlayer = (currentPlayer+1)%2
            
            #Fin du jeu et fermeture des connexions
            for client in clients_connectes:
                client.close()
            server.close()
    
main()
