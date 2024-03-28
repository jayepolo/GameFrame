import pygame as pg
from network import Network
from game import Command
from network import Network, network_check
from client_threads import send_loop, recv_loop
import threading
import queue
import time

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
    run = True
    clock = pg.time.Clock()
    n = Network()
    user = ""
    send_queue.put(Command("NEW", "USER", "Client join request"))  #Request a formal User object from Server
    print("Queues: " + str(send_queue.qsize())+ str(ack_queue.qsize())+ str(recv_queue.qsize()))

    HBT_time = time.time() + 5
    #print(f"HBT_time = {HBT_time}")

    #Start thread to send and receive Socket messages
    recv_thread = threading.Thread(target=recv_loop, args=(n, send_queue, recv_queue, ack_queue), daemon=True).start() #args=(netconn,), 
    send_thread = threading.Thread(target=send_loop, args=(n, send_queue, recv_queue, ack_queue), daemon=True).start() #args=(netconn,), 

    #Add a small section to get a User state before moving into the while run section
    print("Waiting for User assignment from Server")
    while user != False:
        process_queues
    print(f"Hello {user}")

    print("Starting Client Main() Loop")  #All Client processing happens within this loop
    while run:
        clock.tick(60)
        #game_events()
        process_queues()
        if network_check(user.userID, HBT_time):
            HBT_time = time.time() + 5
        try:
            #game_udate()
            pass
        except:
            run = False
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

def network_check(userID, HBT_time):
    global send_lock
    global send_queue
    print(".", end='', flush=True)
    #print(f"Is {time.time()} >= {HBT_time}??")
    if time.time() >= HBT_time:
        print("H")
        hbt_cmd = Command(userID, "HBT", "Ready to play")
        send_lock.acquire()
        send_queue.put(hbt_cmd)  #Or use the Send Queue to send the command...
        send_lock.release()
        HBT_time = time.time() + 5 #Pause 5 seconds until next heartbeat / This delay is blocking (bad)
        #print(time.time(), HBT_time)
        return True

def process_queues():
        global user
        #Now process recv_queue here
        print("\nP", end='', flush=True)
        proc_lock.acquire()
        if ack_queue.qsize()>0:
            print("Processing ack_queue: " + str(ack_queue.qsize()))
            pop_cmd = ack_queue.get()
            if type(pop_cmd) == Command:  #Validate msg is well formed
                #*** Insert code to process ACK messages ***
                pass
            else:
                print("!", end='', flush=True)
            pop_cmd = ""
        if recv_queue.qsize()>0:
            print("Processing recv_queue: " + str(ack_queue.qsize()))
            pop_cmd = recv_queue.get()
            if type(pop_cmd) == Command:  #Validate msg is well formed
                send_queue.put(Command(pop_cmd.userID, "ACK", "Command " + pop_cmd.command + " received"))
                #*** Additional processing of CMD messages & Gameplay ***
                if pop_cmd.command == "USER":
                    print(f"{pop_cmd.cmd_data} {pop_cmd.cmd_data.user.userID}")
                    user = pop_cmd.cmd_data
                pass
            else:
                print("!", end='', flush=True)
            pop_cmd = ""
        #wrap it up
        print(str(send_queue.qsize()), end='', flush=True)
        print(str(ack_queue.qsize()), end='', flush=True)
        print(str(recv_queue.qsize()), end='', flush=True)
        print("p\n", end='', flush=True)

        proc_lock.release()

main()
