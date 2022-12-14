from .fenUtility import FenUtility
from .pieceList import PieceList
from .piece import Piece
from .zobrist import Zobrist
from .makeMove import MakeMove
from .moveGenerator import MoveGenerator

import numpy as np

class Board():
    fenUtility = FenUtility()
    pieceUtility = Piece()
    zobrist = Zobrist()
    
    def __init__(self):
        self.whiteIndex = 0
        self.blackIndex = 1
        self.squares = np.zeros(64)
        self.kingSquare = np.zeros(2)
        self.history = []
        self.zobristKey = 0
        self.n_moves = 0
        
        self.gameStateHistory = []
        self.currentGameState = None
        
        self.playCount = 0

        knights = [PieceList(10), PieceList(10)]
        pawns = [PieceList(8), PieceList(8)]
        rooks = [PieceList(10), PieceList(10)]
        bishops = [PieceList(10), PieceList(10)]
        queens = [PieceList(9), PieceList(9)]
        empty = PieceList(0)
        
        self.pieceLists = [
            empty,
            empty,
            pawns[self.whiteIndex],
            knights[self.whiteIndex],
            empty,
            bishops[self.whiteIndex],
            rooks[self.whiteIndex],
            queens[self.whiteIndex],
            empty,
            empty,
            pawns[self.blackIndex],
            knights[self.blackIndex],
            empty,
            bishops[self.blackIndex],
            rooks[self.blackIndex],
            queens[self.blackIndex]
        ]
        
        # starting game state
        self.startPosition = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        
        self.whiteToMove = True
        self.colorToMove = 8
        self.opponentColor = 16
        self.colorToMoveIndex = 0
        
    def getPieceList(self, type, color):
        return self.pieceLists[color * 8 + type]
    
    def getPieceTypeSquare(self, square):
        piece = self.squares[square]
        type = Piece().type(piece)
        
        return type
    
    def makeMove(self, move):
        self = MakeMove(move, self).getBoard()

    def loadBoard(self):
        loadedPosition = FenUtility().positionFromFen(fen=self.startPosition)
        
        for index in range(64):
            piece = loadedPosition.squares[index]
            self.squares[index] = piece
            
            if piece != 0:
                type = Piece().type(piece)
                colorIndex = self.whiteIndex if Piece().isColor(piece, 8) else self.blackIndex
                if Piece().isSlidingPiece(piece):
                    if type == Piece().queen or type == Piece().rook or type == Piece().bishop:
                        self.getPieceList(type, colorIndex).addPiece(index)
                elif type == Piece().knight or type == Piece().pawn:
                    self.getPieceList(type, colorIndex).addPiece(index)
                else:
                    self.kingSquare[colorIndex] = int(index)
                
        self.whiteToMove = loadedPosition.whiteToMove
        self.colorToMove = 8 if self.whiteToMove else 16
        self.opponentColor = 16 if self.whiteToMove else 8
        self.colorToMoveIndex = 0 if self.whiteToMove else 1
        
        # Create gamestate
        whiteCastle = 1 << 0 if (loadedPosition.whiteCastleKingside) else 0 | 1 << 1 if (loadedPosition.whiteCastleQueenside) else 0
        blackCastle = 1 << 2 if (loadedPosition.blackCastleKingside) else 0 | 1 << 3 if (loadedPosition.blackCastleQueenside) else 0
        epState = loadedPosition.epFile << 4
        initialGameState = whiteCastle | blackCastle | epState
        self.gameStateHistory.append(initialGameState)
        self.currentGameState = initialGameState
        self.playCount = loadedPosition.playCount

        # Initialize zobrist key
        self.zobristKey = self.zobrist.calculateZobrist(self)
    
    def checkResult(self):
        moveGenerator = MoveGenerator(self)
        moves = moveGenerator.moves
        
        if not moves:
            if moveGenerator.inCheck:
                return 1 if self.colorToMoveIndex == 0 else -1

            return 1
        
        return None
    
    def getPlanesForNeural(self):
        planes = []
        kingBoard = [1 if i==self.kingSquare[0] else 0 for i in range(64)]
        opponentKingBoard = [1 if i==self.kingSquare[1] else 0 for i in range(64)]
        # p1 pieces
        planes.extend(kingBoard)
        planes.extend(1 if i is not None else 0 for i in self.pieceLists[2].board)
        planes.extend(1 if i is not None else 0 for i in self.pieceLists[3].board)
        planes.extend(1 if i is not None else 0 for i in self.pieceLists[5].board)
        planes.extend(1 if i is not None else 0 for i in self.pieceLists[6].board)
        planes.extend(1 if i is not None else 0 for i in self.pieceLists[7].board)
        # p2 pieces
        planes.extend(opponentKingBoard)
        planes.extend(1 if i is not None else 0 for i in self.pieceLists[10].board)
        planes.extend(1 if i is not None else 0 for i in self.pieceLists[11].board)
        planes.extend(1 if i is not None else 0 for i in self.pieceLists[13].board)
        planes.extend(1 if i is not None else 0 for i in self.pieceLists[14].board)
        planes.extend(1 if i is not None else 0 for i in self.pieceLists[15].board)
        
        return planes
        
    def printBoard(self):
        for i in range(0, 64, 8):
            print(self.squares[i: i+8])
        
            