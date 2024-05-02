import socket
import threading
from game import Command
import time
import pickle

def send_loop(n, send_queue, recv_queue):
    send_lock = threading.Lock()
    print("Client send_loop Thread started")  #All Client processing happens within this loop   
    while True:
        send_lock.acquire()
        if send_queue.qsize()>0:
            message = send_queue.get()
            n.send(message)
            print(f"Sending: {str(message.command)}: {message.cmd_data}")
            #To aid in debugging...
            #Actually this detail for gameplay should be somewhere else...
            print("S", end='', flush=True)
            if message.command == "ACK":  #Ack'd a Server's command
                print("K", end='', flush=True)
            elif message.command == "HBT":  
                print("H", end='', flush=True)
            elif message.command == "JOIN":  
                print("J", end='', flush=True)
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
            print(str(recv_queue.qsize()), end='', flush=True)
            print("s\n", end='', flush=True)
            message = ""
        send_lock.release()

def recv_loop(n, send_queue, recv_queue):
    recv_lock = threading.Lock()
    print("Client receive_loop Thread started")
    while True:
        message = n.socket_recv()  #Get any inbound messages
        recv_lock.acquire()
        if type(message) == Command:  #Confirm whether msg is properly formed
            print(f"Receiving: {str(message.command)}: {message.cmd_data}")
            print("R", end='', flush=True)
            if message.command == "ACK": #send_queue will be waiting for this (what's that mean?)
                #ack_queue.put(message)
                pass
            else:
                recv_queue.put(message) #Then push onto the incoming queue for processing
                print("C", end='', flush=True)
        else:  #Else abandon the bad incoming message
            print("R", end='', flush=True)
            print("!", end='', flush=True)
        print(str(send_queue.qsize()), end='', flush=True)
        print(str(recv_queue.qsize()), end='', flush=True)
        message = ""
        print("r\n", end='', flush=True)
        recv_lock.release()


