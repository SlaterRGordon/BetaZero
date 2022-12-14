from .piece import Piece

import numpy as np
import random

class Zobrist():
    def __init__(self):
        self.pieces = [[[0, 0] for j in range(8)] for i in range(64)]
        
        self.castlingRights = np.zeros(16)
        self.enPassantFile = np.zeros(9)
        
        for square in range(64):
            for piece in range(8):
                self.pieces[square][piece][0] = int(random.randrange(2**64))
                self.pieces[square][piece][1] = int(random.randrange(2**64))
                
        for i in range(16):
            self.castlingRights[i] = int(random.randrange(2**64))
          
        for i in range(9):
            self.enPassantFile[i] = int(random.randrange(2**64))
            
        self.sideToMove = int(random.randrange(2**64))
        
    def calculateZobrist(self, board):
        zobristKey = 0
        
        for square in range(64):
            if board.squares[square] != 0:
                type = Piece().type(board.squares[square])
                color = int((Piece().color(board.squares[square]) / 8) - 1)
                zobristKey ^= self.pieces[square][type][color]
        
        epIndex = (board.currentGameState >> 4) & 15
        if (epIndex != -1):
            zobristKey ^= int(self.enPassantFile[epIndex])
            
        if board.colorToMove == 16:
            zobristKey ^= self.sideToMove
            
        zobristKey ^= int(self.castlingRights[board.currentGameState & 0b1111])
        
        return zobristKey
                
                
