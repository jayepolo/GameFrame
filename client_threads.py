import socket
import threading
from game import Command
import time
import pickle

def send_loop(n, send_queue, recv_queue, ack_queue):
    send_lock = threading.Lock()

    print("Client send_loop Thread started")  #All Client processing happens within this loop   
    RTS = True  #Ready To Send
    while True:
        send_lock.acquire()
        if RTS and send_queue.qsize()>0:
            print("\nS", end='', flush=True)
            #print(str(send_queue.qsize()), end='', flush=True)
            message = send_queue.get()
            if type(message) == Command:  #Validate msg is well formed
                n.send(message)
                print(f"\n{str(message.command)}: {message.cmd_data}")
                if message.command == "ACK":  #Ack'd a Server's command
                    print("K", end='', flush=True)
                elif message.command == "HBT":  
                    print("H", end='', flush=True)
                elif message.command == "NAME":  
                    print("N", end='', flush=True)
                elif message.command == "PLACE":  
                    print("P", end='', flush=True)
                elif message.command == "ATTACK":  
                    print("A", end='', flush=True)
                elif message.command == "MOVE":  
                    print("M", end='', flush=True)
                else:
                    print("C", end='', flush=True)  
                print(str(send_queue.qsize()), end='', flush=True)
                print(str(ack_queue.qsize()), end='', flush=True)
                print(str(recv_queue.qsize()), end='', flush=True)
                print("s\n", end='', flush=True)
                #print("Command: " + message.command +"\n", end='', flush=True)
            else:  #Else abandon the bad outgoing message
                print("!", end='', flush=True)
                print("s\n", end='', flush=True)
            message = ""
        send_lock.release()

def recv_loop(n, send_queue, recv_queue, ack_queue):
    recv_lock = threading.Lock()
    proc_lock = threading.Lock()

    print("Client receive_loop Thread started")
    while True:
        message = n.socket_recv()  #Get any inbound messages
        print("\nR", end='', flush=True)
        recv_lock.acquire()
        if type(message) == Command:  #Confirm whether msg is properly formed
            if message.command == "ACK": #send_queue will be waiting for this (what's that mean?)
                ack_queue.put(message)
                print(str(message.command), end='', flush=True)
            else:
                recv_queue.put(message) #Then push onto the incoming queue for processing
                print("C", end='', flush=True)
        else:  #Else abandon the bad incoming message
            print("!", end='', flush=True)
        print(str(send_queue.qsize()), end='', flush=True)
        print(str(ack_queue.qsize()), end='', flush=True)
        print(str(recv_queue.qsize()), end='', flush=True)
        message = ""
        print("r\n", end='', flush=True)
        recv_lock.release()


