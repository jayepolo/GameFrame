import config
import threading
from _thread import *
import socket
import queue
import pickle
from game import Command
from user import User
from server_threads import send_loop, recv_loop

#users = []

def socket_mgr():
    global users, send_queues, send_queue, recv_queue, ack_queue

    #Listen/wait for Socket connections
    server = "localhost"
    port = 5556
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((server, port))
    except socket.error as e:
        str(e)
    s.listen(5)
    print("Waiting for connections, Server Started")

    # def threaded_client(user, conn):
    #     # conn.send(pickle.dumps(Command(user.userID, "ACK", "Welcome to Conq!")))
    #     # print(f"threaded_client established for {user.name}")

    #     while True:
    #         try:
    #             #Continually check for data from client and handle accordingly:
    #             data = pickle.loads(conn.recv(4096))
    #             if not data:
    #                 print(f"User connection failed for {user.name}")
    #                 break
    #             else:
    #                 if type(data) == Command:
    #                     if data.command == "HBT":
    #                         conn.send(pickle.dumps(Command(user.userID, "ACK", "Server acks the HBT")))
    #                         print("Sent HBT ACK")
    #                     if data.command == "JOIN":
    #                         #Add user to active players?  
    #                         #Already managing connection based userID list
    #                         #So just reply ACK without doing more
    #                         conn.send(pickle.dumps(Command(user.userID, "ACK", "JOIN: You have joined the game")))
    #                         #Also update uuid and send back a USER command to user
    #                         conn.send(pickle.dumps(Command(user.userID, "USER", user)))
    #                     if data.command == "USER":
    #                         conn.send(pickle.dumps(Command(user.userID, "USER", user)))
    #         except:
    #             #If socket lost, bail on this threaded_client connection entirely
    #             break
    #     print("Lost connection")
    #     #Remove User and close down the connection
    #     try:
    #         print(f"Deleting user {user.name}")   #Might want to mark them as inactive, instead
    #         users.remove(user)
    #         for u in users:
    #             print(f"   {u.name}")
    #     except:
    #         print("Deleting User Exception!")
    #         pass
    #     conn.close()

    while True:  #Listen for Client Socket connections; Spin up Send/Recv threads for each Socket
        print("Listening...")  
        conn, addr = s.accept()  #Blocking wait for user to connect via Socket
        print(conn)
        print("Connecting a user...")
        user = User()  #Server creates a user object
        users.append(user)  #Add user to list of users
        users[len(users)-1].name = "Player " + str(len(users))  #Name the user
        print("Active Players:")
        for u in users:
            print(f"   {u.name}")
        unique_send_queue = queue.Queue()
        send_queues.append((user.userID, unique_send_queue, conn, addr))
        #This ^^ lsit of tuples can be searched using one of these methods:
            #my_queue = [i for i, v in enumerate(send_queues) if v[0] is my_user]  How to select only the queue?
            #Or this:  my_queue = dict(send_queues)[my_user]
            #And finally possibly this (which gives the list index, and value then needs to be broken):
            # try:
            #     res = test_list.index([t for t in test_list if t[N] == ele][0])
            # except IndexError:
            #     res = -1

        #This code was inside threaded_client, but moved out to here...
        #TODO:  Consider pushing this send command onto the Queue, instead...
        conn.send(pickle.dumps(Command(user.userID, "ACK", "Welcome to Conq!")))
        print(f"threaded_client established for {user.name}")

        #IMPORTANT - need to create a unique send_queue for each conn/user that is created
        #Save the unique send_queue here, in a list, and associated with the new user
        #But also pass that unique send_queue on the the new send_loop thread created
        #that way, each 1:1 send can be completed within the send loop
        #while 1:many sends can be orchestrated here, and distributed to each unique send_loop

        #The send_queue below, should not be the GLOBAL send_queue.  It should be a UNIQUE send_queue
        #start_new_thread(threaded_client, (user, conn))   #Create User Thread, passing user object to it
        recv_thread = threading.Thread(target=recv_loop, args=(conn, user, send_queue, recv_queue, ack_queue), daemon=True).start() #args=(netconn,), 
        send_thread = threading.Thread(target=send_loop, args=(conn, user, send_queue, recv_queue, ack_queue), daemon=True).start() #args=(netconn,), 

    # #Set up Server side Socket and set it to listen
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server = "localhost"
    # port = 5555
    # addr = (server, port)
    # try:
    #     sock.bind(addr)
    #     sock.listen(5)
    #     print("Server is listening on socket")
    # except:
    #     print("Failed to establish Server Socket")

    # #Allow Players to connect to the Server
    # while True:
    #     conn, address = sock.accept()     # Blocks, waiting for connection
    #     #There are many conn instances per Server!
    #     new_client_connection = New_Client_Connection(conn)
    #     new_player = Player(new_client_connection)  #Create a player linked to the Socket conn
    #     all_players.append(new_player)   #Do I really want to add Server to this???
    #     print(f"New connection from player ID: {new_player.id}")
        
    #     #Start threads to send/receive messages to one specific Client
    #     recv_thread = threading.Thread(target=recv_loop, args=(new_client_connection, new_player,), daemon=True).start() #args=(netconn,), 
    #     send_thread = threading.Thread(target=send_loop, args=(new_client_connection, new_player,), daemon=True).start() #args=(netconn,), 

    #     #Send and ACK indicating "Welcome to Conq" to the new_player
    #     ack_cmd = Command(new_player.id, "ACK", "Welcome to Conq!")
    #     print(f"Welcome new player {new_player.id}")
    #     textbox.insert("end", ("Welcome new player " + new_player.id + "\n"))
    #     send_lock.acquire()
    #     send_queue.put(ack_cmd)  #Or use the Send Queue to send the command...
    #     send_lock.release()

    #     update_players()
    #     print("\nAll Players:")
    #     for p in all_players:
    #         print("   Player" + ": " + p.id + " " + p.name)

    # #print(f"Connection closed to {player.conn}")
    # #textbox.insert("end", ("Connection closed to " + str(player.id) + "\n"))
    # #player.conn.close()