import socket
import threading
from game import Command
import time
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5556
        self.addr = (self.server, self.port)
        #self.server_obj = self.connect()
        #self.user = self.connect()
        self.connect()

    def connect(self):
        try:
            print(f"Connecting to Server {self.addr}")
            self.client.connect(self.addr)  #Establish Socket connection to Server
            print("Connected")
            data = pickle.loads(self.client.recv(2048))  #Receive ACK from Server
            print(f"{data.command}: {data.cmd_data}") 

            #Passively waiting for server to send a user object.  
            #Switch this to actively hanlde user request?
            #Exist this connection routine
            #Then back in the client setup code, Send a User Command to Server asking for user object object?
            #Means I will not get the Server assigned user.name, unless of course I do not update it
            
            #user_cmd = pickle.loads(self.client.recv(2048))  #Receive USER object from Server
            #user = user_cmd.cmd_data
            #print(f"{user_cmd.command} : {user_cmd.cmd_data}")
            #print(user.name)
            return #user
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

