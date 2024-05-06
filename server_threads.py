import config
import threading
import socket, errno
import queue
from game import Command
import pickle
from user import User

#Establish I/O threads for each Client: send_loop, recv_loop

def send_loop(DEBUG, conn: socket.socket, userID, send_queue, recv_queue):
    send_lock = threading.Lock()   #Define the lock but do not activate yet
    while config.users[userID].connected:
        send_lock.acquire()
        #if send_queue.qsize()>0:
        if config.send_queues[userID].qsize()>0:
            print("Pulling from send_queue to send")
            if DEBUG: print("S", end='', flush=True)
            message = config.send_queues[userID].get()   #JOIN,Hello
            print(f"Sending: {message.userID}: {message.command}: {message.cmd_data}")
            try:
                conn.send(pickle.dumps(message))
            except socket.error as e:
                print(e)
                #Need to handle what do do about socket failure!
                #Consider retry, restart, or delete all and let client re-join...
            except:
                #Could pass notification of lost connection to the SocketMgr
                break
            if message.command == "ACK":  
                if DEBUG: print("A", end='', flush=True)
            elif message.command == "HBT": 
                if DEBUG: print("H", end='', flush=True)
            else:
                if DEBUG: print("C", end='', flush=True)
            if DEBUG: print(str(send_queue.qsize()), end='', flush=True)
            message = ""
            if DEBUG: print("s\n", end='', flush=True)  
        send_lock.release()
    print(f"Exiting {userID} send_loop thread")
    config.users[userID].connected == False


def recv_loop(DEBUG, conn: socket.socket, userID, send_queue, recv_queue):
    recv_lock =  threading.Lock()  #Define the lock but do not activate yet
    while config.users[userID].connected:  
        try:
            message = pickle.loads(conn.recv(4096))  #Get any inbound messages
        except socket.error as e:
            print(e)

            print("Socket error in recv_loop")
            config.users[userID].connected = False
            message = ""
            break
        except:
            config.users[userID].connected = False
            try:
                config.users[userID].connected = False
            except:
                pass
            message  = ""
            break
        if message != "":
            if DEBUG: print("R", end='', flush=True)
            recv_lock.acquire()
            if type(message) == Command:
                #Handle 3 sets of msgs; HBT = reply here, ACK = chk off list, All Else = pass to server 
                print(f"Receiving: {str(message.command)}: {message.cmd_data}")
                if message.command == "HBT": #handle HBT right here; no need to queue it up 
                    send_queue.put(Command(userID, "ACK", "HBT received"))
                    if DEBUG: print("H", end='', flush=True)
                elif message.command == "ACK": #Check-off the original Cmd was ACK'd
                    #Implement msg numbering and ability to match an ACK back for eash sent msg
                    if DEBUG: print("A", end='', flush=True)
                else:
                    print(f"Pushing {message.command} from {message.userID} to recv_queue")
                    recv_queue.put(message) #Then push onto the Server's recv_queue to process
                    print(f"recv_queue length is now {recv_queue.qsize()}")
                    if DEBUG: print("C", end='', flush=True)
            else: 
                if DEBUG: print("! ", end='', flush=True)
                print(f"Badly formatted command from client {userID}")
                #Let the Connection Mgr do the removal of players.
            if DEBUG: 
                print(str(recv_queue.qsize()), end='', flush=True)
                print("r\n", end='', flush=True)
            recv_lock.release()
        message = ""
    print(f"Exiting {userID} recv_loop thread")
    config.users[userID].connected == False

#Not sure I will use this remove_player function any longer
def remove_player(DEBUG, user):
    for u in config.users:
        i = config.users.index(u)
        if config.users[i] == user:
            #users.remove(u)
            config.users.pop(i)
            config.send_queues.pop(i)
            if DEBUG: print("User found and removed")
    
    print(f"Removing user: {user.userID}")
    print("Active Players:")
    if len(config.users)>0:
        for u in config.users:
            i = config.users.index(u)
            print(f"   {u.name} - {config.send_queues[i][0]} {config.send_queues[i][3][0]}:{config.send_queues[i][3][1]}")
            #print(f"   {u.name} - {config.send_queues[i][0]} {config.send_queues[i][3][0]}:{config.send_queues[i][3][1]}  {recv_thread.name} {send_thread.name}")
    else:
            print(f"   none")
    print("Active Threads:")
    for t in threading.enumerate():
        print(f"   {t.name}")
