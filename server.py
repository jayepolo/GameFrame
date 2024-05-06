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

DEBUG=False

send_queue = queue.Queue()  # Each client has a dedicated queue for sending out comms
recv_queue = queue.Queue()  # Recv queue is shared by all clients
#admin_queue = queue.Queue()
send_lock = threading.Lock()
recv_lock = threading.Lock()
#admin_lock = threading.Lock()

def socket_mgr():
    global users, send_queue, recv_queue, ack_queue, send_queues, kill_threads

    #Listen/wait for Socket connections
    server = "localhost"
    port = 5556
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Attempting to bind Socket to server port...")
    while True:
        try:
            s.bind((server, port))
            break
        except socket.error as e:
            print(".", end='', flush=True)
            #str(e)
            #print("Socket not created properly")
        #Need to RETRY here ^^ - do not advance without the Server/Port functioning

        #Example solution to wait for a port:
            # start_time = time.perf_counter()
            # while True:
            #     try:
            #         with socket.create_connection((host, port), timeout=timeout):
            #             break
            #     except OSError as ex:
            #         time.sleep(0.01)
            #         if time.perf_counter() - start_time >= timeout:
            #             raise TimeoutError('Waited too long for the port {} on host {} to start accepting '
            #                             'connections.'.format(port, host)) from ex
    s.listen(5)
    print("Socket_mgr started - listening for connections")
    total_conns = 0
    while True:  
        conn, addr = s.accept()  #Blocking wait for user to connect via Socket
        if DEBUG: print("Connecting...")
        total_conns += 1
        user = User()  #Server creates a user object

        config.users[user.userID] = user  #Add new user to the Dictionary
        config.users[user.userID].name = "Player_" + str(total_conns)  #Name the user
        config.users[user.userID].connected = True  #Enable comms with this user
        
        config.send_queues[user.userID] = queue.Queue() #Add new queue to send_queues Dictionary

        if DEBUG: print("Starting send_loop and recv_loop threads for: " + user.name)
        recv_thread = threading.Thread(name=str(user.userID)+"_recv", target=recv_loop, args=(DEBUG, conn, user.userID, config.send_queues[user.userID], recv_queue), daemon=True).start()
        send_thread = threading.Thread(name=str(user.userID)+"_send", target=send_loop, args=(DEBUG, conn, user.userID, config.send_queues[user.userID], recv_queue), daemon=True).start()

        #Welcome the new user
        config.send_queues[user.userID].put(Command(user.userID, "ACK", "Welcome to Conq!"))
        config.send_queues[user.userID].put(Command(user.userID, "USER", user))

        print(f"New user: {user.userID}")
        print("Active Players:")
        for u in config.users.keys():
            if config.users[u].connected == True:
                print(f"   {config.users[u].name} - {config.users[u].userID}") 
        if DEBUG:
            print("Active Threads:")
            for t in threading.enumerate():
                print(f"   {t.name}")

def process_queues():
    global users, send_queues, recv_queue
    #Data format of a Command in a queue is confirmed to be of type==Command
    #print(str(recv_queue.qsize()), end='', flush=True)
    proc_lock =  threading.Lock()
    while True:
        proc_lock.acquire()
        #print(f"recv_queue length is now {recv_queue.qsize()}")
        if recv_queue.qsize()>0:
            pop_cmd = recv_queue.get()
            print("Pulling from recv_queue to process")
            send_queue.put(Command(pop_cmd.userID, "ACK", "Command " + pop_cmd.command + " received"))
            if pop_cmd.command == "USER":
                tmp_user = pop_cmd.cmd_data  
                tmp_user.name = tmp_user.name + "_updated"
                print(f"Pushing USER from {tmp_user.userID} to send_queue for user: {tmp_user.name}")
                config.send_queues[tmp_user.userID].put(Command(tmp_user.userID, "USER", tmp_user))  #Add to the send queue
            elif pop_cmd.command == "JOIN":
                config.send_queues[pop_cmd.userID].put(Command(pop_cmd.userID, "ACK", "Still building..."))  #Add to the send queue
            pop_cmd = ""
            if DEBUG: print("r", end='', flush=True)
        proc_lock.release()

def cli_loop():
    global users, send_queue, recv_queue

    print("Client cli_loop Thread started")  #Manually execute commands using command line input
    while True:
        try:
            get_cmd, get_cmd_data = input("Enter <command>,<cmd_data>: ").split(",")
            print(f"cmd: {get_cmd} cmd_data: {get_cmd_data}")
            for u in config.users.keys():
                print(f"Sending: user:{u} cmd:{get_cmd} cmd_data:{get_cmd_data}")
                config.send_queues[u].put(Command(config.users[u].userID, get_cmd, get_cmd_data))
        except:
            print("Invalid entry")

#Start a thread to send and receive Socket messages
#socketmgr_thread = threading.Thread(target=socket_mgr, args=(send_queue, recv_queue, ack_queue), daemon=True).start() #args=(netconn,), 
print("Starting up SocketMgr and ProcessQueues threads")
socketmgr_thread = threading.Thread(name="SocketMgr", target=socket_mgr, args=(), daemon=True).start() 
process_thread = threading.Thread(name="ProcessQueues", target=process_queues, args=(), daemon=True).start() 
print("Active Threads:")
for t in threading.enumerate():
    print(f"   {t.name}")



#Create a thread to handle manual entry user input at command line
cli_thread = threading.Thread(name="CLI", target=cli_loop, args=(), daemon=True).start() #args=(netconn,), 
print("Active Threads:")
for t in threading.enumerate():
    print(f"   {t.name}")

while True:
    #All gameplay will happen here
    time.sleep(5)
    if True:
        print("Active Players:")
        num = 0
        for u in config.users.keys():
            if config.users[u].connected == True:
                print(f"   {config.users[u].name} - {config.users[u].userID}")
                num += 1
        if num == 0:
            print("   none")
        print("Active Threads:")
        for t in threading.enumerate():
            print(f"   {t.name}")


    # Test the process of SENDING messages to users
    # Both 1:1 and 1:Many
    # Typ format = conn.send(pickle.dumps(Command(user.userID, "ACK", "Welcome to Conq!")))
    # But here ^^ conn is not known at the Server, only SockerMgr
    # Need to lookup conn based on send_queues[]
