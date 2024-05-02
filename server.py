import config
import socket
#from _thread import *
import threading
import pickle
import queue
import time
from user import User
from game import Game, Command
from server_threads import send_loop, recv_loop


send_queue = queue.Queue()
recv_queue = queue.Queue()
send_lock = threading.Lock()
recv_lock = threading.Lock()
proc_lock = threading.Lock()

def socket_mgr():
    global users, send_queue, recv_queue, ack_queue, send_queues

    #Listen/wait for Socket connections
    server = "localhost"
    port = 5556
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((server, port))
    except socket.error as e:
        str(e)
    s.listen(5)
    print("Listening for connections, Server Started")
    total_conns = 0
    while True:  
        conn, addr = s.accept()  #Blocking wait for user to connect via Socket
        total_conns += 1
        print("Connecting a user...")
        user = User()  #Server creates a user object
        config.users.append(user)  #Add user to list of users
        config.users[len(config.users)-1].name = "Player " + str(total_conns)  #Name the user
        unique_send_queue = queue.Queue()
        config.send_queues.append((user.userID, unique_send_queue, conn, addr))

        print("send_loop and recv_loop threads started for: " + user.name)
        recv_thread = threading.Thread(target=recv_loop, args=(conn, user, unique_send_queue, recv_queue), daemon=True).start()
        send_thread = threading.Thread(target=send_loop, args=(conn, user, unique_send_queue, recv_queue), daemon=True).start()

        unique_send_queue.put(Command(user.userID, "ACK", "Welcome to Conq!"))

        print("Active Players:")
        for u in config.users:
            i = config.users.index(u)
            print(f"   {u.name} - {config.send_queues[i][0]} {config.send_queues[i][3][0]}:{config.send_queues[i][3][1]}")

def process_queues():
    #Data in a queue feels 'pre-certified' as okay to process without more checks
    proc_lock =  threading.Lock()
    proc_lock.acquire()
    #print(str(recv_queue.qsize()), end='', flush=True)
    print(".", end='', flush=True)
    if recv_queue.qsize()>0:
        pop_cmd = recv_queue.get()
        # if type(pop_cmd) == Command:  #Validate msg is well formed
        #     send_queue.put(Command(pop_cmd.userID, "ACK", "Command " + pop_cmd.command + " received"))  #Or use the Send Queue to send the command...
        #     #*** Additional processing of CMD messages & Gameplay ***
        # else:
        #     print("!recv_q", end='', flush=True)
        pop_cmd = ""
        print("r", end='', flush=True)
    proc_lock.release()

#Start a thread to send and receive Socket messages
#socketmgr_thread = threading.Thread(target=socket_mgr, args=(send_queue, recv_queue, ack_queue), daemon=True).start() #args=(netconn,), 
socketmgr_thread = threading.Thread(target=socket_mgr, args=(), daemon=True).start() 

while True:
    #All gameplay will happen here
    time.sleep(1)

    #process queues here!!
    process_queues()


    #Test out sending messages to users
    #1:1 and 1:Many
    #Typ format = conn.send(pickle.dumps(Command(user.userID, "ACK", "Welcome to Conq!")))
    #But here ^^ conn is not known at the Server, only SockerMgr
    #Need to lookup conn based on send_queues[]
