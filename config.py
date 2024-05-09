gameID = "uuid"
world = {}
territory = ""
regions = {}
territories = {}
users = {}
players = {}   #This should include sharable data: name, stats, card qty, etc.
cards = {}
stage = {'Setup', 'Play', 'Victory', 'Draw'}
turn = {}   #Include round, player, phase

send_queues = {}
recv_queue = ""

DEBUG = False
VERBOSE = True
