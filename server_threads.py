import config
import threading
import socket
import queue
from game import Command
import pickle
from user import User

#Establish 2 I/O threads for each Client: send_loop, recv_loop

def send_loop(conn: socket.socket, user, send_queue, recv_queue):
    send_lock = threading.Lock()   #Define the lock but do not activate yet
    while True:
        send_lock.acquire()
        if send_queue.qsize()>0:
            print("S", end='', flush=True)
            message = send_queue.get()
            try:
                conn.send(pickle.dumps(message))
            except socket.error as e:
                print(e)
                #Need to handle what do do about socket failure!
                #Consider retry, restart, or delete all and let client re-join...
            if message.command == "ACK":  
                print("A", end='', flush=True)
            elif message.command == "HBT": 
                print("H", end='', flush=True)
            else:
                print("C", end='', flush=True)
            print(str(send_queue.qsize()), end='', flush=True)
            message = ""
            print("s\n", end='', flush=True)  
        send_lock.release()

def recv_loop(conn: socket.socket, user, send_queue, recv_queue):
    recv_lock =  threading.Lock()  #Define the lock but do not activate yet
    while True:
        try:
            message = pickle.loads(conn.recv(4096))  #Get any inbound messages
        except: #socket.error as e:
            #print(e)
            print("Socket error in recv_loop")
        print("R", end='', flush=True)
        recv_lock.acquire()
        if type(message) == Command:
            #Handle 3 sets of msgs; HBT = reply here, ACK = chk off list, All Else = pass to server 
            if message.command == "HBT": #handle HBT right here; no need to queue it up 
                send_queue.put(Command(user.userID, "ACK", "HBT received"))
                print("H", end='', flush=True)
            elif message.command == "ACK": #Check-off the original Cmd was ACK'd
                #Implement msg numbering and ability to match an ACK back for eash sent msg
                print("A", end='', flush=True)
            else:
                recv_queue.put(message) #Then push onto the Server's recv_queue to process
                print("C", end='', flush=True)
        else: 
            print("! ", end='', flush=True)
            remove_player(user) 
            #TODO Need to close the SOCKET and Turn off the client THREADs!
            break  #Exit this While True loop; 
                    #closes the Socket for this specific Client - where??
                    #How to close the send_loop thread as well???              
        print(str(recv_queue.qsize()), end='', flush=True)
        print("r\n", end='', flush=True)
        message = ""
        recv_lock.release()

def remove_player(user):
    print(f"Removing user: {user.name}")
    for u in config.users:
        i = config.users.index(u)
        if config.users[i] == user:
            #users.remove(u)
            config.users.pop(i)
            config.send_queues.pop(i)
            print("User found and removed")
    print("Active Players:")
    for u in config.users:
        i = config.users.index(u)
        print(f"   {u.name} - {config.send_queues[i][0]} {config.send_queues[i][3][0]}:{config.send_queues[i][3][1]}")
