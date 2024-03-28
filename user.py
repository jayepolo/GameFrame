import uuid

class User:
    def __init__(self):
        self.userID = str(uuid.uuid1())[:8]
        self.name = "Player " + self.userID

