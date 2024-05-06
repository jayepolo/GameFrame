import socket
import threading
from game import Command
import time
import pickle
import queue

def send_loop(DEBUG, n, send_queue, recv_queue):
    send_lock = threading.Lock()
    print("Client send_loop Thread started")  #All Client processing happens within this loop   
    while True:
        send_lock.acquire()
        if send_queue.qsize()>0:
            message = send_queue.get()
            n.send(message)
            if DEBUG: print(f"Sending: {str(message.command)}: {message.cmd_data}")
            #To aid in debugging...
            #Actually this detail for gameplay should be somewhere else...
            if DEBUG: print("S", end='', flush=True)
            if message.command == "ACK":  #Ack'd a Server's command
                if DEBUG: print("K", end='', flush=True)
            elif message.command == "HBT":  
                if DEBUG: print("H", end='', flush=True)
            elif message.command == "JOIN":  
                if DEBUG: print("J", end='', flush=True)
            elif message.command == "NAME":  
                if DEBUG: print("N", end='', flush=True)
            elif message.command == "PLACE":  
                if DEBUG: print("P", end='', flush=True)
            elif message.command == "ATTACK":  
                if DEBUG: print("A", end='', flush=True)
            elif message.command == "MOVE":  
                if DEBUG: print("M", end='', flush=True)
            else:
                if DEBUG: print("C", end='', flush=True)
            if DEBUG: 
                print(str(send_queue.qsize()), end='', flush=True)
                print(str(recv_queue.qsize()), end='', flush=True)
                print("s\n", end='', flush=True)
            message = ""
        send_lock.release()

def recv_loop(DEBUG, n, send_queue, recv_queue):
    recv_lock = threading.Lock()
    print("Client receive_loop Thread started")
    while True:
        try:
            message = pickle.loads(n.client.recv(4096))  #Get any inbound messages
            #data = pickle.loads(self.client.recv(2048))  #Receive ACK from Server
        except socket.error as e:
            print(e)
            print("Socket error in recv_loop")
            #Consider adding: user.connected = False
            message = ""
            break
        except:
            print("Exception in recv_loop")
            #Agail consider: user.connected = False
            message  = ""
            break

        recv_lock.acquire()
        if type(message) == Command:  #Confirm whether msg is properly formed
            print(f"Receiving: {str(message.command)}: {message.cmd_data}")
            if DEBUG: print("R", end='', flush=True)
            if message.command == "ACK": #send_queue will be waiting for this (what's that mean?)
                #ack_queue.put(message)  #Not really needed??!
                pass
            else:
                print(f"Putting {message.command} command onto recv_queue")
                recv_queue.put(message) #Then push onto the incoming queue for processing
                if DEBUG: print("C", end='', flush=True)
        else:  #Else abandon the bad incoming message
            print(f"Bad Message: {str(message)}")
            if DEBUG: 
                print("R", end='', flush=True)
                print("!", end='', flush=True)
        if DEBUG: 
            print(str(send_queue.qsize()), end='', flush=True)
            print(str(recv_queue.qsize()), end='', flush=True)
            print("r\n", end='', flush=True)
        message = ""            
        recv_lock.release()


