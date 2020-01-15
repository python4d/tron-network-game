class Game:
    def __init__(self, id):
        self.p1Went = False
        self.p2Went = False
        self.ready = False
        self.id = id
        self.moves = [None, None]
        self.wins = [0,0]
        self.ties = 0

    def get_player_move(self, p):
        return self.moves[p]

    def set_player_move(self,playerId,trace):
        self.moves[playerId] = trace
        self.wins[playerId] += 1 if trace[3] else 0

    def play(self, playerId, move):
        #self.moves[playerId] = move
        if playerId == 0:
            self.p1Went = True
        else:
            self.p2Went = True

    def connected(self):
        return self.ready

    def bothWent(self):
        return self.p1Went and self.p2Went

    def resetWent(self):
        self.p1Went = False
        self.p2Went = False
        
    def resetMove(self):
        self.moves = [None, None]
        self.resetWent()
        