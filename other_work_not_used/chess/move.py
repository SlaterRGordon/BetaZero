from .piece import Piece
from .boardRepresentation import BoardRepresentation

import numpy as np

class Flag():
    def __init__(self):
        self.none = 0
        self.enPassantCapture = 1
        self.castling = 2
        self.promoteToQueen = 3
        self.promoteToKnight = 4
        self.promoteToRook = 5
        self.promoteToBishop = 6
        self.pawnTwoForward = 7

class Move(Flag):
    def __init__(self):
        self.startSquareMask = 0b0000000000111111
        self.targetSquareMask = 0b0000111111000000
        self.flag = 0b1111000000000000
        self.moveValue = 0
    
    def move(self, moveValue):
        self.moveValue = np.ushort(int(moveValue))
        return self
        
    def moveSquare(self, startSquare, targetSquare):
        self.moveValue = np.ushort(int(startSquare) | int(targetSquare) << 6)
        return self
    
    def moveFlag(self, startSquare, targetSquare, flag):
        self.moveValue = np.ushort(int(startSquare) | int(targetSquare) << 6 | int(flag) << 12)
        return self

    def moveFlagValue(self):
        return self.moveValue >> 12
        
    def getStartSquare(self):
        return self.moveValue & self.startSquareMask
    
    def getTargetSquare(self):
        return (self.moveValue & self.targetSquareMask) >> 6
    
    def pawnMoveIndex(self, start, end, colorIndex):
        if(end - start == 8): # N 1 square
            return 0
        elif(end - start == 16): # N 2 square
            return 1
        elif(end - start == -8): # S 1 square
            return 7*4
        elif(end - start == -16): # S 2 square
            return 7*4 + 1
        elif(end - start % 7 == 0): # NE, SW
            if (end - start)*colorIndex > 0:
                return 1*7
            else:
                return 5*7
        elif(end - start % 9 == 0): # NE, SW
            if (end - start)*colorIndex > 0:
                return 7*7
            else:
                return 3*7
    
    def knightMoveIndex(self, start, end, colorIndex):
        if(end - start == 15*colorIndex):
            return 0
        elif(end - start == 17*colorIndex):
            return 1
        elif(end - start == -15*colorIndex):
            return 2
        elif(end - start == -17*colorIndex):
            return 3
        elif(end - start == 10*colorIndex):
            return 4
        elif(end - start == 6*colorIndex):  
            return 5
        elif(end - start == -10*colorIndex):
            return 6
        elif(end - start == -6*colorIndex):  
            return 7
        
    def bishopMoveIndex(self, start, end, colorIndex):
        if (end - start) % 7 == 0: # NE, SW
            numberSquares = int((end - start) / 7) - 1
            if numberSquares*colorIndex > 0:
                return 1*7 + abs(numberSquares)
            else:
                return 5*7 + abs(numberSquares)
        elif (end - start) % 9 == 0: # NW, SE
            numberSquares = int((end - start) / 9) - 1
            if numberSquares*colorIndex > 0:
                return 7*7 + abs(numberSquares)
            else:
                return 3*7 + abs(numberSquares)
    
        return None
            
    def rookMoveIndex(self, start, end, colorIndex):
        if (end - start) % 8 == 0: # N, S
            numberSquares = int((end - start) / 8) - 1
            if numberSquares*colorIndex > 0:
                return abs(numberSquares)
            else:
                return 4*7 + abs(numberSquares)
        elif np.floor((end - start) / 8) == 0: # E, W
            numberSquares = end - start
            if numberSquares*colorIndex > 0:
                return 2*7 + abs(numberSquares)
            else:
                return 6*7 + abs(numberSquares)
            
    def queenMoveIndex(self, start, end, colorIndex):
        index = self.bishopMoveIndex(start, end, colorIndex)
        if index is None:
            index = self.rookMoveIndex(start, end, colorIndex)
        
        return index
    
    def getNewSquare(self, start, planeIndex):
        if planeIndex < 56:
            direction = np.floor(planeIndex / 7)
            numberSquares = (planeIndex % 7) + 1
            
            if direction == 0:
                return start + (numberSquares * 8)
            elif direction == 1:
                return start + (numberSquares * 7)
            elif direction == 2:
                return start + numberSquares
            elif direction == 3:
                return start - (numberSquares * 9)
            if direction == 4:
                return start - (numberSquares * 8)
            elif direction == 5:
                return start - (numberSquares * 7)
            elif direction == 6:
                return start - numberSquares
            elif direction == 7:
                return start + (numberSquares * 9)
        elif planeIndex < 64:
            direction = planeIndex - 55
            if direction == 0:
                return start + 15
            elif direction == 1:
                return start + 17
            elif direction == 2:
                return start - 15
            elif direction == 3:
                return start - 17
            if direction == 4:
                return start + 11
            elif direction == 5:
                return start + 9
            elif direction == 6:
                return start - 11
            elif direction == 7:
                return start - 9
    
    def isPromotion(self):
        flag = self.moveValue >> 12
        
        return flag == Flag().promoteToQueen or flag == Flag().promoteToRook or flag == Flag().promoteToKnight or flag == Flag().promoteToBishop
    
    def getPromotionPieceType(self):
        flag = self.moveValue >> 12
        
        if flag == Flag().promoteToQueen:
            return Piece().queen
        elif flag == Flag().promoteToKnight:
            return Piece().knight
        elif flag == Flag().promoteToRook:
            return Piece().rook
        elif flag == Flag().promoteToBishop:
            return Piece().bishop
        else:
            return Piece().none
        
    def isSameMove(self, a, b):
        return a.moveValue == b.moveValue
    
    def isInvalidMove(self, move):
        return move.moveValue == 0
    
    def getValue(self, move):
        return move.moveValue
    
    def getName(self):
        return BoardRepresentation().squareName(self.getStartSquare()) + "-" + BoardRepresentation().squareName(self.getTargetSquare())