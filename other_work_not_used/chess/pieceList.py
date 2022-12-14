import numpy as np

class PieceList():
    def __init__(self, maxPieces):
        self.occupied = [None for i in range(maxPieces)]
        self.board = [None for i in range(64)]
        self.n_pieces = 0
    
    def addPiece(self, square):
        self.occupied[self.n_pieces] = square
        self.board[square] = self.n_pieces
        self.n_pieces += 1

    def removePiece(self, square):
        index = self.board[square] # get the index occupied
        self.occupied[index] = self.occupied[self.n_pieces - 1] # move last to removed place
        self.board[self.occupied[index]] = index # update board to point to moved new location in occupied
        self.n_pieces -= 1

    def movePiece(self, start, target):
        index = self.board[start] # get the index occupied
        self.occupied[index] = target # move start to target place
        self.board[target] = index # update board to point to target
        
    def printBoard(self):
        for i in range(0, 64, 8):
            print(self.board[i: i+8])