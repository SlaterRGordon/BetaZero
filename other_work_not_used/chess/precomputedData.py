import numpy as np
from .boardRepresentation import BoardRepresentation

class PrecomputedData():
    def __init__(self):
        self.directionOffsets = [8, -8, -1, 1, 7, -7, 9, -9]
        self.pawnAttackDirections = [[4, 6], [7, 5]]
         
        self.pawnAttacksWhite = [[] for i in range(64)]
        self.pawnAttacksBlack = [[] for i in range(64)]
        self.numSquaresToEdge = [[None for i in range(8)] for i in range(64)]
        self.knightMoves = [[] for i in range(64)]
        self.kingMoves = [[] for i in range(64)]

        self.rookMoves = [0 for i in range(64)]
        self.bishopMoves = [0 for i in range(64)]
        self.queenMoves = [0 for i in range(64)]
        
        self.allKnightJumps = [15, 17, -17, -15, 10, -6, 6, -10]
        self.knightAttackBitboards = [0 for i in range(64)]
        self.kingAttackBitboards = [0 for i in range(64)]
        self.pawnAttackBitboards = [[] for i in range(64)]
        
        self.allKnightJumps = [15, 17, -17, -15, 10, -6, 6, -10]
        self.knightAttackBitboards = [0 for i in range(64)]
        self.kingAttackBitboards = [0 for i in range(64)]
        self.pawnAttackBitboards = [[] for i in range(64)]
        
        for square in range(64):
            y = int(square / 8)
            x = int(square - y * 8)

            north = 7 - y
            south = y
            west = x
            east = 7 - x
            self.numSquaresToEdge[square][0] = north
            self.numSquaresToEdge[square][1] = south
            self.numSquaresToEdge[square][2] = west
            self.numSquaresToEdge[square][3] = east
            self.numSquaresToEdge[square][4] = min(north, west)
            self.numSquaresToEdge[square][5] = min(south, east)
            self.numSquaresToEdge[square][6] = min(north, east)
            self.numSquaresToEdge[square][7] = min(south, west)
            
            legalKnightJumps =[]
            knightBitboard = 0
            
            # Calculate all squares knight can jump to from current square
            for knightJumpDelta in self.allKnightJumps:
                knightJumpSquare = int(square + knightJumpDelta)
                if knightJumpSquare >= 0 and knightJumpSquare < 64:
                    knightSquareY = int(knightJumpSquare / 8)
                    knightSquareX = int(knightJumpSquare - knightSquareY * 8)
                    
                    # Ensure knight has moved max of 2 squares on x/y axis (to reject indices that have wrapped around side of board)
                    maxCoordMoveDst = max(abs(x - knightSquareX), abs(y - knightSquareY))
                    if (maxCoordMoveDst == 2):
                        legalKnightJumps.append(knightJumpSquare)
                        knightBitboard |= 1 << knightJumpSquare
                    
            self.knightMoves[square] = legalKnightJumps
            self.knightAttackBitboards[square] = knightBitboard
            
            # Calculate all squares king can move to from current square (not including castling)
            legalKingMoves = []
            for kingMoveDelta in self.directionOffsets:
                kingMoveSquare = square + kingMoveDelta
                if kingMoveSquare >= 0 and kingMoveSquare < 64:
                    kingSquareY = kingMoveSquare / 8
                    kingSquareX = kingMoveSquare - kingSquareY * 8
                    
                    # Ensure king has moved max of 1 square on x/y axis (to reject indices that have wrapped around side of board)
                    maxCoordMoveDst = max(abs(x - kingSquareX), abs(y - kingSquareY))
                    if maxCoordMoveDst == 1:
                        legalKingMoves.append(kingMoveSquare)
                        self.kingAttackBitboards[square] |= 1 << kingMoveSquare
                        
            self.kingMoves[square] = legalKingMoves
            
            # Calculate legal pawn captures for white and black
            pawnCapturesWhite = []
            pawnCapturesBlack = []
            self.pawnAttackBitboards[square] = [0 for i in range(2)]
            if x > 0:
                if y < 7:
                    pawnCapturesWhite.append(square + 7)
                    self.pawnAttackBitboards[square][0] |= 1 << (square + 7)
                if y > 0:
                    pawnCapturesBlack.append(square - 9)
                    self.pawnAttackBitboards[square][1] |= 1 << (square - 9)
            if x < 7:
                if y < 7:
                    pawnCapturesWhite.append(square + 9)
                    self.pawnAttackBitboards[square][0] |= 1 << (square + 9)
                if y > 0:
                    pawnCapturesBlack.append(square - 7)
                    self.pawnAttackBitboards[square][1] |= 1 << (square - 7)
                    
            self.pawnAttacksWhite[square] = pawnCapturesWhite
            self.pawnAttacksBlack[square] = pawnCapturesBlack
            
            # Rook moves
            for directionIndex in range(4):
                currentDirOffset = self.directionOffsets[directionIndex]
                for n in range(int(self.numSquaresToEdge[square][directionIndex])):
                    targetSquare = square + currentDirOffset * (n + 1)
                    self.rookMoves[square] |= 1 << targetSquare
            
            # Bishop moves
            for directionIndex in range(4, 8):
                currentDirOffset = self.directionOffsets[directionIndex]
                for n in range(int(self.numSquaresToEdge[square][directionIndex])):
                    targetSquare = square + currentDirOffset * (n + 1)
                    self.bishopMoves[square] |= 1 << targetSquare
                    
            self.queenMoves[square] = self.rookMoves[square] | self.bishopMoves[square]
            
            self.directionLookup = [None for i in range(127)]
            for i in range(127):
                offset = i - 63
                absOffset = abs(offset)
                absDir = 1
                if (absOffset % 9 == 0):
                    absDir = 9
                elif (absOffset % 8 == 0):
                    absDir = 8
                elif (absOffset % 7 == 0):
                    absDir = 7

                self.directionLookup[i] = absDir * np.sign(offset)
                
            # Distance lookup
            self.orthogonalDistance = [[0 for j in range(64)] for i in range(64)]
            self.kingDistance = [[0 for j in range(64)] for i in range(64)]
            self.centreManhattanDistance = [0 for i in range(64)]

            for squareA in range(64):
                coordA = BoardRepresentation().getCoordinate(squareA)
                fileDstFromCentre = max(3 - coordA.file, coordA.file - 4)
                rankDstFromCentre = max(3 - coordA.rank, coordA.rank - 4)
                self.centreManhattanDistance[squareA] = fileDstFromCentre + rankDstFromCentre
                
                for squareB in range(64):
                    coordB = BoardRepresentation().getCoordinate(squareB)
                    rankDistance = abs(coordA.rank - coordB.rank)
                    fileDistance = abs(coordA.file - coordB.file)
                    self.orthogonalDistance[squareA][squareB] = fileDistance + rankDistance
                    self.kingDistance[squareA][squareB] = max(fileDistance, rankDistance)