import pickle
import socket
import threading
from player import *
import network
import time

current_player = 1
host_connected = 1

players = []

def define_players():
    global players

    players = [Player(), PlayerMulti()]

def threaded_client(conn,):
    conn.send(pickle.dumps(players[1].position))

    reply = ""
    connected = True

    while connected and host_connected:
        try:
            data = pickle.loads(conn.recv(2048))
        except:
            ("can't receive conn data")
        else:
            if not data:
                connected = False
            else:
                players[1].position, players[1].true_angle, players[1].shooting = data[0], data[1], data[2]

                reply = [players[0].position, players[0].weapon.angle, players[0].map_manager.current_map, players[0].shooting]

                players[0].shooting = False #assure que l'information d'un tir n'est reçue q'une fois

                conn.send(pickle.dumps(reply))
        
    print("deconexion")
    conn.close()

    global current_player
    current_player -= 1

def handle_conn(soc, listening):
    global current_player

    conn, adr = soc.accept()
    print(f"connected to {adr}")

    thread_cli = threading.Thread(target=threaded_client, args=(conn,))
    thread_cli.daemon = True
    thread_cli.start()
    current_player += 1
    listening[0] = 0

def main():
    global current_player

    ip = socket.gethostbyname(socket.gethostname() + ".local")
    port = network.port
    serv = (ip, port)

    s = network.soc

    try:
        s.bind(serv)
    except:
        print ("impossible de lier le serveur a son adresse")

    s.listen(2)
    print(f"waiting for connection on {serv}")

    listening = [0]

    while current_player != 0:
        # print(current_player)

        time.sleep(1)

        # permet à l'invité de se reconnecter
        if current_player != 2 and not listening[0]:
            listening[0] = 1
            th_reconn = threading.Thread(target=handle_conn,args=(s, listening))
            th_reconn.daemon = True
            th_reconn.start()

    print("Joueurs deconnectes")

    s.close()