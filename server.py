import socket
from _thread import *
import pickle
from user import User
from game import Game, Command

server = "localhost"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(5)
print("Waiting for a connection, Server Started")

#connected = set()
users = []

def threaded_client(user, conn):
    conn.send(pickle.dumps(Command(user.userID, "ACK", "Welcome to the game!")))
    #conn.send(pickle.dumps(Command(user.userID, "USER", user)))
    print(f"User_Thread established for {user.userID}")

    while True:
        try:
            data = pickle.loads(conn.recv(4096))
            if not data:
                print(f"User connection failed for {user.userID}")
                break
            else:
                print(data)
                if data == type(Command):
                    if data.command == "USER":
                        conn.send(pickle.dumps(Command(user.userID, "USER", user)))
                    if data.command == "HBT":
                        conn.send(pickle.dumps(Command(user.userID, "ACK", "Received HBT")))
                        print("Sent HBT ACK")
        except:
            break
    print("Lost connection")
    #Remove User and close down the connection
    try:
        del users[user]
        print(f"Deleting user {user}")   #Might want to mark them as inactive, instead
    except:
        pass
    conn.close()

while True:
    conn, addr = s.accept()  #someone connects via Socket
    user = User()  #server creates a user object
    print(f"{addr} connected as {user.userID}")
    start_new_thread(threaded_client, (user, conn))   #Create User Thread, passing user object to it
