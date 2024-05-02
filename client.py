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
send_lock = threading.Lock()
recv_lock = threading.Lock()
proc_lock = threading.Lock()

def main():
    print(f"Starting GameFrame Client v{version}")
    run = True
    clock = pg.time.Clock()
    
    #Establish Server Socket connection
    n = Network() # Establish connection to Server

    #Start threads to send/receive Socket messages
    recv_thread = threading.Thread(target=recv_loop, args=(n, send_queue, recv_queue), daemon=True).start() #args=(netconn,), 
    send_thread = threading.Thread(target=send_loop, args=(n, send_queue, recv_queue), daemon=True).start() #args=(netconn,), 

    user = User()  #Generic user locally, ot be replaced by Server
    playing = False  #Server has accepted User to play (Needs implementing)
    print(f"Sending JOIN request for userID: {user.userID}")
    send_queue.put(Command(user.userID, "JOIN", user.userID + " join request"))  

    HBT_time = time.time() + 5
    print("Starting main() loop")  #All Client processing happens within this loop
    while run:  #Process certain game activities
        clock.tick(60)
        #game_events()      
        process_queues()        
        HBT_time = network_check(user, HBT_time)

        try:
            #game_udate()
            pass
        except:
            run = False   #TODO Always 'run' but sometimes 'play' but bever bail out completely.
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
        proc_lock.acquire()
        if recv_queue.qsize()>0:
            pop_cmd = recv_queue.get()
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
        proc_lock.release()

main()
