import pygame as pg
from network import Network
from network import Network, network_check
from game import Command
from user import User
from client_threads import send_loop, recv_loop
import threading
import queue
import time

version = "0.1"
width = 700
height = 700
win = pg.display.set_mode((width, height))
pg.display.set_caption("Client")

send_queue = queue.Queue()
recv_queue = queue.Queue()
ack_queue = queue.Queue()
lock = threading.Lock()
send_lock = threading.Lock()
recv_lock = threading.Lock()
proc_lock = threading.Lock()

def main():
    print(f"Starting GameFrame Client v{version}")
    run = True
    clock = pg.time.Clock()
    
    #Establish Server Socket connection
    #Currently this instantiates a User object.  
    #Probably should not couple that to Network connection?  TBD
    n = Network() # Establish connection to Server

    #Start thread to send and receive Socket messages
    recv_thread = threading.Thread(target=recv_loop, args=(n, send_queue, recv_queue, ack_queue), daemon=True).start() #args=(netconn,), 
    send_thread = threading.Thread(target=send_loop, args=(n, send_queue, recv_queue, ack_queue), daemon=True).start() #args=(netconn,), 

    user = User()  #Instantiate a generic user locally
    playing = False  #Server has accepted User to play
    print(f"Sending JOIN request to Server")
    print(f"{user.userID} join request")  #Request a formal User object from Server
    print("Queues: " + str(send_queue.qsize())+ str(ack_queue.qsize())+ str(recv_queue.qsize()))
    send_queue.put(Command(user.userID, "JOIN", user.userID + " join request"))  #Request a formal User object from Server

    #user = n.user #Save User object   

    #ISSUE!!  
    #This loop must be inside the While Run, so that the queues are being processed!!!
    #while not playing:
        #Loop here until the User has joined the Server's game
    #    time.sleep(0.5)
    #    print(playing)  #("o", end='', flush=True)

    #Contact our web support at  866-755-2680.  Anthem

    HBT_time = time.time() + 5
    print("Starting main() loop")  #All Client processing happens within this loop
    while run:  #Process certain game activities
        clock.tick(60)
        #game_events()
        
        #Check and process Queues 60 times per second
        process_queues()
        
        HBT_time = network_check(user, HBT_time)

        try:
            #game_udate()
            pass
        except:
            run = False   #Should enhance to have a "playing" state, vs this run state 
                            #Eg always 'run' but sometimes 'play' but bever bail out completely.
            print("Something failed!?")
            break

        #Execute various gameplay activities here, refreshing pygrame afterwards
        #pygame.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                pg.quit()

            if event.type == pg.MOUSEBUTTONDOWN:
                #check for mouse clicks on teh game GUI
                #and react accordingly
                pass

        #Refresh the gameplay GUI as needed
        #redrawWindow(win, game, player)
        pg.display.update()

#Try passing in user instead of just userID, so can update UI with user.name
def network_check(user, HBT_time):
    global send_lock
    global send_queue
    if time.time() >= HBT_time:
        hbt_cmd = Command(user.userID, "HBT", "Ready to play")
        send_lock.acquire()
        send_queue.put(hbt_cmd)  #Or use the Send Queue to send the command...
        send_lock.release()
        return HBT_time + 5
    else:
        return HBT_time        

def process_queues():
        global user, playing
        print(".", end='', flush=True)
        proc_lock.acquire()
        if ack_queue.qsize()>0:
            #print("\nP", end='', flush=True)
            #print("Processing ack_queue of: " + str(ack_queue.qsize()) + "\n")
            pop_cmd = ack_queue.get()
            print(f"\n{str(pop_cmd.command)}: {pop_cmd.cmd_data}")
            if type(pop_cmd) == Command:  #Validate msg is well formed
                #*** Insert code to process ACK messages ***
                if str(pop_cmd.cmd_data[:4]) == "JOIN":
                    print(pop_cmd.cmd_data)
                    playing = True
                pass
            else:
                print("!", end='', flush=True)
            pop_cmd = ""
        if recv_queue.qsize()>0:
            pop_cmd = recv_queue.get()
            #if type(pop_cmd) == Command:  #Validate msg is well formed
            print(f"\n{str(pop_cmd.command)}: {pop_cmd.cmd_data}")
            send_queue.put(Command(pop_cmd.userID, "ACK", "Command " + pop_cmd.command + " received"))
                #*** Additional processing of CMD messages & Gameplay ***
            if pop_cmd.command == "USER":
                user = pop_cmd.cmd_data
                pg.display.set_caption("Client - " + user.name)
                pg.display.update
            elif pop_cmd.command == "ARMIES":
                print(f"{pop_cmd.cmd_data} {pop_cmd.cmd_data.user.userID}")
                # WHAT OBJECT STORES ARMIES TO BE PLACED?
            elif pop_cmd.command == "GAME":
                print(f"{pop_cmd.cmd_data} {pop_cmd.cmd_data.user.userID}")
                # NEED OBJECTS FOR THE GAME
            elif pop_cmd.command == "TURN":
                print(f"{pop_cmd.cmd_data} {pop_cmd.cmd_data.user.userID}")
                # NEED TURN OBJECT
            elif pop_cmd.command == "WORLD":
                print(f"{pop_cmd.cmd_data} {pop_cmd.cmd_data.user.userID}")
                # NEED OBJECT FOR THE WORLD (Collection of Territories and Cards??)
            elif pop_cmd.command == "TERRITORY":
                print(f"{pop_cmd.cmd_data} {pop_cmd.cmd_data.user.userID}")
                # NEED OBJECT FOR A TERRITORY (Collection of Territories and Cards??)



            else:
                print("!", end='', flush=True)
            pop_cmd = ""
        #wrap it up
        # print(str(send_queue.qsize()), end='', flush=True)
        # print(str(ack_queue.qsize()), end='', flush=True)
        # print(str(recv_queue.qsize()), end='', flush=True)
        # print("p\n", end='', flush=True)

        proc_lock.release()

main()
