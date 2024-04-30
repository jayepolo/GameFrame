import socket
from _thread import *
import pickle
from user import User
from game import Game, Command

server = "localhost"
port = 5556

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(5)
print("Waiting for connections, Server Started")

#connected = set()
users = []

def threaded_client(user, conn):
    conn.send(pickle.dumps(Command(user.userID, "ACK", "Welcome to Conq!")))
    print(f"threaded_client established for {user.name}")

    while True:
        try:
            #Continually check for data from client and handle accordingly:
            data = pickle.loads(conn.recv(4096))
            if not data:
                print(f"User connection failed for {user.name}")
                break
            else:
                if type(data) == Command:
                    if data.command == "HBT":
                        conn.send(pickle.dumps(Command(user.userID, "ACK", "Server acks the HBT")))
                        print("Sent HBT ACK")
                    if data.command == "JOIN":
                        #Add user to active players?  
                        #Already managing connection based userID list
                        #So just reply ACK without doing more
                        conn.send(pickle.dumps(Command(user.userID, "ACK", "JOIN: You have joined the game")))
                        #Also update uuid and send back a USER command to user
                        conn.send(pickle.dumps(Command(user.userID, "USER", user)))
                    if data.command == "USER":
                        conn.send(pickle.dumps(Command(user.userID, "USER", user)))
        except:
            #If socket lost, bail on this threaded_client connection entirely
            break
    print("Lost connection")
    #Remove User and close down the connection
    try:
        print(f"Deleting user {user.name}")   #Might want to mark them as inactive, instead
        users.remove(user)
        for u in users:
            print(f"   {u.name}")
    except:
        print("Deleting User Exception!")
        pass
    conn.close()

while True:  #Listen for connections BLOCKING => cannot run gameplay here | Spin up Connection_Manager thread
    print("Listening...")  
    conn, addr = s.accept()  #someone connects via Socket
    print("Connecting...")
    user = User()  #server creates a user object
    users.append(user)
    users[len(users)-1].name = "Player " + str(len(users))
    #print(f"User {user.userID} created as {user.name}")
    print("Active Players:")
    for u in users:
        print(f"   {u.name}")
    start_new_thread(threaded_client, (user, conn))   #Create User Thread, passing user object to it
