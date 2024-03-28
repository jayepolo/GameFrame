import socket
import threading
from game import Command
import time
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.server_obj = self.connect()

    def connect(self):
        try:
            print("Connecting to Server")
            self.client.connect(self.addr)
            print("Connected")
            data = pickle.loads(self.client.recv(2048))  #Receive ACK from Server
            print(f"{data} {data.command}")  #Receive ACK from Server
            #return pickle.loads(self.client.recv(2048))  #Rceive USER object from Server
            return data
        except:
            print(f"Connection to Server failed")
            return False

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return  #Send function should not Recv data!
        except socket.error as e:
            print(e)

    def socket_recv(self):
        try:
            data = self.client.recv(2048)   #Wait for inbound msg
            if data != b'':
                message = pickle.loads(data)
                return message
            else:
                print("Connection broken; Goodbye")
        except socket.error as e:
            print(e)



def network_check(client, userID):
    global HBT_time
    global send_lock
    global send_queue
    print(".", end='', flush=True)
    print(userID)
    if time.time() >= HBT_time:
        hbt_cmd = Command(userID.userID, "HBT", "Ready to play")
        send_lock.acquire()
        send_queue.put(hbt_cmd)  #Or use the Send Queue to send the command...
        send_lock.release()
        HBT_time = time.time() + 5 #Pause 5 seconds until next heartbeat / This delay is blocking (bad)
        print(time.time(), HBT_time)

