import socket
import threading
from game import Command
import time
import pickle

def send_loop(n, send_queue, recv_queue, ack_queue):
    send_lock = threading.Lock()

    print("Client Send Thread Started")  #All Client processing happens within this loop   
    RTS = True  #Ready To Send - Prior ACKs received & *Socket healthy*
    while True:
        send_lock.acquire()
        if RTS and send_queue.qsize()>0:
            print("\nS", end='', flush=True)
            #print(str(send_queue.qsize()), end='', flush=True)
            message = send_queue.get()
            if type(message) == Command:  #Validate msg is well formed
                n.send(message)
                if message.command == "ACK":  #Ack'd a Server's command
                    print("A", end='', flush=True)
                elif message.command == "HBT":  
                    print("H", end='', flush=True)
                if message.command == "USER":  
                    print("U", end='', flush=True)
                elif message.command == "NAME":  
                    print("N", end='', flush=True)
                else:
                    print("C", end='', flush=True)  
            else:  #Else abandon the bad outgoing message
                print("!", end='', flush=True)
            print(str(send_queue.qsize()), end='', flush=True)
            print(str(ack_queue.qsize()), end='', flush=True)
            print(str(recv_queue.qsize()), end='', flush=True)
            message = ""
            print("s\n", end='', flush=True)
        send_lock.release()

def recv_loop(n, send_queue, recv_queue, ack_queue):
    recv_lock = threading.Lock()
    proc_lock = threading.Lock()

    print("Client Receive Thread Started")
    while True:
        message = n.socket_recv()  #Get any inbound messages
        print("\nR", end='', flush=True)
        recv_lock.acquire()
        if type(message) == Command:  #Confirm whether msg is properly formed
            if message.command == "ACK": #send_queue will be waiting for  this
                ack_queue.put(message)
                print("A", end='', flush=True)
            elif message.command == "USER":
                recv_queue.put(message)
                print("U", end='', flush=True)
                #print(f"{message.cmd_data} {message.cmd_data.userID}")  
            else:
                recv_queue.put(message) #Then push onto the incoming queue
                print("C", end='', flush=True)
        else:  #Else abandon the bad incoming message
            print("!", end='', flush=True)
        print(str(send_queue.qsize()), end='', flush=True)
        print(str(ack_queue.qsize()), end='', flush=True)
        print(str(recv_queue.qsize()), end='', flush=True)
        message = ""
        print("r\n", end='', flush=True)
        recv_lock.release()


